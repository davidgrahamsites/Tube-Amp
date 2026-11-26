"""HD-011 monitor supply and hysteresis fixtures; not a hardware qualification."""
from pathlib import Path
import argparse, csv, hashlib, json
import numpy as np
import detector_candidate as d
M=d.M
sp=d.s.p.sp

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def monitor(rejected=False):
    raw=(M/'sources/LM2903B.lib').read_text().replace('TC=0,0','')
    rh,rl=(40000,20000) if rejected else (2000000,1000000)
    return f'''RFEED1 IN FEED1 22000
RFEED2 FEED1 FEED2 22000
RFEED3 FEED2 MON 22000
CMON MON 0 1u
BSH MON 0 I=max(0,(V(MON)-8.192)/1.5)
BREF MON VR I=max(0,min(.01,(min(2.5,max(0,V(MON)-.2))-V(VR))/.1))
BQUIET MON 0 I=.000097*max(0,min(1,V(MON)/2))
CREF VR 0 .1u
RREFLOAD VR 0 100k
RREFH VR HALF 10k
RREFL HALF 0 10k
RISO VR POS 10k
RH OUT SEN 1176000
RL SEN 0 10100
XMAIN POS SEN MON 0 CMP LM2903B
XHOLD FB HALF MON 0 POS LM2903B
RFBH CMP FB {rh}
RFBL FB 0 {rl}
RPU MON CMP 100k
RLED MON L1 3650
DLED1 L1 L2 LED
DLED2 L2 LD LED
VLED LD CMP 0
.model LED D IS=1e-20 N=1.3 RS=10
'''+raw

def deck(name):
    if name.startswith('fixture'):
        text='''HD011 imposed-output monitor fixture; no pass-stage claim
VIN IN 0 320
VOUT OUT 0 PWL(0 0 .01 0 .21 330 .31 330 .51 0 .61 0 .81 280 1 280)
.func if(c,a,b) {c ? a : b}
'''
        return text+monitor(name=='fixture-rejected')+'\n.end\n',1.0
    c=json.loads((M/'detector-contract.json').read_text())
    prior=json.loads((M/'series-contract.json').read_text())
    vin=int(name.split('-')[-1]); startup=name.startswith('startup')
    text=d.s.build(prior,d.base_config(c),vin,'nominal',True,'none',dict(vto1=-5,vto2=-5,source_ohm=646),True,not startup)
    if startup:
        text=text.replace(f'VIN IN 0 {vin}',f'VIN IN 0 PWL(0 0 .01 0 .03 {vin} .6 {vin})')
    extra=monitor()
    if name.startswith('resetprobe'):
        extra=extra.replace('XHOLD FB HALF','XHOLD FBC HALF')
        extra+='VINIT FBC FB PWL(0 3 .02 3 .020001 0 .6 0)\n'
    if name.startswith('release'):
        extra+='.nodeset v(cmp)=7.9 v(pos)=2.5 v(fb)=2.65 v(mon)=8.2 v(vr)=2.5\n'
    if not startup:
        extra+='''VFAULT FC 0 PWL(0 0 .1 0 .100001 1 .6 1)
SFAIL REGIN OUT FC 0 FAULT
.model FAULT SW RON=.001 ROFF=1e12 VT=.5 VH=.1
'''
    extra+='''BOP1 GREF BASE1 I=max(0,I(VLED))*.25*max(0,min(1,V(GREF,BASE1)/.4))
BOP2 GREF2 BASE2 I=max(0,I(VLED))*.25*max(0,min(1,V(GREF2,BASE2)/.4))
XCTL1 GREF BASE1 OUT QFLOAT
XCTL2 GREF2 BASE2 OUT QFLOAT
RBE1 BASE1 OUT 100k
RBE2 BASE2 OUT 100k
.model QC NPN IS=1e-14 BF=20 VAF=100
.subckt QFLOAT C B E
EC CC 0 C E 1
EB BB 0 B E 1
QIN CC BB 0 QC
BC C E I=-I(EC)
BBI B E I=-I(EB)
.ends QFLOAT
'''
    text=text.replace('\n.end\n','\n'+extra+'\n.end\n')
    if name.startswith('resetprobe'):
        text=text.replace('PWL(0 0 .1 0 .100001 1 .6 1)','PWL(0 0 1.5 0 1.500001 1 3 1)')
        return text,3.0
    return text,.6

def run(name,step):
    text,stop=deck(name)
    stem='monitor-'+name+('-fine' if step<20e-6 else '')
    out=M/'results'
    (out/(stem+'.cir')).write_text(text)
    names=['v(in)','v(out)','v(mon)','v(vr)','v(pos)','v(cmp)','v(sen)','v(fb)','v(half)','i(vled)']
    if not name.startswith('fixture'): names+=['v(regin)','v(s)','v(g)','v(g2)','v(mid)','v(gref)','v(gref2)']
    sp.cmd('set ngbehavior=psa');sp.load(text);sp.cmd('save '+' '.join(names))
    sp.cmd(f'tran {step} {stop} 0 {step}')
    (out/(stem+'.log')).write_text('\n'.join(sp.logs)+'\n')
    t=np.asarray(sp.vector('time'));a={n:np.asarray(sp.vector(n)) for n in names}
    if not len(t):
        (out/(stem+'.json')).write_text(json.dumps(dict(case=name,completed=False,rows=0,reason='no transient rows',factory_sha256=sha(Path(__file__)),deck_sha256=sha(out/(stem+'.cir'))),indent=2)+'\n')
        return
    completed=bool(abs(t[-1]-stop)<1e-9)
    assert all(np.all(np.isfinite(v)) for v in a.values())
    with (out/(stem+'.csv')).open('w') as f:
        w=csv.writer(f);w.writerow(['time']+names)
        w.writerows(zip(t,*(a[n] for n in names)))
    idx=np.where((a['i(vled)'][:-1]<.0005)&(a['i(vled)'][1:]>=.0005))[0]+1
    reset=np.where((a['i(vled)'][:-1]>=.0005)&(a['i(vled)'][1:]<.0005))[0]+1
    result=dict(case=name,completed=completed,step_s=step,last_time_s=float(t[-1]),rows=len(t),
      ranges={n:[float(v.min()),float(v.max())] for n,v in a.items()},
      final={n:float(v[-1]) for n,v in a.items()},
      trip=[dict(time_s=float(t[i]),output_V=float(a['v(out)'][i])) for i in idx],
      reset=[dict(time_s=float(t[i]),output_V=float(a['v(out)'][i])) for i in reset],
      samples={str(tm):{n:float(v[np.abs(t-tm).argmin()]) for n,v in a.items()} for tm in ([.18,.3,.4,.6,.99] if name.startswith('fixture') else ([1.4,1.51,2,2.99] if name.startswith('resetprobe') else [.09,.11,.3,.59]))},
      factory_sha256=sha(Path(__file__)),deck_sha256=sha(out/(stem+'.cir')),csv_sha256=sha(out/(stem+'.csv')),model_sha256=sha(M/'sources/LM2903B.lib'),
      qualification=False)
    (out/(stem+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    (out/(stem+'.log')).write_text('\n'.join(sp.logs)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=['fixture','fixture-rejected','fault-320','fault-550','release-320','release-550','resetprobe-320','resetprobe-550','startup-320','startup-550']);p.add_argument('--step',type=float,default=20e-6)
    a=p.parse_args();run(a.case,a.step)
