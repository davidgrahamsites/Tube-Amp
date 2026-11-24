"""Export native Excellon temporarily and verify the two R215 round PTH hits."""
import hashlib,json,re,subprocess,tempfile
from pathlib import Path
M=Path(__file__).resolve().parents[1];BOARD=M.parent/'pcb-measured-r/boards/Renegade_Control.kicad_pcb'
def main():
 with tempfile.TemporaryDirectory(prefix='renegade-preload-drill-') as temp:
  subprocess.run(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli','pcb','export','drill','--excellon-units','mm','--excellon-separate-th','--output',temp,str(BOARD)],check=True,capture_output=True)
  text=(Path(temp)/'Renegade_Control-PTH.drl').read_text();tools={};current=None;hits=[]
  assert 'Plated,1,2,PTH' in text and 'METRIC' in text
  for line in text.splitlines():
   m=re.fullmatch(r'T(\d+)C([\d.]+)',line)
   if m:tools[m[1]]=float(m[2])
   m=re.fullmatch(r'T(\d+)',line)
   if m:current=m[1]
   m=re.fullmatch(r'X([\d.-]+)Y([\d.-]+)',line)
   if m and tuple(map(float,m.groups())) in [(196.654,-75.5),(209.354,-75.5)]:hits.append(dict(x_mm=float(m[1]),y_mm=float(m[2]),diameter_mm=tools[current],shape='round',plated=True))
  assert len(hits)==2 and all(h['diameter_mm']==.9 for h in hits)
  result=dict(passed=True,hits=hits,export_sha256=hashlib.sha256(text.encode()).hexdigest(),board_sha256=hashlib.sha256(BOARD.read_bytes()).hexdigest(),native_excellon_kit='KiCad10.0.6',limits='R215 only; shop hole tolerance, registration and actual lead forming still need inspection.')
  (M/'results/preload/drill-checks.json').write_text(json.dumps(result,indent=2)+'\n');print('R215: two round 0.9mm plated drill hits verified.')
if __name__=='__main__':main()
