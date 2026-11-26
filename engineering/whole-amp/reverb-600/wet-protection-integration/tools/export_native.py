from pathlib import Path
import subprocess,json,sys,hashlib
M=Path(__file__).resolve().parents[1];R=M.parents[3];D=M/'results';CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli';S=R/'engineering/whole-amp/reverb-600/cad/Renegade_220V_Reverb.kicad_sch';B=R/'engineering/whole-amp/pcb-measured-r/boards/Renegade_Reverb.kicad_pcb';phase=sys.argv[1];assert phase in ["before","after"]
# Refuse to relabel a changed design as the historical baseline.
c=json.loads((M/'contract.json').read_text());receipt=json.loads((D/'integration.json').read_text()) if phase=='after' else {}
for path,h in c['native_sha256'].items():
 expected=receipt.get('after_sha256',{}).get(path,h)
 assert hashlib.sha256((R/path).read_bytes()).hexdigest()==expected,path
commands=[]
for cmd in [[CLI,'sch','export','netlist','--format','kicadxml','-o',str(D/(phase+'.xml')),str(S)],[CLI,'sch','erc','--format','json','--severity-all','-o',str(D/(phase+'-erc.json')),str(S)],[CLI,'sch','export','pdf','-o',str(D/(phase+'.pdf')),str(S)],[CLI,'pcb','drc','--format','json','--severity-all','--all-track-errors','-o',str(D/(phase+'-drc.json')),str(B)]]:
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=120);commands.append(dict(command=cmd,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,commands[-1]
drill=D/('drill-'+phase);drill.mkdir(exist_ok=True)
(drill/'CONTEXT.md').write_text('# Generated drill witness\nOwner: Wet-protection integration check. Inputs: '+phase+' native PCB. Process: KiCad Excellon export. Outputs: drill coordinates compared by tools/check.py. Human check: four new diode holes and two resized PR01 holes; all unrelated drills remain unchanged. Not fabrication release.\n')
cmd=[CLI,'pcb','export','drill','--format','excellon','--excellon-units','mm','--output',str(drill)+'/',str(B)]
p=subprocess.run(cmd,capture_output=True,text=True,timeout=120);assert p.returncode==0,p.stderr
commands.append(dict(command=cmd,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
if phase=='after':
 cmd=[CLI,'pcb','export','svg','--layers','F.Cu,B.Cu,F.Silkscreen,F.Courtyard,Edge.Cuts','--output',str(D/'board.svg'),'--mode-single','--exclude-drawing-sheet',str(B)]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=120);assert p.returncode==0,p.stderr
 commands.append(dict(command=cmd,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
 svg=D/'board.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
(D/(phase+'-commands.json')).write_text(json.dumps(commands,indent=2)+'\n');print(phase,'native exports complete')
