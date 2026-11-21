"""Export standalone PCB schematic from the canonical integrated circuit."""
from pathlib import Path
import sys,json,copy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parent/'updated-schematic/tools'))
from kicad_factory import *
OUT=ROOT/'pcb';project='Renegade_Reverb';rid=uid(project+'/root');f=Factory(OUT);s=Sheet(f,project,'root','Renegade spring reverb PCB',1,rid);s.id=rid
s.text('RENEGADE SPRING REVERB PCB v0.4',20,25,2,True)
s.text('45 fitted components; isolated low-voltage +/-15V audio, +12V relay.\nPanel pot and real tank connect via harnesses; see integrated schematic.\nNo mains, heater or B+ copper on this PCB. Fit and component procurement gates remain.',20,40,1.3)
for i,name in enumerate(['07a_reverb_send','07b_reverb_recovery','07c_reverb_output']):
 p=ROOT/(name+'.kicad_sch');t=parse(p.read_text());sid=uid('Renegade_220V_Reverb/sheet/'+name)
 for sym in children(t,'symbol'):
  inst=child(sym,'instances');pr=child(inst,'project');pr[1]=project
  for pa in children(pr,'path'):pa[1]='/'+rid+'/'+sid
 child(t,'uuid')[1]=uid(project+'/'+name)
 (OUT/(name+'.kicad_sch')).write_text(serialize(t)+'\n')
 x=25+i*125;y=90
 s.items.append(f'(sheet (at {x} {y}) (size 110 30) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1.1 1.1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+31.27} 0) (effects (font (size 1 1)) (justify left top))) (instances (project {q(project)} (path "/{rid}" (page "{i+2}")))))')
for i,n in enumerate(['+15V','-15V','GND','+12V']):s.sym('power:PWR_FLAG','#FLG'+str(900+i),'PWR_FLAG',50+i*90,160,{'1':n},source='External isolated supply via JR6')
for i in range(4):s.sym('Mechanical:MountingHole','H'+str(i+1),'MountingHole_3.2mm_M3',50+i*90,210,{},source='Board mounting, insulated standoffs')
s.write(OUT);t=parse((OUT/'root.kicad_sch').read_text())
for sym in children(t,'symbol'):
 ps={p[1]:p for p in children(sym,'property')}
 if ps['Reference'][2].startswith('H'):ps['Footprint'][2]='MountingHole:MountingHole_3.2mm_M3'
for tx in children(t,'text'):tx[1]=tx[1].replace('DRAFT v0.2','ENGINEERING v0.4')
child(child(t,'title_block'),'rev')[1]='0.4';child(child(t,'title_block'),'date')[1]='2026-11-11'
(OUT/(project+'.kicad_sch')).write_text(serialize(t)+'\n');(OUT/'root.kicad_sch').unlink()
(OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Renegade_Draft") (type "KiCad") (uri "${KIPRJMOD}/../libraries/Renegade_Draft.kicad_sym") (options "") (descr "Portable project symbols")))\n')
# Include root-only stock symbols in canonical library; embedded caches also present.
libpath=ROOT/'libraries/Renegade_Draft.kicad_sym';t=parse(libpath.read_text());existing={x[1] for x in children(t,'symbol')}
for name,sym in f.symbols.items():
 if name not in existing:t.append(sym)
libpath.write_text(serialize(t)+'\n')
print('Standalone reverb PCB schematic exported')
