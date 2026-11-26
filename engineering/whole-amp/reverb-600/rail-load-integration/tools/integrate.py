"""Hash-guarded, narrow electrical checkpoint; preserve all unrelated CAD objects."""
from pathlib import Path
import copy,hashlib,json,sys,uuid
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3]
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'));import native_sexpr as n
sys.path.insert(0,str(M.parent/'interface-voltage/tools'));from correct_metadata import spans
Q=json.dumps

def emit(x):return '('+' '.join(emit(y) if isinstance(y,list) else y for y in x)+')'
def props(x):return {p[1].strip('"'):p for p in n.children(x,'property')}
def uid(tag):return Q(str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade-rail-load/'+tag)))
def reuid(x,tag):
 for i,y in enumerate(x):
  if isinstance(y,list):
   if y[0]=='uuid':y[1]=uid(tag+'/'+str(i))
   else:reuid(y,tag+'/'+str(i))
def move(x,dx,dy):
 for y in x:
  if isinstance(y,list):
   if y[0]=='at':y[1:3]=[str(round(float(y[1])+dx,6)),str(round(float(y[2])+dy,6))]
   else:move(y,dx,dy)
def property_set(obj,key,val):
 pr=props(obj)
 if key not in pr:
  p=copy.deepcopy(pr.get('Datasheet',pr['Value']));p[1]=Q(key);reuid(p,key);obj.append(p);pr[key]=p
 pr[key][2]=Q(val)
def append_objects(text,objects):
 at=text.rfind(')');return text[:at]+'\n'+'\n'.join(map(emit,objects))+'\n'+text[at:]
def wire(a,b,tag):return n.parse(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {uid(tag)}))')
def junction(x,y,tag):return n.parse(f'(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid {uid(tag)}))')
def main():
 assert sys.argv[1:]==['--apply']
 c=json.loads((M/'contract.json').read_text());changes={};fp=c['resistor_footprint'];rating='1% MF0207 metal film, 0.6W at70C derated to0W at155C; 350V max or sqrt(P*R), whichever lower'
 for path,h in c['native_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 # Circuit metadata and exact two new branches; existing signal nets untouched.
 for path in ['engineering/whole-amp/reverb-600/circuit.json','engineering/whole-amp/reverb-600/cad/design-connectivity.json']:
  d=json.loads((ROOT/path).read_text());r1=next(x for x in d['components'] if x['reference']=='R601')
  r1.update(footprint=fp,rating=rating,selected_mpn=c['R601_mpn'],datasheet=c['datasheet'],selection_evidence='engineering/whole-amp/reverb-600/rail-load-integration/review.md')
  for ref,row in c['loads'].items():
   assert not any(x['reference']==ref for x in d['components'])
   r=copy.deepcopy(r1);r.update(reference=ref,sheet='07c_reverb_output',value=row['value'],pins=row['pins'],selected_mpn=c['load_mpn'],source='VAL-063 rail-load correction',status='Native rail-load integration; full-system qualification pending');d['components'].append(r)
   if 'layout' in d:d['layout']['07c_reverb_output']['positions'][ref]=c['schematic_positions'][ref]
  changes[path]=json.dumps(d,indent=2)+'\n'
 # Preserve existing drawing, update only hidden exact R601 fields.
 path='engineering/whole-amp/reverb-600/cad/07a_reverb_send.kicad_sch';text=(ROOT/path).read_text()
 for a,b in spans(text,'symbol'):
  s=n.parse(text[a:b])
  if props(s)['Reference'][2]!='"R601"':continue
  for key,val in {'Footprint':fp,'Rating':rating,'Datasheet':c['datasheet'],'Part_status':'Exact MF0207 package integrated; system qualification pending'}.items():property_set(s,key,val)
  text=text[:a]+emit(s)+text[b:];break
 changes[path]=text
 path='engineering/whole-amp/reverb-600/cad/07c_reverb_output.kicad_sch';text=(ROOT/path).read_text();tree=n.parse(text)
 template=next(s for s in n.children(tree,'symbol') if props(s)['Reference'][2]=='"R612"')
 ground=next(s for s in n.children(tree,'symbol') if props(s)['Value'][2]=='"GND"')
 added=[];symbols={}
 for ref,row in c['loads'].items():
  s=copy.deepcopy(template);reuid(s,ref);at=n.field(s,'at');pos=c['schematic_positions'][ref];move(s,pos[0]-float(at[1]),pos[1]-float(at[2]))
  for key,val in {'Reference':ref,'Value':'10k','Footprint':fp,'Rating':rating,'Datasheet':c['datasheet'],'MPN':c['load_mpn'],'Supplier_SKU':c['load_sku'],'Part_source':'https://item.szlcsc.com/528499.html','Source':'VAL-063 rail-load correction','Part_status':'Exact package integrated; full-system validation pending'}.items():property_set(s,key,val)
  inst=n.field(n.field(n.field(s,'instances'),'project'),'path');n.field(inst,'reference')[1]=Q(ref)
  symbols[ref]=n.field(s,'uuid')[1].strip('"');added.append(s)
 # Local branches beside reservoir capacitors; avoid label-only fragments.
 for i,(a,b) in enumerate([((353.06,90.17),(365.76,90.17)),((365.76,90.17),(365.76,95.25)),((365.76,102.87),(365.76,115.57)),((403.86,90.17),(403.86,95.25)),((403.86,102.87),(403.86,107.95)),((403.86,107.95),(383.54,107.95))]):added.append(wire(a,b,'wire'+str(i)))
 for x,y,ref in [(365.76,115.57,'#PWR9901'),(403.86,90.17,'#PWR9902')]:
  s=copy.deepcopy(ground);reuid(s,ref);at=n.field(s,'at');move(s,x-float(at[1]),y-float(at[2]));property_set(s,'Reference',ref)
  n.field(n.field(n.field(n.field(s,'instances'),'project'),'path'),'reference')[1]=Q(ref);added.append(s)
 added += [junction(353.06,90.17,'jplus'),junction(383.54,107.95,'jminus')]
 added.append(n.parse(f'(text "R619/R620: defined rail loads, 1.5mA each at 15V.\\n[TBD-MEASURE] Complete supply and fault qualification." (at 355.6 125.73 0) (effects (font (size 1.15 1.15)) (justify left)) (uuid {uid("note")}))'))
 changes[path]=append_objects(text,added)
 # Native footprint replacement without whole-board serialization.
 path='engineering/whole-amp/pcb-measured-r/boards/Renegade_Reverb.kicad_pcb';text=(ROOT/path).read_text();tree=n.parse(text)
 library=n.parse((ROOT/'engineering/component-selection/footprints/Renegade_Selected.pretty/Yageo_MFR50S_MF0207_P10.16.kicad_mod').read_text())
 original=next(f for f in n.children(tree,'footprint') if props(f)['Reference'][2]=='"R601"')
 def make_fp(ref,value,pos,pins,sym):
  f=copy.deepcopy(library);f[1]=Q(fp);f[:]=[x for x in f if not(isinstance(x,list) and x[0] in ['version','generator','generator_version'])];reuid(f,ref)
  f.extend([['at',*map(str,pos)],['uuid',uid(ref+'/footprint')],['path',Q('/97ca3088-a174-52f9-956d-0a38bb8e2f56/'+('905ab7bf-c478-5283-9fbb-463e3e3d1d16' if ref=='R601' else '8fe72301-58ee-52c0-a750-925f875cec11')+'/'+sym)]])
  for key,val in {'Reference':ref,'Value':value,'Datasheet':c['datasheet'],'Selected_MPN':c['R601_mpn'] if ref=='R601' else c['load_mpn'],'Rating':rating}.items():property_set(f,key,val)
  if ref=='R620':n.field(props(f)['Reference'],'at')[1:]=['5.08','2.37','0']
  for p in n.children(f,'pad'):p.append(['net',Q(pins[p[1].strip('"')])])
  return f
 for a,b in spans(text,'footprint'):
  f=n.parse(text[a:b])
  if props(f)['Reference'][2]!='"R601"':continue
  replacement=make_fp('R601','1M',n.field(f,'at')[1:],{'1':'IN_AC','2':'SEND_IN'},'8a9cb995-466e-5c4e-afee-087da21a4bc5')
  # Retain instance/pad UUIDs and existing metadata; change only geometric primitives.
  geom={'fp_line','fp_rect','fp_text','pad','model'}
  f[1]=Q(fp);f[:]=[x for x in f if not(isinstance(x,list) and x[0] in geom)]
  for obj in replacement:
   if isinstance(obj,list) and obj[0] in geom:
    if obj[0]=='pad':
     old=next(p for p in n.children(original,'pad') if p[1]==obj[1]);n.field(obj,'uuid')[1]=n.field(old,'uuid')[1]
    f.append(obj)
  for key,val in {'Datasheet':c['datasheet'],'Selected_MPN':c['R601_mpn'],'Rating':rating}.items():property_set(f,key,val)
  text=text[:a]+emit(f)+text[b:];break
 new=[make_fp(ref,'10k',c['board_positions'][ref],row['pins'],symbols[ref]) for ref,row in c['loads'].items()]
 # Short local routes; 45-degree doglegs and same-net cap terminals.
 routes=[('+15V','F.Cu',[(125.5,5),(129.5,9),(131,9),(137,15)]),('GND','B.Cu',[(135.66,5),(129.5,5),(125.5,9)]),('GND','B.Cu',[(125.5,9),(129.5,13),(137.5,13),(139.5,15)]),('-15V','B.Cu',[(135.66,9),(142,9),(148,15)])]
 for i,(net,layer,points) in enumerate(routes):
  for j,(a,b) in enumerate(zip(points,points[1:])):new.append(n.parse(f'(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (width 0.3) (layer {Q(layer)}) (net {Q(net)}) (uuid {uid("track"+str(i)+"/"+str(j))}))'))
 for a,b in spans(text,'gr_text'):
  obj=n.parse(text[a:b])
  if obj[1]=='"+15 GND -15 +12 COIL"':
   obj[1]=Q('JR6: +15 GND -15 +12 COIL');n.field(obj,'at')[1:3]=['100','5'];text=text[:a]+emit(obj)+text[b:];break
 changes[path]=append_objects(text,new)
 for p,t in changes.items():
  if p.endswith(('.kicad_sch','.kicad_pcb')):n.parse(t)
  (ROOT/p).write_text(t)
 (M/'results/integration.json').write_text(json.dumps({'changed_paths':list(changes),'after_sha256':{p:hashlib.sha256(t.encode()).hexdigest() for p,t in changes.items()},'added_refs':list(c['loads']),'symbol_uuids':symbols,'full_amp_qualified':False},indent=2)+'\n')
 print('Applied two rail-load branches and R601 exact package metadata; verification required.')
if __name__=='__main__':main()
