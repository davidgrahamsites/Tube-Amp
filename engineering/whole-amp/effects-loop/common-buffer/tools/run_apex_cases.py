import subprocess,json,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
script=Path(__file__).resolve().with_name('apex_return.py')
cases={
'dw':'', 'dw-short':'--short', 'cc':'--part PA340 --iso 3300', 'cc-hot':'--part PA340 --iso 3300 --rail 320 --temp 85', 'cc-low':'--part PA340 --iso 3300 --rail 300 --temp -25', 'cc-short':'--part PA340 --iso 3300 --short', 'cc-original':'--part PA340 --iso 3300 --old-send', 'cc-1k':'--part PA340 --iso 3300 --hz 1000 --peak 4.27', 'cc-zero':'--part PA340 --iso 3300 --pf 0', 'cc-fine':'--part PA340 --iso 3300 --steps 640 --cycles 90','cc-100':'--part PA340 --iso 3300 --pf 100'}
cases.update({
    'trim-20k':'--trimmed', 'trim-fine':'--trimmed --steps 640 --cycles 90',
    'trim-clean':'--trimmed --hz 1000 --peak 4.27', 'trim-bass':'--trimmed --hz 20 --cycles 30',
    'trim-hot':'--trimmed --temp 85 --rail 320','trim-cold':'--trimmed --temp -25 --rail 300',
    'trim-short':'--trimmed --short', 'trim-unloaded':'--trimmed --pf 0',
})
cases.update({
    'guard-20k':'','guard-fine':'--steps 640 --cycles 90','guard-hot':'--temp 85 --rail 320',
    'guard-bass':'--hz 20 --cycles 30','guard-clean':'--hz 1000 --peak 4.27',
    'guard-short':'--short --temp 85 --rail 320','guard-zero':'--pf 0',
})
def run(c):
 k,args=c
 if k.startswith('guard-'):args='--part PA340 --iso 3300 --trimmed --guarded '+args
 if k.startswith('trim-'):args='--part PA340 --iso 3300 '+args
 p=subprocess.run([sys.executable,str(script),*args.split()],capture_output=True,text=True,timeout=240)
 print(k,p.returncode,p.stderr[-350:],flush=True)
 return (k,json.loads(p.stdout) if p.returncode==0 else {'error':p.stderr[-800:]})
with ThreadPoolExecutor(3) as pool:
 rows=dict(pool.map(run,cases.items()))
(script.parents[1]/'results/apex-return.json').write_text(json.dumps(rows,indent=2)+'\n')
