"""Export before/candidate witnesses without modifying CAD."""
import subprocess,sys,json
from pathlib import Path
from prepare import M,ROOT,sha
phase=sys.argv[1];assert phase in ['before','after']
workspace=ROOT if phase=='before' else Path(sys.argv[2])
c=json.loads((M/'contract.json').read_text());expected=c['input_sha256'] if phase=='before' else json.loads((workspace/'receipt.json').read_text())['after_sha256']
for p,h in expected.items():assert sha(workspace/p)==h,p
out=M/'results'/phase;out.mkdir(exist_ok=True)
(out/'CONTEXT.md').write_text('# Native '+phase+' rectifier witness\nOwner: PCB integration. Inputs: guarded native source. Process: ../.. tools/export_native.py. Outputs: netlist, ERC, drawing, drill and DRC. Human check: inspect diodes, cathode mapping, 8 enlarged holes and 8 relocated parts; unrelated objects must match. Not a release.\n')
cli='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli';s=workspace/'engineering/whole-amp/reverb-600/cad/Renegade_220V_Reverb.kicad_sch';b=workspace/'engineering/whole-amp/pcb-measured-r/boards/Renegade_Power.kicad_pcb'
commands=[['sch','export','netlist','--format','kicadxml','-o',str(out/'netlist.xml'),str(s)],['sch','erc','--format','json','--severity-all','-o',str(out/'erc.json'),str(s)],['sch','export','pdf','-o',str(out/'schematics.pdf'),str(s)],['pcb','drc','--format','json','--severity-all','--all-track-errors','-o',str(out/'drc.json'),str(b)],['pcb','export','drill','--format','excellon','--excellon-units','mm','--output',str(out)+'/',str(b)],['pcb','export','svg','--layers','F.Cu,B.Cu,F.Silkscreen,F.Courtyard,Edge.Cuts','--output',str(out/'board.svg'),'--mode-single','--exclude-drawing-sheet',str(b)]]
receipts=[]
for args in commands:
 r=subprocess.run([cli,*args],capture_output=True,text=True,timeout=120);receipts.append({'args':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,receipts[-1]
(out/'commands.json').write_text(json.dumps(receipts,indent=2)+'\n');print(phase,'exports complete')
