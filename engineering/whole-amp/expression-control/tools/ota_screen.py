"""Bounded isolated wet VCA comparison; no native writes or model edits."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MODULE = Path(__file__).resolve().parents[1]
OUT = MODULE / 'results'
OTA = MODULE / 'models/LM13700.MOD'
OP = ROOT / 'engineering/solid-state-reverb/simulation/models/OPAx134.LIB'


def deck(case):
    """Ideal current bias isolates the audio cell; trim is a physical divider."""
    fraction=case.get('trim_fraction',.5)
    assert 0<=fraction<=1
    return f'''Isolated expression OTA candidate, not released hardware
.include "{OTA}"
.include "{OP}"
.options rshunt={case.get('rshunt',1e12)}
.temp {case.get('temperature',27)}
VP vp 0 {case.get('rail',15)}
VN vn 0 {-case.get('rail',15)}
VIN in 0 DC 0 AC 1 SIN(0 {case.get('amplitude',1)} {case.get('hz',1000)})
CIN in acin 1u
RIN acin minus 100k
RTRIMTOP vp trim {max(1,100000*(1-fraction))}
RTRIMBOT trim vn {max(1,100000*fraction)}
RTRIM trim plus 470k
RPLUS plus 0 1k
RMINUS minus 0 1k
ID vp db DC 1m
IABC vp abc DC {case.get('bias',.0005)}
XOTA abc db plus minus io vn 0 unused vp LM13700/NS
RUNUSED unused vn 100k
XOP 0 io vp vn out OPAx134
RF io out 215k
CF io out 10p
RLOAD out 0 110k
.end
'''


def measure(case):
    import numpy as np
    sys.path.insert(0, str(ROOT/'engineering/whole-amp/tools'))
    import spice_runtime as sp
    text=deck(case)
    sp.load(text); sp.cmd('op')
    result={'op': {n:float(sp.vector('v('+n+')')[-1]) for n in ['out','plus','minus','db']}}
    if not case.get('dc_only'):
        hz=case['hz']; step=1/(hz*256*case.get('refine',1)); stop=16/hz
        sp.cmd(f'tran {step:.12g} {stop:.12g} 0 {step:.12g}')
        t=np.array(sp.vector('time')); y=np.array(sp.vector('v(out)'))
        assert t[-1]>=stop*(1-1e-7)
        sample_t=np.arange(8*1024)/(hz*1024)+8/hz
        sampled=np.interp(sample_t,t,y)
        spectrum=np.fft.rfft(sampled); amps=2*abs(spectrum)/len(sampled)
        fundamental=float(amps[8]); harmonics=[float(amps[8*i]) for i in range(2,10)]
        result.update(end_s=float(t[-1]),fundamental_peak_V=fundamental,
                      gain=fundamental/case['amplitude'],
                      thd_percent=float(np.linalg.norm(harmonics)/fundamental*100) if fundamental>1e-9 else None,
                      dc_V=float(np.mean(sampled)),peak_V=float(np.max(abs(sampled))),
                      harmonics_peak_V=harmonics)
    result['log']='\n'.join(sp.logs)
    return result


def bounded(case):
    try:
        p=subprocess.run([sys.executable,__file__,'--case',json.dumps(case)],capture_output=True,text=True,timeout=40)
        if p.returncode: return {'status':'failed','error':p.stderr[-2500:],'stdout':p.stdout[-2500:]}
        return {'status':'complete',**json.loads(p.stdout)}
    except subprocess.TimeoutExpired:
        return {'status':'timeout','seconds':40}


def main():
    rows=[]; logs=[]
    def run(name,case):
        text=deck(case); path=OUT/f'ota-{name}.cir'; path.write_text(text)
        result=bounded(case); log=result.pop('log',''); logs.append(name+'\n'+log)
        row={'name':name,'case':case,'deck':path.name,'sha256':hashlib.sha256(text.encode()).hexdigest(),**result}; rows.append(row)
        print(name,result.get('status'),result.get('gain'),result.get('thd_percent'),flush=True)
        return row
    a=run('dc-untrimmed',{'dc_only':True,'trim_fraction':.5})
    b=run('dc-trim-probe',{'dc_only':True,'trim_fraction':.25})
    assert a['status']==b['status']=='complete'
    trim=.5-a['op']['out']*(.25-.5)/(b['op']['out']-a['op']['out'])
    c=run('dc-trimmed',{'dc_only':True,'trim_fraction':trim})
    # One further secant step; this is model calibration, not a real trim network.
    trim=trim-c['op']['out']*(.25-trim)/(b['op']['out']-c['op']['out'])
    calibrated=run('dc-calibrated',{'dc_only':True,'trim_fraction':trim})
    assert abs(calibrated['op']['out'])<.001, calibrated
    for bias in [0,.00005,.00025,.0005]:
        for label,offset in [('untrimmed',.5),('trimmed',trim)]:
            run(f'dc-{label}-{bias:g}',{'dc_only':True,'trim_fraction':offset,'bias':bias})
    for hz in [100,1000,10000]:
        for amplitude in [.1,1,10]:
            run(f'audio-{hz}-{amplitude:g}',dict(hz=hz,amplitude=amplitude,trim_fraction=trim))
    for bias in [.00005,.00025]:
        run(f'gain-{bias:g}',dict(hz=1000,amplitude=10,trim_fraction=trim,bias=bias))
    run('rail12',dict(hz=1000,amplitude=8,trim_fraction=trim,rail=12))
    run('refinement',dict(hz=10000,amplitude=10,trim_fraction=trim,refine=2))
    for shunt in [1e11,1e13]:
        run(f'shunt-{shunt:g}',dict(hz=1000,amplitude=10,trim_fraction=trim,rshunt=shunt))
    for temperature in [0,70]:
        run(f'temperature-{temperature}',dict(dc_only=True,trim_fraction=trim,temperature=temperature))
    provenance={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OTA,OP,Path(__file__)]}
    result=dict(scope='Nominal TI standalone audio cell, ideal current sources and calibrated resistor trim. Not a selected part or full control system.',trim_fraction=trim,provenance=provenance,cases=rows)
    (OUT/'ota-screen.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'ota-screen.log').write_text('\n'.join(logs))


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--case': print(json.dumps(measure(json.loads(sys.argv[2]))))
    else: main()
