"""Bounded amplitude/ring-down diagnostics on the explicit transformer fixture.
Retains completion/failure, provenance and selected waveform windows; no CAD writes.
"""
import hashlib,json,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from fixture import ROOT,WHOLE,fingerprint
from feedback_model import build
from run import stats,NODES
sys.path.insert(0,str(WHOLE/'tools'))
import spice_runtime as sp
OUT=ROOT/'results'

def hashes():
    return {str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [Path(__file__),ROOT/'tools/feedback_model.py',ROOT/'tools/transformer_model.py',ROOT/'tools/fixture.py',ROOT/'tools/run.py',WHOLE/'tools/spice_runtime.py']}

def worker(name,p,c):
    source=fingerprint();factory=hashes();text=build(p,**c);(OUT/f'{name}.cir').write_text(text)
    sp.cmd('version');version=list(sp.logs);sp.load(text);sp.cmd('op')
    sp.cmd('save '+' '.join('v('+n.lower()+')' for n in NODES))
    f=c['freq'];step=min(20e-6,1/(96*f));end=.5
    sp.cmd(f'tran {step} {end} 0 {step}');t=np.array(sp.vector('time'));assert len(t) and t[-1]>=end*(1-1e-8)
    vals={n:np.array(sp.vector('v('+n.lower()+')')) for n in NODES};assert all(np.isfinite(v).all() for v in vals.values())
    sig={n:stats(t,v,f,end) for n,v in vals.items()}
    active=(t>.15)&(t<.19);tail=t>.4
    metrics={n:dict(active_window_peak_V=float(np.max(abs(v[active]))),tail_peak_V=float(np.max(abs(v[tail])))) for n,v in vals.items() if n in ('SPEAKER','FX_SEND','MIX_OUT')}
    ts=np.linspace(.4995,.5,1001)
    waves=dict(time_s=ts.tolist(),**{n:np.interp(ts,t,vals[n]).tolist() for n in ['SPEAKER','MIX_OUT','EL34_GA','EL34_GB']})
    row=dict(status='completed',parameters=p,config=c,end_s=float(t[-1]),max_step_s=step,signals=sig,windows=metrics,waveform=waves,
             source_hashes=source,factory_hashes=factory,deck_sha256=hashlib.sha256(text.encode()).hexdigest(),simulator_version_log=version,physical_qualified=False)
    assert source==fingerprint() and factory==hashes(),'Inputs changed during worker'
    (OUT/f'{name}.json').write_text(json.dumps(row,indent=2,allow_nan=False)+'\n')

def bounded(case):
    name,p,c=case;start=time.monotonic();limit=600
    try:
        r=subprocess.run([sys.executable,__file__,'--worker',name,json.dumps(p),json.dumps(c)],capture_output=True,text=True,timeout=limit)
        row=json.loads((OUT/f'{name}.json').read_text()) if r.returncode==0 else dict(status='failed',error=r.stderr[-2500:])
    except subprocess.TimeoutExpired:row=dict(status='timeout',error='600 s wall limit; full transient not completed')
    row.update(name=name,parameters=p,config=c,elapsed_s=time.monotonic()-start,wall_time_limit_s=limit)
    (OUT/f'{name}.json').write_text(json.dumps(row,indent=2,allow_nan=False)+'\n')
    print(name,row['status'],flush=True)
    return {k:v for k,v in row.items() if k!='waveform'}

def main():
    config=dict(channel='clean',mode='native',freq=20000,amp=.00672,supply=278,volume=1,tone=.5,gain=.5,guard_pentode_power=True)
    legacy=dict(legacy_transformer=dict(half_primary_H=40,coupling=.995))
    cases=[('feedback-tran-legacy-small',legacy,dict(config,amp=.0001)),
           ('feedback-tran-independent-small',{},dict(config,amp=.0001)),
           ('feedback-tran-independent-full',{},config),
           ('feedback-tran-lead47-burst',dict(leakage_H=.08,presence=0,feedback_cap_F=47e-12),dict(config,freq=1000,amp=.001,burst=True)),
           ('feedback-tran-lead220-negative-control',dict(leakage_H=.08,presence=0,feedback_cap_F=220e-12),dict(config,freq=1000,amp=.001,burst=True))]
    with ThreadPoolExecutor(max_workers=2) as pool: rows=list(pool.map(bounded,cases))
    result=dict(scope='Amplitude/ring-down diagnosis, including deliberately poor compensation negative control; no native adoption',cases=rows,physical_qualified=False,fabrication_ready=False)
    (OUT/'feedback-transient-summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':
    if '--worker' in sys.argv:
        try:worker(sys.argv[2],json.loads(sys.argv[3]),json.loads(sys.argv[4]))
        finally:(OUT/f'{sys.argv[2]}.log').write_text('\n'.join(sp.logs)+'\n')
    else:main()
