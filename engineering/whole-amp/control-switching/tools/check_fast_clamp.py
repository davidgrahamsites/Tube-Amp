"""Independent coil integration, SPICE clamp sensitivity, evidence/native guards."""
import copy,json,math,sys,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];DEST=BASE/'results/fast-clamp'
sys.path.insert(0,str(BASE.parent/'tools'))
import spice_runtime as sp

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(s,b):
    assert s['qualified'] is False and s['native_adopted'] is False and s['contact_release_verified'] is False
    assert b['qualified'] is False and b['native_adopted'] is False
    assert len(s['cases'])==24 and len(b['cases'])==32 and len({r['id'] for r in b['cases']})==32
    for p,h in s['inputs'].items():assert sha(BASE/p)==h,p
    for p,h in b['inputs'].items():assert sha(BASE.parent/p)==h,p
    for p,h in s['native_sha256'].items():assert sha(BASE.parent/p)==h,p
    latency=b['detector']['detection_propagation_allocation_s']+b['detector']['relay_five_percent_current_screen_s']+b['detector']['additional_contact_and_logic_allocation_s']
    assert abs(b['detector']['relay_five_percent_current_screen_s']-max(r['decay_to_5percent_s'] for r in s['cases']))<1e-12
    for row in b['cases']:
        assert row['id'] in b['decks']
        for tr in row['raw_warning_traces']:
            at=tr['qualified_pulse_start_relative_s'];assert at is not None
            assert abs(min(row['raw_floor_relative_s'].values())-at-latency-tr['conditional_raw_mute_reserve_s'])<1e-10
    assert b['summary']['refinement_delta_s']<1e-4

def integrate(row):
    # Independent time stepping: no log/exponential decay formula.
    dt=1e-7;i=row['initial_A'];time=0;charge=0;cross=None
    while i>1e-10 and time<.2:
        reverse=max(0,row['cold_drain_min_V']-row['supply_V']) if i>.001 else 0
        def f(x):return -(row['resistance_ohm']*x+reverse)/row['inductance_H']
        k1=f(i);k2=f(i+dt*k1/2);k3=f(i+dt*k2/2);k4=f(i+dt*k3)
        new=max(0,i+dt*(k1+2*k2+2*k3+k4)/6)
        if cross is None and new<=row['target_A']:cross=time+dt*(i-row['target_A'])/(i-new)
        charge+=(i+new)*dt/2;i=new;time+=dt
    assert cross is not None and i<=1e-10
    assert abs(cross-row['decay_to_5percent_s'])<2e-6
    assert abs(charge-row['conservative_integrated_charge_C'])<2e-9
    return {'coil_C':row['coil_C'],'time_error_s':abs(cross-row['decay_to_5percent_s']),'charge_error_C':abs(charge-row['conservative_integrated_charge_C'])}

def simulate(row,step,old_diode=False):
    # Quasistatic TVS knee and dynamic resistance; ideal driver switch.
    # This cross-check cannot prove actual MOS turnoff overshoot or contact timing.
    knee=row['cold_drain_min_V']-.276*.001
    deck=f'''K3 candidate clamp sensitivity; ideal driver, quasistatic cold TVS
V12 supply 0 {row['supply_V']}
Vgate gate 0 PWL(0 1 .01 1 .0100001 0 .04 0)
Sdriver drain 0 gate 0 SW
.model SW SW(Ron=.01 Roff=1e10 Vt=.5 Vh=.01)
Rcoil supply coil {row['resistance_ohm']}
Lcoil coil remote {row['inductance_H']}
Rwire remote wire .2
Lwire wire drain 100u
Cdrain drain 0 100p
BTVS drain 0 I=max(v(drain)-{knee},0)/.276
{'BOLD drain supply I=max(v(drain)-v(supply)-.5,0)/.2' if old_diode else '* Both old ordinary diode paths absent'}
.options method=gear maxord=2 reltol=1e-6 abstol=1e-12 vntol=1e-8
.save i(lcoil) v(drain)
.tran {step} .04 0 {step}
.end
'''
    sp.cmd('destroy all');sp.logs.clear();sp.load(deck);sp.cmd('run');t=sp.vector('time');i=sp.vector('i(lcoil)');v=sp.vector('v(drain)')
    assert abs(t[-1]-.04)<1e-9 and all(math.isfinite(x) for a in [t,i,v] for x in a)
    j=next(k for k in range(1,len(t)) if t[k]>.01 and i[k]<=i[0]*.05)
    crossing=t[j-1]+(t[j]-t[j-1])*(i[j-1]-.05*i[0])/(i[j-1]-i[j])-.01
    return {'step_s':step,'ordinary_diode_left_in_parallel':old_diode,'decay_to_5percent_s':crossing,'model_peak_drain_V':max(v),'deck':deck,'log':'\n'.join(sp.logs)}

def main():
    s=json.loads((DEST/'screen.json').read_text());b=json.loads((DEST/'brownout.json').read_text());validate(s,b)
    numeric=[integrate(row) for row in s['cases']]
    samples=[min(s['cases'],key=lambda r:r['decay_to_5percent_s']),max(s['cases'],key=lambda r:r['decay_to_5percent_s'])]
    sims=[]
    for row in samples:
        coarse=simulate(row,2e-6);fine=simulate(row,1e-6)
        assert coarse['decay_to_5percent_s']<=row['decay_to_5percent_s']+1e-6
        delta=abs(coarse['decay_to_5percent_s']-fine['decay_to_5percent_s']);assert delta<1e-5
        sims.append({'analytical':row,'coarse':coarse,'fine':fine,'refinement_delta_s':delta})
    old=simulate(samples[1],2e-6,True);assert old['decay_to_5percent_s']>s['summary']['maximum_coil_decay_s']+.005
    rejects=[]
    for label,change in [('false qualification',lambda d:d.update(qualified=True)),('missing case',lambda d:d['cases'].pop()),('altered input hash',lambda d:d['inputs'].__setitem__(next(iter(d['inputs'])),'0'*64))]:
        test=copy.deepcopy(b);change(test)
        try:validate(s,test)
        except AssertionError:rejects.append(label)
        else:raise AssertionError(label)
    source=json.loads((DEST/'source-observations.json').read_text())
    assert sha(DEST/source['manufacturer']['retained_document'])==source['manufacturer']['sha256']
    # Preserve earlier failed comparison as evidence, rather than replacing it with today's success.
    previous=json.loads((BASE/'results/brownout-timing/raw-warning.json').read_text());assert sum(r['healthy_enable_margin_V']<0 for r in previous['cases'])==8
    receipt={'evidence_checks_passed':True,'qualified':False,'native_adopted':False,'contact_release_verified':False,'conditional_brownout_cases_pass':all(r['healthy_enable_margin_V']>0 and all(t['conditional_raw_mute_reserve_s']>0 for t in r['raw_warning_traces']) for r in b['cases']),'native_preserved_count':len(s['native_sha256']),'numerical_integration':numeric,'spice_cross_checks':sims,'parallel_diode_negative_control':old,'negative_controls_rejected':rejects,'source_hash_verified':True,'old_failure_preserved':True,'inputs':{str(p.relative_to(BASE)):sha(p) for p in [Path(__file__),DEST/'screen.json',DEST/'brownout.json',DEST/'source-observations.json']}}
    (DEST/'checks.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['inputs','numerical_integration','spice_cross_checks','parallel_diode_negative_control']},indent=2));print('Maximum numerical time error',max(r['time_error_s'] for r in numeric));print('Parallel diode time',old['decay_to_5percent_s'])
if __name__=='__main__':main()
