"""Bounded solver diagnosis and model-guard validation; no hardware edits."""
import concurrent.futures
import json
import subprocess
import sys
from fixture import ROOT, deck, fingerprint
from run import bounded_case, sp
OUT=ROOT/'results'
VARIANTS=['baseline','iterations','trap','preamp','no-output','no-shunts','guarded-power']

def diagnostic(name):
    text,_=deck(channel='clean',supply=240,amp=1,guard_pentode_power=name=='guarded-power')
    if name=='iterations':text=text.replace('.options ','.options itl4=100 ')
    if name=='trap':text=text.replace('method=gear','method=trap').replace('.options ','.options itl4=100 ')
    if name in {'preamp','no-output'}:
        removed=('XV4_','XV5_','XV6_') if name=='preamp' else ('XV5_','XV6_')
        text='\n'.join(l for l in text.splitlines() if not l.startswith(removed))+'\n'
    if name=='no-shunts':text=text.replace(' rshunt=1e12 cshunt=1e-14','')
    (OUT/f'solver-{name}.cir').write_text(text)
    try:
        sp.load(text);sp.cmd('tran 10u .05 0 10u')
        t=sp.vector('time');finished=bool(t) and t[-1]>=.05*(1-1e-8)
        row={'variant':name,'status':'completed' if finished else 'failed','end_s':t[-1] if t else None,'rows':len(t),'last_log':sp.logs[-5:]}
    finally:
        (OUT/f'solver-{name}.log').write_text('\n'.join(l.rstrip() for l in sp.logs)+'\n')
    (OUT/f'solver-{name}.json').write_text(json.dumps(row,indent=2)+'\n')

def main():
    diagnostics=[]
    for name in VARIANTS:
        try:
            p=subprocess.run([sys.executable,__file__,'--diagnostic',name],capture_output=True,text=True,timeout=30)
            if p.returncode:raise RuntimeError(p.stderr[-2000:])
            row=json.loads((OUT/f'solver-{name}.json').read_text())
        except subprocess.TimeoutExpired:row={'variant':name,'status':'timeout'}
        diagnostics.append(row);print(name,row['status'],flush=True)
    configs=[]
    # Retained legacy nominal cases provide an independent comparison target.
    for ch,amps in [('clean',[.01,.1]),('dirty',[.001,.01])]:
        for a in amps:configs.append((f'guard-nominal-{ch}-{a}',dict(channel=ch,supply=278,freq=1000,amp=a,guard_pentode_power=True)))
    for ch in ['clean','dirty']:
        for supply in [240,320]:
            for f in [82.4,1000,5000]:
                configs.append((f'guard-heavy-{ch}-{supply}-{f}',dict(channel=ch,supply=supply,freq=f,amp=1,guard_pentode_power=True)))
    configs.append(('guard-heavy-refined-384',dict(channel='clean',supply=240,freq=1000,amp=1,guard_pentode_power=True,steps=384,max_step=5e-6)))
    configs.append(('guard-heavy-refined',dict(channel='clean',supply=240,freq=1000,amp=1,guard_pentode_power=True,steps=192,max_step=10e-6)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        rows=list(pool.map(lambda pair:bounded_case(*pair),configs))
    nominal=json.loads((OUT/'transient-summary.json').read_text())
    errors=[]
    for old,new in zip(nominal,rows[:4]):
        if new['status']=='completed':
            for node in old['signals']:
                a=old['signals'][node]['fundamental_Vpk'];b=new['signals'][node]['fundamental_Vpk']
                errors.append(abs(a-b)/max(abs(a),1e-12))
    data={'source_hashes':fingerprint(),'diagnostics':diagnostics,'cases':dict(zip([p[0] for p in configs],rows)),
          'max_nominal_relative_fundamental_change':max(errors) if len(errors)==44 else None,
          'scope':'Numerical domain-guard qualification only. Original tube files unchanged. Removed-stage diagnostics are fault-localization fixtures, not amplifier designs. Heavy cases use volume .25, tone/gain .5; not all controls or physical tank/transformer validation.'}
    (OUT/'solver-review.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')

def retry_timeouts():
    path=OUT/'solver-review.json';data=json.loads(path.read_text())
    todo=[(name,row) for name,row in data['cases'].items() if row['status']=='timeout']
    def retry(pair):
        name,old=pair
        new=bounded_case(name,old['config'],time_limit_s=300)
        new['previous_attempt']={k:old[k] for k in ['status','error','elapsed_s']}
        (OUT/(name+'.json')).write_text(json.dumps(new,indent=2)+'\n')
        return name,new
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for name,row in pool.map(retry,todo):
            data['cases'][name]=row
            path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':
    if '--diagnostic' in sys.argv:diagnostic(sys.argv[2])
    elif '--retry-timeouts' in sys.argv:retry_timeouts()
    else:main()
