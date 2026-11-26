"""Additional near-25W comparison in the same loaded-transformer fixture."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

M=Path(__file__).resolve().parents[1]
ROOT=M.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    c=json.loads((M/'contract.json').read_text())
    for p,h in c['source_sha256'].items():assert sha(ROOT/p)==h,p
    rows=[]
    for limit in [None,12]:
        case=dict(id='clean-25w-probe'+('-unlimited' if limit is None else '-12'),
                  scenario='clean-25w-probe',channel='clean',amp=.009,freq=1000,
                  volume=1,tone=.5,gain=.5,ceiling_V=limit)
        name=case['id'];start=time.monotonic()
        (M/'results'/f'{name}.json').unlink(missing_ok=True)
        try:
            p=subprocess.run([sys.executable,str(M/'tools/run.py'),'--worker',json.dumps(case)],
                             capture_output=True,text=True,timeout=90)
            (M/'results'/f'{name}.log').write_text(p.stdout+p.stderr)
            row=json.loads((M/'results'/f'{name}.json').read_text()) if p.returncode==0 else dict(
                status='failed',case=case,error=(p.stdout+p.stderr)[-1500:])
        except subprocess.TimeoutExpired as e:
            row=dict(status='timeout',case=case,error='90 second wall limit')
            (M/'results'/f'{name}.log').write_bytes((e.stdout or b'')+(e.stderr or b''))
        row['elapsed_s']=time.monotonic()-start;rows.append(row)
        (M/'results'/f'{name}.json').write_text(json.dumps(row,indent=2)+'\n')
        print(name,row['status'],row.get('fundamental_load_W'),flush=True)
    for p,h in c['source_sha256'].items():assert sha(ROOT/p)==h,p
    out=dict(cases=rows,contract_sha256=sha(M/'contract.json'),factory_sha256=sha(Path(__file__)),
             worker_sha256=sha(M/'tools/run.py'),source_sha256=c['source_sha256'],
             hardware_qualified=False,adopted=False)
    (M/'results/target.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':main()
