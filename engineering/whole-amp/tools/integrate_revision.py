from pathlib import Path as _GuardPath
if (_GuardPath(__file__).resolve().parents[1]/'NATIVE_EDIT_GUARD').exists():
 raise RuntimeError('Saved native CAD is authoritative. Preserve it before intentionally regenerating this historical experiment.')
"""Create a separate v0.5 integrated development schematic; preserve v0.4."""
from pathlib import Path
import sys,shutil,json,copy,csv
R=Path(__file__).resolve().parents[1];OLD=R.parent/'solid-state-reverb';D=R/'integrated';D.mkdir(exist_ok=True);sys.path.insert(0,str(R.parent/'updated-schematic/tools'))
from kicad_factory import parse,serialize,children,child
plan=json.loads((R/'board-plan.json').read_text());shutil.copytree(OLD/'libraries',D/'libraries',dirs_exist_ok=True)
for n in ['Renegade_220V_Reverb.kicad_pro','sym-lib-table']:shutil.copy2(OLD/n,D/n)
lib=parse((D/'libraries/Renegade_Draft.kicad_sym').read_text());cap=copy.deepcopy(next(x for x in children(lib,'symbol') if x[1]=='Device_C'));cap[1]='Renegade_Draft:Device_C'
for source in OLD.glob('*.kicad_sch'):
 tree=parse(source.read_text())
 for s in children(tree,'symbol'):
  props={p[1]:p for p in children(s,'property')};ref=props['Reference'][2]
  if ref not in plan['components']:continue
  c=plan['components'][ref]
  for name,key in [('Value','value'),('Footprint','footprint'),('Rating','rating'),('Datasheet','datasheet')]:
   if name in props and key in c:props[name][2]=c[key]
  if ref in ['C12','C13','C25','C26','C10','C14']:
   child(s,'lib_id')[1]='Renegade_Draft:Device_C';symbols=child(tree,'lib_symbols')
   if not any(x[1]==cap[1] for x in children(symbols,'symbol')):symbols.append(copy.deepcopy(cap))
  if 'selected_part' in c:
   prop=copy.deepcopy(props['Rating']);prop[1]='Selected_part';prop[2]=c['selected_part'];s.append(prop)
  prop=copy.deepcopy(props['Rating']);prop[1]='Assembly';prop[2]=c.get('assembly','Chassis / socket / panel');s.append(prop)
 text=serialize(tree).replace('v0.4 engineering package','v0.5 development package').replace('DRAFT v0.4','DRAFT v0.5').replace('PCB: isolated low-voltage spring reverb module. Original tube stages remain chassis/turret wired.','PCB assemblies: Main, Power, Control and Reverb. Valves, socket-local protection, magnetics and panel parts are chassis mounted.')
 (D/source.name).write_text(text+'\n')
(D/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Renegade_Whole") (type "KiCad") (uri "${KIPRJMOD}/../libraries/Renegade_Whole.pretty") (options "") (descr "Development footprints")))\n')
with (R/'bom-development.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Reference','Quantity','Value','Assembly','Selected part or candidate','Rating','Footprint','Status'])
 for ref,c in plan['components'].items():w.writerow([ref,0 if ref=='R100' else 1,c['value'],c.get('assembly','Chassis / socket / panel'),c.get('selected_part','UNRESOLVED exact purchase part; see v0.4 BOM'),c.get('rating',''),c.get('footprint',''),'Development; selection/fit/release review pending'])
 for name in ['Main','Power','Control']:
  for row in json.loads((R/'pcb'/name/'placements.json').read_text())['ports']:w.writerow([name+':'+row['reference'],1,row['net'],name,'Bare PCB wire termination; no separate connector','Wire insulation and strain relief require harness review','Renegade_Whole:WirePad_1.3mm','Development'])
  w.writerow([name+':H1-H4',4,'M3 mounting hole',name,'Chassis standoff/fastener stack pending','NPTH 3.2mm','MountingHole:MountingHole_3.2mm_M3','Development'])
print('Integrated schematic and assembly BOM created')
