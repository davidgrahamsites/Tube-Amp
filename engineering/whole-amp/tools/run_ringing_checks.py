from pathlib import Path
import subprocess,json
py='/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3';p=Path(__file__).resolve().parents[1]/'simulation/candidate-hf'
for mode in ['reference-step','half-step','feedback-zero']:
 try:
  r=subprocess.run([py,str(Path(__file__).with_name('check_ringing_transient.py')),mode],capture_output=True,text=True,timeout=180);result={'variant':mode,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
 except subprocess.TimeoutExpired:result={'variant':mode,'timeout_s':180}
 (p/(mode+'-execution.json')).write_text(json.dumps(result,indent=2));print(result,flush=True)
