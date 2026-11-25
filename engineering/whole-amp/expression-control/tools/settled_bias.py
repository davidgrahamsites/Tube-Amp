"""Resolve steady DC with retained physical circuit and explicit settling evidence.

This is a powered-circuit initialization method, not a power-on simulation.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
import bias_screen as bias
ota=bias.ota

def deck(case):
    s=bias.deck(case)
    return '\n'.join('VIN in 0 DC 0' if line.startswith('VIN ') else line for line in s.splitlines())+'\n'

def measure(case):
    import numpy as np
    sys.path.insert(0,str(ota.ROOT/'engineering/whole-amp/tools'));import spice_runtime as sp
    step=case.get('step',1e-4);stop=case.get('stop',2.)
    warm_step=case.get('warm_step',1e-6);warm_stop=case.get('warm_stop',.002)
    sp.load(deck(case));sp.cmd(f'optran 0 0 0 {warm_step:g} {warm_stop:g} 0')
    sp.cmd('save all @cin[i] @cbi[i] @cf[i] @qbi[ic] @qbi[ie] @qdm[ic]')
    sp.cmd(f'tran {step:g} {stop:g} 0 {step:g}')
    try:
        t=np.array(sp.vector('time'))
        if not len(t) or t[-1]<stop*(1-1e-8):raise ValueError('incomplete duration')
        names=['out','bo','be','bbas','abc','ref','target','plus','minus','db','acin']
        v={n:np.array(sp.vector('v('+n+')')) for n in names}
        if not all(np.isfinite(a).all() for a in v.values()):raise ValueError('non-finite waveform')
        late=t>=stop-.2
        final={n:float(a[-1]) for n,a in v.items()}
        ranges={n:float(np.ptp(a[late])) for n,a in v.items()}
        caps={n:np.array(sp.vector('@'+n+'[i]')) for n in ['cin','cbi','cf']}
        cap_max={n:float(np.max(abs(a[late]))) for n,a in caps.items()}
        ie=np.array(sp.vector('@qbi[ie]'));ic=np.array(sp.vector('@qbi[ic]'))
        # Sign convention: positive ie enters the PNP emitter.
        residual=(v['ref']-v['be'])/10000+(v['bo']-v['be'])/100000+caps['cbi']-ie-v['be']/case.get('rshunt',1e12)
        rail=case.get('rail',15)
        valid=all(-rail<final[n]<rail for n in ['out','bo'])
        stationary=max(ranges.values())<1e-5 and max(cap_max.values())<1e-9
        result=dict(status='settled' if valid and stationary else 'unsettled',end_s=float(t[-1]),final=final,
            late_window_s=.2,late_peak_to_peak_V=ranges,late_capacitor_max_abs_A=cap_max,
            late_emitter_kcl_max_abs_A=float(max(abs(residual[late]))),
            collector_current_A=float(ic[-1]),diode_bias_current_A=float(-sp.vector('@qdm[ic]')[-1]),
            post_initialization_reverse_BE_max_V=float(max(v['bbas']-v['be'])),
            commands=[f'optran 0 0 0 {warm_step:g} {warm_stop:g} 0',f'tran {step:g} {stop:g} 0 {step:g}'])
    except (AssertionError,IndexError,ValueError) as e:result=dict(status='failed',error=str(e)[-1000:])
    return dict(result,log='\n'.join(sp.logs))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,case):
    dp=ota.OUT/('settled-'+name+'.cir');dp.write_text(deck(case));lp=dp.with_suffix('.log')
    try:
        p=subprocess.run([sys.executable,__file__,'--case',json.dumps(case)],capture_output=True,text=True,timeout=35)
        r=json.loads(p.stdout) if p.returncode==0 else dict(status='failed',error=p.stderr[-2000:])
        log=r.pop('log','')+'\n'+p.stderr
    except subprocess.TimeoutExpired as e:r=dict(status='timeout',seconds=35);log=str(e.stderr or '')
    lp.write_text(log);print(name,r['status'],r.get('final',{}).get('out'),flush=True)
    return dict(name=name,case=case,deck=dp.name,deck_sha256=sha(dp),log=lp.name,log_sha256=sha(lp),**r)

def main():
    trim=json.loads((ota.OUT/'trim-screen.json').read_text())['calibrated_fractions']['150000']
    base=dict(trim_fraction=trim,trim_resistance=150000)
    rows=[]
    for rail in [12,15,16.5]:
        for target in [0,2.5,4.9,5]:rows.append(run(f'{rail}-{target}',dict(base,rail=rail,target=target)))
    for label,changes in [('half-step',dict(step=5e-5)),('longer',dict(stop=3)),('warm-half',dict(warm_step=5e-7)),('warm-double',dict(warm_step=2e-6)),('weak-shunt',dict(rshunt=1e13))]:
        for target in [0,5]:rows.append(run(label+'-'+str(target),dict(base,target=target,**changes)))
    for temp in [0,70]:rows.append(run('temp-'+str(temp),dict(base,target=5,temperature=temp)))
    inputs=[Path(__file__),Path(bias.__file__),Path(ota.__file__),ota.OTA,ota.OP,bias.BJT,ota.OUT/'trim-screen.json',ota.ROOT/'engineering/whole-amp/tools/spice_runtime.py']
    report=dict(scope='Steady DC of the existing 150k trim candidate using transient initialization. Not cold-start, pedal/protection, tolerance, noise, or native qualification.',cases=rows,provenance={str(p.relative_to(ota.ROOT)):sha(p) for p in inputs})
    (ota.OUT/'settled-bias.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':
    if len(sys.argv)>1:print(json.dumps(measure(json.loads(sys.argv[2]))))
    else:main()
