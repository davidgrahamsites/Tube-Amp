"""Run native checks/plots with input hashes and unchanged-source assertions."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,shutil
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];D=M/'results';src=Path(sys.argv[1]).resolve();CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p):sha(p) for p in [src,src.with_suffix('.kicad_pro'),src.with_suffix('.kicad_dru')]};commands=[]
def run(cmd):
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);commands.append({'command':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,r.stdout+r.stderr
with tempfile.TemporaryDirectory(prefix='renegade-plane-drc-') as td:
 t=Path(td)/src.name
 for ext in ['.kicad_pcb','.kicad_pro','.kicad_dru']:shutil.copy2(src.with_suffix(ext),t.with_suffix(ext))
 (Path(td)/'fp-lib-table').write_text((ROOT/'engineering/whole-amp/pcb-measured-r/boards/fp-lib-table').read_text().replace('${KIPRJMOD}',str(ROOT/'engineering/whole-amp/pcb-measured-r/boards')))
 pro=json.loads(t.with_suffix('.kicad_pro').read_text());settings=pro.setdefault('board',{}).setdefault('design_settings',{});sev=settings.setdefault('rule_severities',{});enabled=[k for k,x in sev.items() if x=='ignore'];exclusions=settings.get('drc_exclusions',[])
 for k in enabled:sev[k]='warning'
 settings['drc_exclusions']=[];t.with_suffix('.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
 run([CLI,'pcb','drc','--format','json','--severity-all','--all-track-errors','--refill-zones','-o',str(D/'reverb-candidate-drc.json'),str(t)])
for name,layers in [('reverb-bottom','B.Cu,Edge.Cuts'),('reverb-overlay','B.Cu,F.Cu,F.Silkscreen,Edge.Cuts')]:
 svg=D/(name+'.svg');run([CLI,'pcb','export','svg','--layers',layers,'--mode-single','--fit-page-to-board','--exclude-drawing-sheet','-o',str(svg),str(src)]);svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n');run(['/usr/local/bin/rsvg-convert','-w','1600','-o',str(D/(name+'.png')),str(svg)])
assert all(sha(Path(p))==h for p,h in inputs.items())
report={'kicad_version':subprocess.check_output([CLI,'version'],text=True).strip(),'input_sha256':inputs,'target_sha256':sha(src),'inputs_unchanged':True,'re_enabled_ignored_checks':enabled,'removed_exclusions':exclusions,'output_sha256':{p.name:sha(p) for p in D.iterdir() if p.suffix in ['.svg','.png'] or p.name=='reverb-candidate-drc.json'},'commands':commands}
(D/'native-run.json').write_text(json.dumps(report,indent=2)+'\n');print('Native checks and final plots complete.')
