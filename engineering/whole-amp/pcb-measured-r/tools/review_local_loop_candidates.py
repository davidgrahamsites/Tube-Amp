"""Read-only native DRC/render of candidates. Usage: script CANDIDATE_DIR.
Writes fixed-name evidence files, replacing prior run; preserves active/candidate CAD.
Run ordinary Python. Requires KiCad CLI and rsvg-convert on macOS.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,hashlib,collections
import sys
out=Path(sys.argv[1]); review=Path(__file__).resolve().parents[1]/'review'; cli='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def run(name):
 b=out/f'Renegade_{name}.kicad_pcb';h=hashlib.sha256(b.read_bytes()).hexdigest();d=review/f'local-loop-{name}-drc.json';svg=review/f'local-loop-{name}.svg'
 cmd=[cli,'pcb','drc','--format','json','--severity-all','--all-track-errors','--refill-zones','-o',str(d),str(b)]
 r=subprocess.run(cmd,capture_output=True,text=True); assert r.returncode==0,r.stderr
 subprocess.run([cli,'pcb','export','svg','--layers','F.Cu,B.Cu,F.Silkscreen,F.Fab,Edge.Cuts','--mode-single','--fit-page-to-board','--exclude-drawing-sheet','-o',str(svg),str(b)],capture_output=True,check=True)
 svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
 subprocess.run(['/usr/local/bin/rsvg-convert','-w','1800','-o',f'/tmp/local-loop-{name}.png',str(svg)],check=True)
 assert hashlib.sha256(b.read_bytes()).hexdigest()==h
 j=json.load(open(d));return name,{'sha256':h,'violations':dict(collections.Counter(v['type'] for v in j['violations'])),'unconnected':len(j['unconnected_items']),'command':cmd,'returncode':r.returncode}
with ThreadPoolExecutor(max_workers=4) as pool: report=dict(pool.map(run,['Main','Power','Control','Reverb']))
(review/'local-loop-native-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
