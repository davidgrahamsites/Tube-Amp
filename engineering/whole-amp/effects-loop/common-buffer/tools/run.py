"""Common-buffer ceiling comparison. No selected-device or native CAD changes."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

M = Path(__file__).resolve().parents[1]
PROJECT = M.parents[3]
TOOLS = M.parent/'tools'
sys.path.insert(0, str(TOOLS))
import numpy as np
from loaded_feedback_model import build
from run import sp, stats


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def deck(case):
    config = {k:case[k] for k in ['channel','amp','freq','volume','tone','gain']}
    text = build(mode='buffer', source_ohm=1000, supply=278, **config)
    original = 'EBUF BUF_OUT 0 FX_SEND 0 1'
    assert text.count(original) == 1
    if case['ceiling_V'] is not None:
        limit = case['ceiling_V']
        text = text.replace(original, f'BBUF BUF_OUT 0 V=max(-{limit},min({limit},V(FX_SEND)))')
    return text


def worker(case):
    name=case['id']; text=deck(case); (M/'results'/f'{name}.cir').write_text(text)
    nodes=['FX_SEND','BUF_OUT','FX_RETURN','MIX_OUT','SEND_IN','PI_G1','SPEAKER']
    sp.cmd('version'); sp.load(text); sp.cmd('op')
    sp.cmd('save '+' '.join('v('+n.lower()+')' for n in nodes))
    f=case['freq']; end=max(.5,30/f); step=min(20e-6,1/(f*96))/case.get('refinement',1)
    sp.cmd(f'tran {step} {end} {max(0,end-20/f)} {step}')
    t=np.array(sp.vector('time')); assert len(t) and t[-1]>=end*(1-1e-8)
    values={n:np.array(sp.vector('v('+n.lower()+')')) for n in nodes}
    assert all(np.isfinite(y).all() for y in values.values())
    signals={n:stats(t,y,f,end) for n,y in values.items()}
    earlier={n:stats(t,y,f,end-10/f) for n,y in values.items()}
    times=end-(10-np.arange(2560)/256)/f
    columns=np.column_stack([times,*[np.interp(times,t,values[n]) for n in nodes]])
    np.savetxt(M/'results'/f'{name}.csv',columns,delimiter=',',header='time_s,'+','.join(nodes),comments='',fmt='%.12g')
    limit=case['ceiling_V']
    row=dict(status='completed',case=case,end_s=float(t[-1]),step_s=step,signals=signals,
             settling_relative={n:abs(signals[n]['fundamental_Vpk']-earlier[n]['fundamental_Vpk'])/
                                max(signals[n]['fundamental_Vpk'],1e-12) for n in nodes},
             clipped_fraction=float(np.mean(abs(columns[:,1])>=limit)) if limit else 0,
             fundamental_load_W=signals['SPEAKER']['fundamental_Vpk']**2/16,
             deck_sha256=sha(M/'results'/f'{name}.cir'),waveform_sha256=sha(M/'results'/f'{name}.csv'))
    (M/'results'/f'{name}.json').write_text(json.dumps(row,indent=2)+'\n')
    sp.cmd('destroy all')


def main():
    contract=json.loads((M/'contract.json').read_text())
    for path,h in contract['source_sha256'].items(): assert sha(PROJECT/path)==h,path
    cases=contract['cases']
    if '--refine' in sys.argv:
        requested=sys.argv[sys.argv.index('--refine')+1]
        cases=[dict(c,id=c['id']+'-fine',refinement=2) for c in cases if c['scenario']==requested]
        assert cases
    rows=[]
    for case in cases:
        start=time.monotonic(); name=case['id']
        # Remove only previous products for this exact case before attempting it.
        for suffix in ['.json','.cir','.csv','.log']:
            (M/'results'/f'{name}{suffix}').unlink(missing_ok=True)
        try:
            p=subprocess.run([sys.executable,str(Path(__file__)),'--worker',json.dumps(case)],
                             capture_output=True,text=True,timeout=90)
            (M/'results'/f'{name}.log').write_text(p.stdout+p.stderr)
            if p.returncode: row=dict(status='failed',case=case,error=(p.stdout+p.stderr)[-1500:])
            else: row=json.loads((M/'results'/f'{name}.json').read_text())
        except subprocess.TimeoutExpired as e:
            row=dict(status='timeout',case=case,error='90 second wall bound; no completed result')
            (M/'results'/f'{name}.log').write_bytes((e.stdout or b'')+(e.stderr or b''))
        row['elapsed_s']=time.monotonic()-start
        (M/'results'/f'{name}.json').write_text(json.dumps(row,indent=2)+'\n')
        rows.append(row); print(name,row['status'],round(row.get('fundamental_load_W',0),3),flush=True)
    for path,h in contract['source_sha256'].items(): assert sha(PROJECT/path)==h,path
    out=dict(cases=rows,source_sha256=contract['source_sha256'],
             contract_sha256=sha(M/'contract.json'),factory_sha256=sha(Path(__file__)),
             adopted=False,hardware_qualified=False)
    filename='refinement.json' if '--refine' in sys.argv else 'summary.json'
    (M/'results'/filename).write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':
    if '--worker' in sys.argv:
        try: worker(json.loads(sys.argv[-1]))
        finally: print('\n'.join(sp.logs[-80:]))
    else: main()
