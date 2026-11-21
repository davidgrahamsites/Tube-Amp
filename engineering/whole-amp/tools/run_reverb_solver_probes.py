import subprocess,json,time,sys
from pathlib import Path
py='/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3'
for mode in (sys.argv[1:] or ['isolated','inputcap','cshunt']):
 t=time.monotonic()
 try:
  p=subprocess.run([py,str(Path(__file__).with_name('probe_reverb_solver.py')),mode],capture_output=True,text=True,timeout=(900 if mode=='combined_80ms' else 240))
  r={'mode':mode,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 except subprocess.TimeoutExpired:r={'mode':mode,'timeout_s':(900 if mode=='combined_80ms' else 240)}
 r['elapsed_s']=time.monotonic()-t
 Path('engineering/whole-amp/simulation/reverb-headroom/'+mode+'-execution.json').write_text(json.dumps(r,indent=2));print(r,flush=True)
