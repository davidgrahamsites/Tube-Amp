"""Run bounded reference cases; one stable result set, no timestamped copies."""
from pathlib import Path
import subprocess
import json
import time
import sys
import numpy as np
from fixture import ROOT, WHOLE, deck, fingerprint
sys.path.insert(0,str(WHOLE/'tools'))
import spice_runtime as sp
OUT=ROOT/'results'
NODES=['FX_SEND','FX_RETURN','MIX_OUT','SEND_IN','PI_G1','PI_TAIL_TOP','PI_P1','PI_P2','EL34_GA','EL34_GB','SPEAKER']

def ac_case(**kw):
    text,inventory=deck(**kw)
    sp.load(text);sp.cmd('op')
    op={n:sp.vector('v('+n+')')[-1] for n in NODES}
    sp.cmd('ac dec 24 20 20000')
    freqs=np.real(sp.vector('frequency'))
    nodes=NODES+(['SEND_PAD','SEND_PORT'] if kw.get('mode','').startswith('send-isolated') else [])
    signals={n:sp.vector('v('+n+')') for n in nodes}
    selected={}
    for hz in [20,82.4,1000,5000,20000]:
        i=int(np.argmin(abs(freqs-hz)))
        selected[str(hz)]={'actual_Hz':float(freqs[i]),'magnitude':{n:float(abs(y[i])) for n,y in signals.items()},'phase_deg':{n:float(np.angle(y[i],deg=True)) for n,y in signals.items()}}
    if kw.get('mode')=='return-drive':
        z=[]
        for v in signals['FX_RETURN']:
            current=(1-v)/kw.get('source_ohm',1000)
            z.append(abs(v/current))
        selected['return_impedance_ohm']={str(hz):float(z[int(np.argmin(abs(freqs-hz)))]) for hz in [20,82.4,1000,5000,20000]}
    sp.cmd('destroy all')
    return {'config':kw,'op':op,'points':selected},text,inventory

def stats(t,y,f,end):
    times=end-(10-np.arange(2560)/256)/f
    v=np.interp(times,t,y); z=np.fft.rfft(v)/len(v)
    h=2*np.abs(z[np.arange(1,11)*10]); fundamental=h[0]
    return dict(min_V=float(v.min()),max_V=float(v.max()),mean_V=float(v.mean()),fundamental_Vpk=float(fundamental),THD_2_to_10_percent=float(100*np.linalg.norm(h[1:])/fundamental) if fundamental>1e-10 else None)

def transient_case(steps=96,max_step=20e-6,**kw):
    text,_=deck(**kw);sp.load(text);sp.cmd('op')
    f=kw.get('freq',1000);end=max(.5,30/f);step=min(max_step,1/(f*steps))
    sp.cmd(f'tran {step} {end} {max(0,end-20/f)} {step}')
    t=np.array(sp.vector('time'));assert len(t) and t[-1]>=end*(1-1e-8), sp.logs[-8:]
    signals={n:np.array(sp.vector('v('+n+')')) for n in NODES}
    s={n:stats(t,y,f,end) for n,y in signals.items()}
    earlier={n:stats(t,y,f,end-10/f) for n,y in signals.items()}
    settling={n:abs(s[n]['fundamental_Vpk']-earlier[n]['fundamental_Vpk'])/max(s[n]['fundamental_Vpk'],1e-12) for n in NODES}
    sp.cmd('destroy all')
    return dict(config=kw,steps_per_cycle=steps,max_step_s=step,end_s=float(t[-1]),signals=s,settling_relative_fundamental=settling),text

def main():
    sp.cmd('version');version=list(sp.logs)
    ac=[];trans=[];inventory=None
    polarity=[]
    for sign in [0,1,-1]:
        row,text,_=ac_case(mode='return-drive',amp=0,feedback_phase=sign)
        polarity.append(row)
        (OUT/f'polarity-{sign}.cir').write_text(text)
    (OUT/'polarity-check.json').write_text(json.dumps(polarity,indent=2)+'\n')
    assert polarity[1]['points']['1000']['magnitude']['SPEAKER'] < polarity[0]['points']['1000']['magnitude']['SPEAKER']
    for ch in ['clean','dirty']:
        for vol in [.01,.25,1]:
            for tone in [0,.5,1]:
                for mode in ['native','buffer']:
                    for stim in ['dry','wet']:
                        row,text,inventory=ac_case(channel=ch,mode=mode,stimulus=stim,volume=vol,tone=tone,amp=0)
                        ac.append(row)
                        (OUT/f'ac-{len(ac):03}.cir').write_text(text)
    row,text,_=ac_case(mode='return-drive',amp=0)
    ac.append(row);(OUT/'return-impedance.cir').write_text(text)
    # Current loop's direct short is a known architectural continuity failure.
    row,text,_=ac_case(mode='send-short',amp=0)
    ac.append(row);(OUT/'send-short.cir').write_text(text)
    (OUT/'ac-summary.json').write_text(json.dumps(ac,indent=2)+'\n')
    print('AC cases:',len(ac),flush=True)
    # Each nonlinear case is isolated and time-bounded: a failed solve must not
    # hide completed cases or prevent an explicit coverage report.
    configs=[dict(channel=ch,supply=278,freq=1000,amp=a)
             for ch,amps in [('clean',[.01,.1]),('dirty',[.001,.01])]
             for a in amps]
    if '--extended' in sys.argv:
        configs=[dict(channel=ch,supply=s,freq=f,amp=a)
                 for ch in ['clean','dirty'] for s in [240,278,320]
                 for f in [82.4,1000,5000] for a in [.01,.1,1]]
    for i,config in enumerate(configs):
        trans.append(bounded_case('tran-'+str(i+1).zfill(3),config))
        (OUT/'transient-summary.json').write_text(json.dumps(trans,indent=2)+'\n')
    refine=[bounded_case('refine-'+ch,dict(channel=ch,supply=278,freq=1000,amp=a,steps=192,max_step=10e-6))
            for ch,a in [('clean',.01),('dirty',.001)]]
    data={'source_hashes':fingerprint(),'simulator_version_log':version,'included_parts':inventory,
          'scope':'Both preamps, actual passive mix and bootstrapped PI, generic EL34 pair, ideal 7600:8 transformer, actual NFB resistors. Stiff 400V main/380V screen/-40V bias; B_EARLY 240/278/320, B_PRE+35 sensitivity only. Wet source ideal at OUT_BUF; spring follower input infinite. No real magnetics, reverb clamps/drive/decay, PSU sag, tube tolerance, noise or physical validation.',
          'coverage_limits':'AC volume/tone corners. Default nonlinear scope: four 1kHz nominal-supply cases plus two timestep refinements, volume .25 and tone/gain .5. Extended matrix optional. No pick burst/recovery or qualified supply/pedal envelope. Failures are coverage gaps, not passing results.',
          'ac_cases':ac,'transient_cases':trans,'refinements':refine}
    (OUT/'summary.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    print('Saved',len(ac),'AC and',len(trans)+len(refine),'transient cases',flush=True)

def bounded_case(name, config, time_limit_s=30):
    start=time.monotonic()
    command=[sys.executable,str(Path(__file__).resolve()),'--worker',name,json.dumps(config)]
    try:
        result=subprocess.run(command,capture_output=True,text=True,timeout=time_limit_s)
        if result.returncode:
            row={'status':'failed','config':config,'error':result.stderr[-3000:]}
        else:
            row=json.loads((OUT/(name+'.json')).read_text())
    except subprocess.TimeoutExpired:
        row={'status':'timeout','config':config,'error':f'{time_limit_s} second wall-time limit; worker terminated; no completed nonlinear result.'}
    row['wall_time_limit_s']=time_limit_s
    row['elapsed_s']=time.monotonic()-start
    (OUT/(name+'.json')).write_text(json.dumps(row,indent=2)+'\n')
    print(name,row.get('status'),flush=True)
    return row

if __name__=='__main__':
    from pathlib import Path
    name=sys.argv[2] if '--worker' in sys.argv else 'ngspice'
    try:
        if '--worker' in sys.argv:
            config=json.loads(sys.argv[3])
            args={k:v for k,v in config.items() if k not in {'steps','max_step'}}
            text,_=deck(**args)
            (OUT/(name+'.cir')).write_text(text)
            row,_=transient_case(**config)
            row['status']='completed'
            (OUT/(name+'.json')).write_text(json.dumps(row,indent=2)+'\n')
        else:main()
    finally:(OUT/(name+'.log')).write_text('\n'.join(line.rstrip() for line in sp.logs)+'\n')
