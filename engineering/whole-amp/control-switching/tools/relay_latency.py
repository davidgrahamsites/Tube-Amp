"""Coil energy diagnostic with immediate driver inhibition; no contact-motion model."""
import hashlib
import itertools
import json
import math
import subprocess
from pathlib import Path
import sys

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE.parent/'tools'))


def remaining(initial, resistance, inductance, clamp, time):
    return max(0.0,(initial+clamp/resistance)*math.exp(-resistance*time/inductance)-clamp/resistance)


def decay_time(initial, resistance, inductance, clamp, fraction):
    return inductance/resistance*math.log((initial+clamp/resistance)/(initial*fraction+clamp/resistance))


def spice_case(case, duration, step, gate_resistance=100, restore=False):
    import spice_runtime as sp
    start=.01
    end=start+duration+.02
    deck=f'''K3 coil diagnostic: immediate gate command, MOS/diode surrogates, no moving contacts
V12 supply 0 {case['supply_V']}
Vcommand gate 0 PWL(0 3.84 {start} 3.84 {start+1e-7} 0 {start+duration} 0 {start+duration+1e-7} 3.84 {end} 3.84)
Mdriver drain gate 0 0 FET
.model FET NMOS(Level=1 Vto=1.45 Kp=6.6137566 Lambda=0 Rd=.005 Rs=.005)
Cds drain 0 25p
Cgd gate drain 50p
Dbody 0 drain DGEN
Rcoil supply coil {case['resistance_ohm']}
Lcoil coil remote {case['inductance_H']}
Rwire remote wire .2
Lwire wire drain 100u
Dremote remote supply DGEN
Dlocal drain supply DGEN
.model DGEN D(Is=1n N=1.8 Rs=.2 Cjo=15p Tt=2u)
.options method=gear maxord=2 reltol=1e-5 abstol=1e-11 vntol=1e-8
.save i(lcoil) v(drain) v(remote)
.tran {step} {end} 0 {step}
.end
'''
    if gate_resistance:
        deck=deck.replace('Vcommand gate 0','Vcommand command 0')
        deck=deck.replace('Mdriver drain',f'Rgate command gate {gate_resistance}\nCgs gate 0 580p\nMdriver drain')
    if not restore:
        deck=deck.replace(f'{start+duration} 0 {start+duration+1e-7} 3.84 {end} 3.84',f'{end} 0')
    sp.cmd('destroy all');sp.load(deck);sp.cmd('run')
    t=sp.vector('time');current=sp.vector('i(lcoil)');drain=sp.vector('v(drain)');remote=sp.vector('v(remote)')
    if t[-1]<end-1e-9:
        return dict(status='failed-incomplete-duration',case=case,pulse_s=duration,step_s=step,completed_s=t[-1],required_s=end,gate_source_screen_ohm=gate_resistance,deck=deck,deck_sha256=hashlib.sha256(deck.encode()).hexdigest())
    assert all(math.isfinite(x) for values in [t,current,drain,remote] for x in values)
    initial=current[0]
    indices=[i for i,x in enumerate(t) if start+1e-7<x<=start+duration]
    minimum=min(current[i] for i in indices)
    crossing=next((t[i]-start for i in indices if current[i]<=initial*.05),None)
    diode_active=[i for i in indices if current[i]>initial*.05 and remote[i]>case['supply_V']]
    samples={}
    for sample in [.0001,.0005,.001,.002,.005,.02]:
        j=next(i for i,x in enumerate(t) if x>=start+sample)
        a=(start+sample-t[j-1])/(t[j]-t[j-1])
        samples[str(sample)]=(current[j-1]+a*(current[j]-current[j-1]))/initial
    return dict(status='complete-diagnostic',case=case,pulse_s=duration,restore=restore,current_fraction_at_off_time=samples,initial_current_A=initial,minimum_current_fraction=minimum/initial,
                current_below_5percent_during_observation_s=crossing,max_drain_V=max(drain),
                active_remote_clamp_range_V=[min(remote[i]-case['supply_V'] for i in diode_active),max(remote[i]-case['supply_V'] for i in diode_active)],
                completed_s=t[-1],step_s=step,gate_source_screen_ohm=gate_resistance,deck=deck,deck_sha256=hashlib.sha256(deck.encode()).hexdigest())


def bounded_case(case, duration, step, gate_resistance=100, restore=False):
    try:
        p=subprocess.run([sys.executable,__file__,'--case',json.dumps([case,duration,step,gate_resistance,restore])],capture_output=True,text=True,timeout=30)
    except subprocess.TimeoutExpired:
        return dict(status='timeout',case=case,pulse_s=duration,step_s=step,timeout_s=30)
    if p.returncode:
        raise RuntimeError(p.stderr[-2000:])
    return json.loads(p.stdout)


def main():
    cpath=BASE/'relay-latency-contract.json';c=json.loads(cpath.read_text())
    assert c['gate_transition_s']==1e-7, 'Update the waveform factory for changed transition time'
    coilpath=BASE/c['coil_contract'];coil=json.loads(coilpath.read_text())['coil']
    rows=[]
    for temp,tol,L,V,clamp in itertools.product(c['temperatures_C'],[-coil['resistance_tolerance'],coil['resistance_tolerance']],coil['inductance_reference_H'],coil['voltage_V'],c['diode_drop_screen_V']):
        R=coil['resistance_23C_ohm']*(1+tol)*(1+coil['copper_tcr_screen_per_C']*(temp-23))
        initial=V/R
        rows.append(dict(temperature_C=temp,resistance_ohm=R,inductance_H=L,supply_V=V,clamp_V=clamp,
                         decay_to_5percent_s=decay_time(initial,R,L,clamp,c['residual_current_fraction_screen']),
                         remaining_fraction={str(t):remaining(initial,R,L,clamp,t)/initial for t in c['fault_pulse_s']}))
    samples=[min(rows,key=lambda r:r['decay_to_5percent_s']),max(rows,key=lambda r:r['decay_to_5percent_s'])]
    runs=[]
    refinements=[]
    for case in samples:
        result=bounded_case(case,c['spice_off_observation_s'],c['spice_step_s'],c['gate_source_screen_ohm']);runs.append(result)
        finer=bounded_case(case,c['spice_off_observation_s'],c['spice_step_s']/4,c['gate_source_screen_ohm'])
        refinement=dict(coarse_step_s=c['spice_step_s'],fine=finer,matched_complete=False)
        if result['status']==finer['status']=='complete-diagnostic':
            refinement.update(matched_complete=True,maximum_sample_fraction_delta=max(abs(v-finer['current_fraction_at_off_time'][k]) for k,v in result['current_fraction_at_off_time'].items()),peak_drain_delta_V=abs(result['max_drain_V']-finer['max_drain_V']))
        refinements.append(refinement)
        print('coil',case['temperature_C'],result['status'],'refinement',finer['status'],flush=True)
    ideal_source_diagnostic=bounded_case(samples[0],.005,c['spice_step_s'],0,True)
    restore_runs=[bounded_case(case,pulse,c['spice_step_s'],c['gate_source_screen_ohm'],True)
                  for case in samples for pulse in [.0001,.001,.005,.02]]
    restore_target=max((r for r in restore_runs if r['status']=='complete-diagnostic'),key=lambda r:r['max_drain_V'])
    restore_refinement=bounded_case(restore_target['case'],restore_target['pulse_s'],c['spice_step_s']/4,c['gate_source_screen_ohm'],True)
    checks=[dict(name='primary and refined off-decay simulations complete',passed=all(x['matched_complete'] for x in refinements)),
            dict(name='sampled current fractions agree within0.001',passed=all(x.get('maximum_sample_fraction_delta',math.inf)<.001 for x in refinements)),
            dict(name='analytical current remains in physical bounds and decays with off-time',passed=all(all(0<=v<=1 for v in r['remaining_fraction'].values()) and list(r['remaining_fraction'].values())==sorted(r['remaining_fraction'].values(),reverse=True) for r in rows))]
    report=dict(scope=c['job'],qualified=False,analytical_cases=len(rows),checks=checks,
                conditional_decay_to_5percent_range_s=[min(r['decay_to_5percent_s'] for r in rows),max(r['decay_to_5percent_s'] for r in rows)],
                pulse_current_ranges={str(t):[min(r['remaining_fraction'][str(t)] for r in rows),max(r['remaining_fraction'][str(t)] for r in rows)] for t in c['fault_pulse_s']},
                analytical_witnesses=samples,spice_cases=runs,refinements=refinements,ideal_gate_source_diagnostic=ideal_source_diagnostic,
                restore_diagnostics=restore_runs,restore_refinement=restore_refinement,
                contact_release_verified=False,limitations=c['limitations'],
                provenance={str(p.relative_to(BASE.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [cpath,coilpath,BASE/c['relay_datasheet'],Path(__file__),BASE.parent/'tools/spice_runtime.py']})
    (BASE/'results/relay-latency.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['analytical_cases','conditional_decay_to_5percent_range_s','pulse_current_ranges']},indent=2))


if __name__=='__main__':
    if len(sys.argv)>1:
        args=json.loads(sys.argv[2])
        try: result=spice_case(*args)
        except (AssertionError,ValueError,IndexError) as error:
            result=dict(status='failed',case=args[0],pulse_s=args[1],step_s=args[2],error=repr(error))
        import spice_runtime as sp
        result['log']='\n'.join(sp.logs)
        print(json.dumps(result))
    else:main()
