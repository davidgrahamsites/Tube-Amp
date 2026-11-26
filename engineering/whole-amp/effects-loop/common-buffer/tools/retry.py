"""Retry terminal timeout cases without changing their physical/numerical setup."""
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
    summary_path=M/'results/summary.json'
    s=json.loads(summary_path.read_text())
    assert s['factory_sha256']==sha(M/'tools/run.py')
    assert s['contract_sha256']==sha(M/'contract.json')
    for p,h in s['source_sha256'].items():assert sha(ROOT/p)==h,p
    receipt_path=M/'results/retry.json'
    receipts=json.loads(receipt_path.read_text())['cases'] if receipt_path.exists() else []
    for i,row in enumerate(s['cases']):
        if row['status']!='timeout':continue
        if any(r['id']==row['case']['id'] for r in receipts):continue
        case=row['case'];name=case['id'];start=time.monotonic()
        original_deck=sha(M/'results'/f'{name}.cir')
        oldlog=M/'results'/f'{name}.log'
        priorlog=M/'results'/f'{name}-90s-timeout.log'
        priorlog.write_bytes(oldlog.read_bytes())
        result_path=M/'results'/f'{name}.json'
        result_path.unlink(missing_ok=True)
        try:
            p=subprocess.run([sys.executable,str(M/'tools/run.py'),'--worker',json.dumps(case)],
                             capture_output=True,text=True,timeout=300)
            oldlog.write_text(p.stdout+p.stderr)
            if p.returncode:
                new=dict(status='failed',case=case,error=(p.stdout+p.stderr)[-1500:])
            else:new=json.loads(result_path.read_text())
        except subprocess.TimeoutExpired as e:
            oldlog.write_bytes((e.stdout or b'')+(e.stderr or b''))
            new=dict(status='timeout',case=case,error='300 second wall bound; worker terminated')
        new['elapsed_s']=time.monotonic()-start
        assert sha(M/'results'/f'{name}.cir')==original_deck, 'Retry changed the deck'
        result_path.write_text(json.dumps(new,indent=2)+'\n')
        receipts.append(dict(id=name,prior_result=row,wall_limit_s=300,
                             final_status=new['status'],elapsed_s=new['elapsed_s'],
                             unchanged_deck_sha256=sha(M/'results'/f'{name}.cir')))
        s['cases'][i]=new
        print(name,new['status'],round(new['elapsed_s'],1),flush=True)
        # Save each completed retry; later interrupted work can resume terminal cases.
        s['retry_receipt']='results/retry.json'
        (M/'results/retry.json').write_text(json.dumps(dict(cases=receipts,
            retry_factory_sha256=sha(Path(__file__)),worker_sha256=sha(M/'tools/run.py'),
            scope='Only wall allowance changed; same worker, deck, measurement and numeric settings'),indent=2)+'\n')
        summary_path.write_text(json.dumps(s,indent=2)+'\n')
    for p,h in s['source_sha256'].items():assert sha(ROOT/p)==h,p


if __name__=='__main__':main()
