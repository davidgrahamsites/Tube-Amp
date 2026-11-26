"""HD012: validate a positive reset floor and isolate startup model boundaries."""
from pathlib import Path
import argparse,csv,gzip,hashlib,io,json
import numpy as np
import monitor_hold as h
M=h.M;sp=h.sp

def sha(b):return hashlib.sha256(b).hexdigest()
def deck(case):
    if case.startswith('coupled'):
        text,stop=h.deck('startup-'+case.split('-')[-1])
    else:
        source='320' if case!='monitor-startup' else 'PWL(0 0 .01 0 .06 320 .65 320)'
        wave={'release':'PWL(0 330 .05 330 .25 0 .30 0 .5 280 .65 280)','trip':'PWL(0 0 .1 280 .2 280 .201 330 .3 330 .5 0 .65 0)','monitor-startup':'PWL(0 0 .1 0 .3 280 .65 280)'}[case]
        text=f'HD012 reset-floor fixture; no hardware qualification\nVIN IN 0 {source}\nVOUT OUT 0 {wave}\n.func if(c,a,b) {{c ? a : b}}\n'+h.monitor()+'\n.end\n';stop=.65
    text=text.replace('XHOLD FB HALF MON 0 POS LM2903B','XHOLD FB HALF MON 0 HOLD LM2903B\nRRESET HOLD POS 1000')
    text=text.replace('BSH MON 0 I=','DSH 0 MON DSHUNT\n.model DSHUNT D IS=1e-12 N=1 RS=1\nBSH MON 0 I=')
    if 'startup' in case or case.startswith('coupled'):text=text.replace('\n.end\n','\n.options method=gear maxord=2\n.end\n')
    return text,stop

def run(case,step):
    factory=sha(Path(__file__).read_bytes());text,stop=deck(case);stem='reset-'+case+('-fine' if step<20e-6 else '');out=M/'results'
    (out/(stem+'.cir')).write_text(text)
    sp.cmd('set ngbehavior=psa');sp.load(text);names=['v(in)','v(out)','v(mon)','v(vr)','v(pos)','v(hold)','v(cmp)','v(sen)','v(fb)','v(half)','i(vled)'];sp.cmd('save '+' '.join(names));sp.cmd(f'tran {step} {stop} 0 {step}')
    (out/(stem+'.log')).write_text('\n'.join(sp.logs)+'\n');t=np.asarray(sp.vector('time'));a={n:np.asarray(sp.vector(n)) for n in names}
    r=dict(case=case,rows=len(t),factory_sha256=factory,prior_factory_sha256=h.sha(M/'tools/monitor_hold.py'),deck_sha256=sha(text.encode()),completed=bool(len(t) and abs(t[-1]-stop)<1e-9),qualification=False,step_s=step)
    if len(t):
        assert all(np.all(np.isfinite(v)) for v in a.values());buf=io.StringIO();w=csv.writer(buf);w.writerow(['time']+names);w.writerows(zip(t,*(a[n] for n in names)));raw=buf.getvalue().encode();packed=gzip.compress(raw,mtime=0);(out/(stem+'.csv.gz')).write_bytes(packed)
        r.update(last_time_s=float(t[-1]),raw_sha256=sha(raw),compressed_sha256=sha(packed),ranges={n:[float(v.min()),float(v.max())] for n,v in a.items()},final={n:float(v[-1]) for n,v in a.items()},samples={str(tm):{n:float(v[np.abs(t-tm).argmin()]) for n,v in a.items()} for tm in [.01,.15,.26,.29,.55,.64]})
        for key,mask in [('trip',(a['i(vled)'][:-1]<.0005)&(a['i(vled)'][1:]>=.0005)),('reset',(a['i(vled)'][:-1]>=.0005)&(a['i(vled)'][1:]<.0005))]:
            r[key]=[dict(time_s=float(t[i]),output_V=float(a['v(out)'][i])) for i in np.where(mask)[0]+1]
    (out/(stem+'.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=['release','trip','monitor-startup','coupled-320','coupled-550']);p.add_argument('--step',type=float,default=20e-6);a=p.parse_args();run(a.case,a.step)
