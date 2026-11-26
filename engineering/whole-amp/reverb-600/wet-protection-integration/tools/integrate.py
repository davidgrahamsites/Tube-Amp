"""Explicit four-part correction, hash-guarded and baseline-reproducible."""
from pathlib import Path
import copy,hashlib,json,sys,uuid
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3]
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools'));import native_sexpr as n
sys.path.insert(0,str(M.parent/'interface-voltage/tools'));from correct_metadata import spans
Q=json.dumps

def emit(x):return '('+' '.join(emit(y) if isinstance(y,list) else y for y in x)+')'
def props(x):return {p[1].strip('"'):p for p in n.children(x,'property')}
def uid(tag):return Q(str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade-wet-integration/'+tag)))
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
  p=copy.deepcopy(pr.get('Datasheet',pr['Value']));p[1]=Q(key);obj.append(p);pr[key]=p
 pr[key][2]=Q(val)
def append_objects(text,objects):
 at=text.rfind(')');return text[:at]+'\n'+'\n'.join(map(emit,objects))+'\n'+text[at:]
def wire(a,b,tag):return n.parse(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {uid(tag)}))')
def junction(x,y,tag):return n.parse(f'(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid {uid(tag)}))')
def patch(text,kind,fn):
 for a,b in reversed(list(spans(text,kind))):
  obj=n.parse(text[a:b]);replacement=fn(obj)
  if replacement is not None:text=text[:a]+(emit(replacement) if replacement else '')+text[b:]
 return text

def main():
 assert sys.argv[1:]==['--apply']
 c=json.loads((M/'contract.json').read_text());changes={};parts=c['parts']
 for path,h in c['native_sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 for path in ['engineering/whole-amp/reverb-600/circuit.json','engineering/whole-amp/reverb-600/cad/design-connectivity.json']:
  d=json.loads((ROOT/path).read_text())
  for r in ['R616','R618']:
   row=next(x for x in d['components'] if x['reference']==r);p=parts[r];assert row['pins']==p['pins']
   row.update(footprint=p['footprint'],rating=p['rating'],selected_mpn=p['mpn'],datasheet=p['datasheet'],selection_evidence=str(M.relative_to(ROOT)/'review.md'))
  base=next(x for x in d['components'] if x['reference']=='D601')
  for r in ['D603','D604']:
   p=parts[r];row=copy.deepcopy(base);row.update(reference=r,unit=1,sheet='07c_reverb_output',value=p['value'],symbol=p['symbol'].replace(':','_'),pins=p['pins'],footprint=p['footprint'],rating=p['rating'],selected_mpn=p['mpn'],datasheet=p['datasheet'],source='VAL-067 wet-contact correction',status='Native draft; application qualification pending',selection_evidence=str(M.relative_to(ROOT)/'review.md'))
   assert not any(x['reference']==r for x in d['components']);d['components'].append(row)
   if 'layout' in d:d['layout']['07c_reverb_output']['positions'][r]=p['schematic_at']
  changes[path]=json.dumps(d,indent=2)+'\n'
 path='engineering/whole-amp/reverb-600/cad/07c_reverb_output.kicad_sch';text=(ROOT/path).read_text();tree=n.parse(text)
 def metadata(s):
  r=props(s)['Reference'][2].strip('"')
  if r not in ['R616','R618']:return
  p=parts[r]
  for k,v in {'Footprint':p['footprint'],'Rating':p['rating'],'Datasheet':p['datasheet'],'MPN':p['mpn'],'Supplier_SKU':p['supplier_sku'],'Part_source':p['supplier_url'],'Price_stock_observed':p['observed'],'Part_status':'Exact package integrated; full-system qualification pending'}.items():property_set(s,k,v)
  return s
 text=patch(text,'symbol',metadata)
 # Add the standard KiCad zener library definition; pin 1 cathode, pin 2 anode.
 lib=n.parse(Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym').read_text());dz=copy.deepcopy(next(s for s in n.children(lib,'symbol') if s[1]=='"D_Zener"'));dz[1]='"Device:D_Zener"'
 for a,b in spans(text,'lib_symbols'):
  defs=n.parse(text[a:b]);assert not any(x[1]=='"Device:D_Zener"' for x in n.children(defs,'symbol'));defs.append(dz);text=text[:a]+emit(defs)+text[b:];break
 template=next(s for s in n.children(tree,'symbol') if props(s)['Reference'][2]=='"R612"');ground=next(s for s in n.children(tree,'symbol') if props(s)['Value'][2]=='"GND"')
 added=[];symbols={}
 for r in ['D603','D604']:
  p=parts[r];s=copy.deepcopy(template);reuid(s,r);at=n.field(s,'at');pos=p['schematic_at'];move(s,pos[0]-float(at[1]),pos[1]-float(at[2]));n.field(s,'at')[3]=str(pos[2]);n.field(s,'lib_id')[1]=Q(p['symbol'])
  for k,v in {'Reference':r,'Value':p['value'],'Footprint':p['footprint'],'Rating':p['rating'],'Datasheet':p['datasheet'],'MPN':p['mpn'],'Supplier_SKU':p['supplier_sku'],'Part_source':p['supplier_url'],'Price_stock_observed':p['observed'],'Source':'VAL-067 wet-contact correction','Part_status':'Exact package integrated; qualification pending'}.items():property_set(s,k,v)
  # Keep labels horizontal beside the vertical symbol.
  for k,dy in [('Reference',-1.27),('Value',1.27)]:n.field(props(s)[k],'at')[1:]=[str(pos[0]+3.81),str(pos[1]+dy),'90']
  if r=='D604':
   for k in ['Reference','Value']:n.field(n.field(props(s)[k],'effects'),'justify')[1]='right'
  n.field(n.field(n.field(n.field(s,'instances'),'project'),'path'),'reference')[1]=Q(r)
  symbols[r]=n.field(s,'uuid')[1].strip('"');added.append(s)
 # Connected branch at WET_AC; anodes meet midway, lower cathode grounded.
 target=[(266.7,90.17),(304.8,90.17)]
 def split(w):
  pts=[tuple(map(float,p[1:])) for p in n.field(w,'pts')[1:]]
  if pts==target:n.field(w,'pts')[2]=['xy','285.75','90.17'];return w
 text=patch(text,'wire',split)
 for i,(a,b) in enumerate([((285.75,90.17),(304.8,90.17)),((285.75,90.17),(285.75,95.25)),((285.75,102.87),(285.75,110.49)),((285.75,118.11),(285.75,123.19))]):added.append(wire(a,b,'wire'+str(i)))
 added.append(junction(285.75,90.17,'tap'))
 g=copy.deepcopy(ground);reuid(g,'ground');at=n.field(g,'at');move(g,285.75-float(at[1]),123.19-float(at[2]));property_set(g,'Reference','#PWR9910');n.field(n.field(n.field(n.field(g,'instances'),'project'),'path'),'reference')[1]=Q('#PWR9910');added.append(g)
 # Explicit net label names the internal common-anode node for source/PCB parity.
 added.append(n.parse(f'(label "WET_Z_JOIN" (at 285.75 106.68 0) (effects (font (size 1.0 1.0)) (justify left bottom)) (uuid {uid("joinlabel")}))'))
 added.append(n.parse(f'(text "D603/D604: opposing-series 27V clamps; common anodes.\\nR616: 100R, PR01 1W / 5%, pulse-rated (VAL-067).\\nR618: 1M / 350V MF0207. Contact-life test pending." (at 270.51 45.72 0) (effects (font (size 1.15 1.15)) (justify left top)) (uuid {uid("note")}))'))
 changes[path]=append_objects(text,added)
 path='engineering/whole-amp/pcb-measured-r/boards/Renegade_Reverb.kicad_pcb';text=(ROOT/path).read_text();old=n.parse(text)
 def make_fp(r,pos,sym=None):
  p=parts[r];f=n.parse((ROOT/'engineering/component-selection/footprints/Renegade_Selected.pretty'/(p['footprint'].split(':')[1]+'.kicad_mod')).read_text());f[1]=Q(p['footprint']);f[:]=[x for x in f if not(isinstance(x,list) and x[0] in ['version','generator','generator_version'])];reuid(f,r)
  f.extend([['at',*map(str,pos)],['uuid',uid(r+'/footprint')]])
  if sym:f.append(['path',Q('/97ca3088-a174-52f9-956d-0a38bb8e2f56/8fe72301-58ee-52c0-a750-925f875cec11/'+sym)])
  for k,v in {'Reference':r,'Value':p['value'],'Datasheet':p['datasheet'],'Selected_MPN':p['mpn'],'Rating':p['rating']}.items():property_set(f,k,v)
  for pad in n.children(f,'pad'):pad.append(['net',Q(p['pins'][pad[1].strip('"')])])
  return f
 def change_fp(f):
  r=props(f)['Reference'][2].strip('"')
  if r not in ['R616','R618']:return
  p=parts[r]
  if r=='R616':
   n.field(f,'at')[1:]=['128.46','60'];g=make_fp(r,n.field(f,'at')[1:]);geom={'fp_line','fp_rect','fp_text','pad','model'};oldpads={x[1]:x for x in n.children(f,'pad')}
   f[:]=[x for x in f if not(isinstance(x,list) and x[0] in geom)]
   for x in g:
    if isinstance(x,list) and x[0] in geom:
     if x[0]=='pad':n.field(x,'uuid')[1]=n.field(oldpads[x[1]],'uuid')[1]
     f.append(x)
  f[1]=Q(p['footprint'])
  for k,v in {'Datasheet':p['datasheet'],'Selected_MPN':p['mpn'],'Rating':p['rating']}.items():property_set(f,k,v)
  return f
 text=patch(text,'footprint',change_fp)
 # R616 pin 2 stays fixed; shorten the original pin-1 OUT_BUF stub.
 changed_tracks=[]
 def change_track(t):
  if n.field(t,'net')[1]=='"OUT_BUF"' and n.field(t,'start')[1:]==['131.0','60.0']:
   n.field(t,'start')[1:]=['128.46','60'];changed_tracks.append(n.field(t,'uuid')[1]);return t
 text=patch(text,'segment',change_track)
 new=[make_fp(r,parts[r]['board_at'],symbols[r]) for r in ['D603','D604']]
 routes=[('WET_AC','B.Cu',[(120.5,42.5),(124,39),(131,39),(132,38),(132,32)]),('WET_Z_JOIN','F.Cu',[(133.2,42.5),(133.2,46.5)]),('GND','B.Cu',[(120.5,46.5),(117,43),(117,34.32),(121.62,29.7)])]
 for i,(net,layer,points) in enumerate(routes):
  for j,(a,b) in enumerate(zip(points,points[1:])):new.append(n.parse(f'(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (width 0.4) (layer {Q(layer)}) (net {Q(net)}) (uuid {uid("track"+str(i)+"/"+str(j))}))'))
 changes[path]=append_objects(text,new)
 for p,t in changes.items():
  if p.endswith(('.kicad_sch','.kicad_pcb')):n.parse(t)
  (ROOT/p).write_text(t)
 (M/'results/integration.json').write_text(json.dumps({'changed_paths':list(changes),'after_sha256':{p:hashlib.sha256(t.encode()).hexdigest() for p,t in changes.items()},'added_refs':['D603','D604'],'symbol_uuids':symbols,'changed_track_uuids':changed_tracks,'full_amp_qualified':False},indent=2)+'\n')
 print('Applied local wet clamp and resistor package corrections; verification required.')
if __name__=='__main__':main()
