"""HF-resolved burst diagnostic and timestep negative control.
A coarse audio timestep can numerically suppress an ultrasonic oscillation.
"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from fixture import ROOT,WHOLE,fingerprint
from feedback_model import build
sys.path.insert(0,str(WHOLE/'tools'))
import spice_runtime as sp
OUT=ROOT/'results'

def main():
    source=fingerprint();paths=[Path(__file__),ROOT/'tools/feedback_model.py',ROOT/'tools/transformer_model.py',ROOT/'tools/fixture.py',WHOLE/'tools/spice_runtime.py'];factory={str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};rows=[]
    for label,cap,step in [('lead47-fine',47e-12,1/6.4e6),('lead220-coarse',220e-12,1/96000),('lead220-fine',220e-12,1/6.4e6),('lead220-refined',220e-12,1/12.8e6)]:
        p=dict(leakage_H=.08,presence=0,feedback_cap_F=cap)
        text=build(p)
        text='\n'.join('BRING RET_DRIVE 0 V=.01*sin(2*pi*50000*time)*(time>0.001)*(time<0.0011)' if x.startswith('VTEST ') else x for x in text.splitlines())+'\n'
        name='feedback-ring-'+label;(OUT/f'{name}.cir').write_text(text);sp.load(text);sp.cmd('op');sp.cmd('save v(speaker)');sp.cmd(f'tran {step} .01 0 {step}')
        t=np.array(sp.vector('time'));v=np.array(sp.vector('v(speaker)'));assert t[-1]>=.01*(1-1e-8) and np.isfinite(v).all()
        peak=lambda a,b:float(np.max(abs(v[(t>=a)&(t<=b)])))
        grid=np.linspace(.0095,.01,2001)
        rows.append(dict(name=name,parameters=p,end_s=float(t[-1]),max_step_s=step,burst_peak_V=peak(.001,.0012),early_tail_peak_V=peak(.002,.003),late_tail_peak_V=peak(.009,.01),deck_sha256=hashlib.sha256(text.encode()).hexdigest(),waveform=dict(time_s=grid.tolist(),speaker_V=np.interp(grid,t,v).tolist())))
        sp.cmd('destroy all');print(name,rows[-1]['late_tail_peak_V'],flush=True)
    assert source==fingerprint() and factory=={str(p.relative_to(WHOLE.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    result=dict(scope='10ms local HF burst; not startup/thermal/full-supply qualification',source_hashes=source,factory_hashes=factory,cases=rows,physical_qualified=False)
    (OUT/'feedback-ringdown.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');(OUT/'feedback-ringdown.log').write_text('\n'.join(sp.logs)+'\n')
if __name__=='__main__':main()
