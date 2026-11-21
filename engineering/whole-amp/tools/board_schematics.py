from pathlib import Path as _GuardPath
if (_GuardPath(__file__).resolve().parents[1]/'NATIVE_EDIT_GUARD').exists():
 raise RuntimeError('Saved native CAD is authoritative. Preserve it before intentionally regenerating this historical experiment.')
from pathlib import Path
import sys,json,copy,math
R=Path(__file__).resolve().parents[1];OLD=R.parent/'solid-state-reverb';sys.path.insert(0,str(R.parent/'updated-schematic/tools'))
from kicad_factory import *
data=json.loads((R/'board-plan.json').read_text())
for b in ['Main','Power','Control']:
 out=R/'pcb'/b;project='Renegade_'+b;rid=uid(project+'/root');f=Factory(out)
 original=parse((OLD/'libraries/Renegade_Draft.kicad_sym').read_text());f.symbols={s[1]:copy.deepcopy(s) for s in children(original,'symbol')};f.origin={s:'Preserved v0.4 symbol cache' for s in f.symbols}
 entries=[]
 for ref in data['boards'][b]['refs']:
  c=data['components'][ref]
  for un in c['units'] or [c]:
   entry=copy.deepcopy(un);entry.update({k:c[k] for k in ['value','footprint','symbol','datasheet','rating']});entry['pins']={n:c['pins'][n] for n in un['pins']};entries.append(entry)
 ports=json.loads((out/'placements.json').read_text())['ports']
 for p in ports:entries.append({'reference':p['reference'],'value':p['net'],'symbol':'Connector_Generic:Conn_01x01','unit':1,'pins':{'1':p['net']},'footprint':'Renegade_Whole:WirePad_1.3mm','rating':'Soldered and strain-relieved wire, voltage-rated sleeving','source':'Whole-assembly port map'})
 for i in range(1,5):entries.append({"reference":"H"+str(i),"value":"MountingHole_3.2mm_M3","symbol":"Mechanical:MountingHole","unit":1,"pins":{},"footprint":"MountingHole:MountingHole_3.2mm_M3","source":"M3 board fixing; chassis coordinates pending"})
 pages=[]
 for i in range(math.ceil(len(entries)/8)):
  name=f'{b.lower()}_{i+1:02}';sid=uid(project+'/sheet/'+name);s=Sheet(f,project,name,b+' board connectivity / '+str(i+1),i+2,rid,sid)
  s.text('PCB ASSEMBLY CONNECTIVITY v0.5 — DEVELOPMENT',18,15,1.5,True)
  for j,c in enumerate(entries[i*8:i*8+8]):
   x=50.8+(j%4)*101.6;y=63.5+(j//4)*114.3
   s.sym(c['symbol'],c['reference'],c['value'],x,y,c['pins'],unit=c.get('unit',1),source=c.get('source','v0.4 source circuit'),rating=c.get('rating',''),datasheet=c.get('datasheet',''))
  s.write(out);t=parse((out/(name+'.kicad_sch')).read_text())
  for sy in children(t,'symbol'):
   props={p[1]:p for p in children(sy,'property')};ref=props['Reference'][2];props['Footprint'][2]=next(c['footprint'] for c in entries if c['reference']==ref)
  (out/(name+'.kicad_sch')).write_text(serialize(t)+'\n');pages.append((name,sid))
 root=Sheet(f,project,'root',b+' PCB assembly',1,rid);root.id=rid;root.text('RENEGADE '+b.upper()+' BOARD — v0.5 DEVELOPMENT',20,20,2,True)
 root.text('Board pin mapping and harness terminals. See integrated amplifier schematic for signal flow.\nChassis valves, transformers, panel controls and socket-local protection parts remain explicit off-board items.\nNot released for fabrication: follow current engineering validation status.',20,35,1.25)
 for i,(name,sid) in enumerate(pages):
  x=20+(i%3)*130;y=70+(i//3)*45
  root.items.append(f'(sheet (at {x} {y}) (size 115 25) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1.1 1.1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+26.27} 0) (effects (font (size 1 1)) (justify left top))) (instances (project {q(project)} (path "/{rid}" (page "{i+2}")))))')
 if b=='Control':
  for i,n in enumerate(['GND','CTRL_RAW','NEG_RAW']):root.sym('power:PWR_FLAG','#FLG'+str(i+1),'PWR_FLAG',50.8+i*50.8,254,{'1':n},source='Rectifier output / center-tap return powered by isolated transformer T3')
 root.write(out);(out/'root.kicad_sch').rename(out/(project+'.kicad_sch'))
 f.save_library()
 (out/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "Renegade_Draft") (type "KiCad") (uri "${KIPRJMOD}/libraries/Renegade_Draft.kicad_sym") (options "") (descr "Project symbols")))\n')
 for path in out.glob("*.kicad_sch"):
  path.write_text(path.read_text().replace("DRAFT v0.2 | Named nets connect across sheets | Build-part models, ratings and fit review pending","DEVELOPMENT v0.5 | Assembly connectivity | Parts and fit review pending"))
 (out/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Renegade_Whole") (type "KiCad") (uri "${KIPRJMOD}/../../libraries/Renegade_Whole.pretty") (options "") (descr "Revisioned project footprints")))\n')
 print(b,len(entries),len(pages))
