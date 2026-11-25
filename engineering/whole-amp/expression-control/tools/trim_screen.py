"""Nominal trim-range repair; reuse the prior physical candidate without changing it."""
import hashlib,json,subprocess,sys
from pathlib import Path
import bias_screen as bias
ota=bias.ota

def run(name,case):
    path=ota.OUT/('trim-'+name+'.cir');path.write_text(bias.deck(case))
    try:
        p=subprocess.run([sys.executable,bias.__file__,'--case',json.dumps(case)],capture_output=True,text=True,timeout=25)
        r=json.loads(p.stdout) if p.returncode==0 else dict(status='failed',error=p.stderr[-2000:])
        log=r.pop('log','')+'\n'+p.stderr
    except subprocess.TimeoutExpired as e:
        r=dict(status='timeout',seconds=25);log=str(e.stderr or '')
    lp=ota.OUT/('trim-'+name+'.log');lp.write_text(log)
    print(name,r['status'],r.get('op',{}).get('out'),r.get('gain'),flush=True)
    return dict(name=name,case=case,deck=path.name,deck_sha256=sha(path),log=lp.name,log_sha256=sha(lp),**r)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=[]
    def add(n,c):
        r=run(n,c);rows.append(r);return r
    calibrated={}
    for resistance in [220000,150000]:
        a=add(f'{resistance}-low',dict(dc_only=True,trim_resistance=resistance,trim_fraction=.4))
        b=add(f'{resistance}-high',dict(dc_only=True,trim_resistance=resistance,trim_fraction=.8))
        for i in range(4):
            if a['status']!='complete' or b['status']!='complete':break
            x,y=a['case']['trim_fraction'],b['case']['trim_fraction'];va,vb=a['op']['out'],b['op']['out']
            t=y-vb*(y-x)/(vb-va)
            if not 0<t<1:break
            c=add(f'{resistance}-cal-{i}',dict(dc_only=True,trim_resistance=resistance,trim_fraction=t))
            a,b=b,c
            if c['status']=='complete' and abs(c['op']['out'])<1e-6:calibrated[str(resistance)]=t;break
    trim=calibrated.get('150000')
    if trim is not None:
        base=dict(trim_resistance=150000,trim_fraction=trim)
        for rail in [12,15,16.5]:
            for target in [0,2.5,4.9,5]:add(f'dc-{rail}-{target}',dict(base,dc_only=True,rail=rail,target=target))
        for hz in [100,1000,10000]:add(f'audio-{hz}',dict(base,hz=hz,amplitude=8))
        add('audio-12',dict(base,hz=1000,amplitude=8,rail=12))
        add('audio-refined',dict(base,hz=1000,amplitude=8,refine=2))
        for temp in [0,70]:add(f'temp-{temp}',dict(base,dc_only=True,temperature=temp))
        for shunt in [1e11,1e13]:add(f'shunt-{shunt:g}',dict(base,dc_only=True,rshunt=shunt))
    inputs=[Path(__file__),Path(bias.__file__),Path(ota.__file__),ota.OTA,ota.OP,bias.BJT]
    report=dict(scope='Nominal trim correction only. No pedal, native adoption, real trim tolerance, noise, startup or purchasing qualification.',calibrated_fractions=calibrated,cases=rows,provenance={str(p.relative_to(ota.ROOT)):sha(p) for p in inputs})
    (ota.OUT/'trim-screen.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
