"""Real OPAx134 macro-model SEND screen, separate from return qualification."""
import hashlib,json,sys,subprocess
import numpy as np
from fixture import ROOT,WHOLE
from run import sp,stats
OUT=ROOT/'results'
MODEL=WHOLE.parent/'solid-state-reverb/simulation/models/OPAx134.LIB'

def make_deck(load=10000,cable=2e-9,short=False,amplitude=100):
    return f'''Padded SEND candidate: TI OPAx134 macro-model, not a released circuit
.include "{MODEL}"
.options method=gear maxord=2 reltol=.001 abstol=1n vntol=10u gmin=1e-10 rshunt=1e12 cshunt=1e-14
.nodeset v(BUF)=0 v(PORT)=0
VP VP 0 15
VN VN 0 -15
VS PREAMP 0 DC 0 AC 1 SIN(0 {amplitude} 1000)
RH PREAMP PAD 9.9meg
RL PAD 0 100k
XU PAD BUF VP VN BUF OPAx134
RO BUF PORT 100
RLOAD PORT 0 {.01 if short else load}
CCABLE PORT 0 {cable}
.end
'''

def worker():
    rows=[]
    for load in [10000,100000]:
        for cable in [1e-15,2e-9,10e-9]:
            text=make_deck(load=load,cable=cable)
            sp.load(text);sp.cmd('op');offset=sp.vector('v(PORT)')[-1]
            sp.cmd('ac dec 40 20 10000000')
            f=np.real(sp.vector('frequency'));v=np.array(sp.vector('v(PORT)'))
            assert len(f)>1 and f[-1]>=1e7*(1-1e-8), 'Incomplete AC sweep'
            h=v/.01;i=int(np.argmin(abs(f-1000)))
            rows.append(dict(load_ohm=load,cable_F=cable,output_offset_V=offset,gain_normalized_1k=abs(h[i]),max_normalized_gain=float(np.max(abs(h))),
                             gain_20k_relative_1k_dB=float(20*np.log10(abs(h[int(np.argmin(abs(f-20000)))])/abs(h[i])))))
            (OUT/f'send-real-{load}-{cable}.cir').write_text(text);sp.cmd('destroy all')
    trans=[]
    for amplitude in [100,200]:
        for short in [False,True]:
            text=make_deck(amplitude=amplitude,short=short)
            (OUT/f'send-real-tran-{amplitude}-{short}.cir').write_text(text)
            sp.load(text);sp.cmd('op')
            bias={n:sp.vector(n)[-1] for n in ['v(BUF)','v(PORT)','vp#branch','vn#branch']}
            assert abs(bias['v(BUF)'])<.002 and max(abs(bias['vp#branch']),abs(bias['vn#branch']))<.01,bias
            sp.cmd('tran 1u .03 .01 1u')
            t=np.array(sp.vector('time'))
            if not len(t) or t[-1]<.03*(1-1e-8):
                trans.append(dict(source_peak_V=amplitude,shorted=short,status='failed',last_log=sp.logs[-5:]))
                sp.cmd('destroy all');continue
            buf=np.array(sp.vector('v(BUF)'));port=np.array(sp.vector('v(PORT)'));current=(buf-port)/100
            trans.append(dict(source_peak_V=amplitude,shorted=short,status='completed',op=bias,end_s=t[-1],buffer=stats(t,buf,1000,.03),port=stats(t,port,1000,.03),
                              peak_series_current_A=float(np.max(abs(current))),series_resistor_mean_W=float(np.sum(np.diff(t)*(current[1:]**2+current[:-1]**2)/2)*100/(t[-1]-t[0]))))
            sp.cmd('destroy all')
    data=dict(model_path=str(MODEL.relative_to(WHOLE.parent.parent)),model_sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),
              ac=rows,transient=trans,scope='Standalone nominal +/-15 V typical manufacturer macro-model. 9.9M/100k provisional pad. 10k/100k loads and up to 10nF cable. No integrated amplifier, supply sequencing, fault protection, component tolerance, noise or physical validation. No return-stage approval.')
    (OUT/'send-real-summary.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))

if __name__=='__main__':
    if '--worker' in sys.argv:
        try:worker()
        finally:(OUT/'send-real.log').write_text('\n'.join(l.rstrip() for l in sp.logs)+'\n')
    else:
        result=subprocess.run([sys.executable,__file__,'--worker'],timeout=60)
        if result.returncode:raise SystemExit(result.returncode)
