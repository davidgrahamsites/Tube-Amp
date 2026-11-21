"""Native KiCad schematic factory. Explicit net maps are in build_design.py.
Generated files must be checked with the installed KiCad CLI before use.
"""
import copy, json, math, re, uuid
from pathlib import Path
LIBROOT=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols')
NS=uuid.UUID('5912f64f-b0fa-47b9-8842-85d81fd1bdfa')
def uid(s):return str(uuid.uuid5(NS,s))
def q(s):return json.dumps(str(s),ensure_ascii=False)
def parse(s):
 t=re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s);i=0
 def read():
  nonlocal i
  v=t[i];i+=1
  if v=='(':
   out=[]
   while t[i]!=')':out.append(read())
   i+=1;return out
  return json.loads(v) if v.startswith('"') else v
 return read()
def emit(x):
 if isinstance(x,list):return '('+' '.join(emit(v) for v in x)+')'
 # Quote string atoms conservatively; KiCad accepts quoted identifiers/keywords? No.
 return q(x) if not re.fullmatch(r'[A-Za-z0-9_+.#/:?~{}$=-]+',str(x)) else str(x)
def serialize(x):
 # S-expression needs explicit quoting for symbol names/property text, including numeric pin IDs.
 if isinstance(x,list):
  key=x[0] if x else ''
  quote_indices={'symbol':{1},'property':{1,2},'lib_id':{1},'name':{1},'number':{1},'extends':{1},'ki_fp_filters':{1},'text':{1},'paper':{1},'title':{1},'rev':{1},'date':{1},'comment':{2},'project':{1},'path':{1},'reference':{1},'global_label':{1},'label':{1},'pin':{1},'generator':{1},'page':{1}}.get(key,set())
  if key=='pin' and len(x)>2 and not isinstance(x[2],list):quote_indices=set()
  return '('+' '.join(q(v) if j in quote_indices and not isinstance(v,list) else serialize(v) for j,v in enumerate(x))+')'
 return str(x)
def children(x,k):return [v for v in x if isinstance(v,list) and v and v[0]==k]
def child(x,k):return next((v for v in x if isinstance(v,list) and v and v[0]==k),None)
_cache={}
def library(lib):
 if lib not in _cache:_cache[lib]={s[1]:s for s in children(parse((LIBROOT/(lib+'.kicad_sym')).read_text()),'symbol')}
 return _cache[lib]
def resolved(lib,name):
 sym=copy.deepcopy(library(lib)[name]);ext=child(sym,'extends')
 if ext:
  parent=resolved(lib,ext[1]);props={v[1]:v for v in children(parent,'property')};props.update({v[1]:v for v in children(sym,'property')})
  parentname=parent[1]
  for sub in children(parent,'symbol'):sub[1]=name+sub[1][len(parentname):]
  sym=['symbol',name]+[v for v in parent[2:] if not (isinstance(v,list) and v[0]=='property')]+list(props.values())
 sym=[v for v in sym if not(isinstance(v,list) and v[0] in {'extends','embedded_fonts'})]
 return sym
class Factory:
 def __init__(self,out):self.out=Path(out);self.symbols={};self.origin={};self.records=[]
 def get(self,libid):
  name=libid.replace(':','_')
  if name not in self.symbols:
   lib,n=libid.split(':');s=resolved(lib,n);s[1]=name
   for sub in children(s,'symbol'):sub[1]=name+sub[1][len(n):]
   # Physical anodes/cathodes are passive terminals, not mutually exclusive logic outputs.
   if lib=='Valve':
    for sub in children(s,'symbol'):
     for pin in children(sub,'pin'):
      num=child(pin,'number')[1]
      if n in ('ECC81','ECC83') and num in ('1','3','6','8'):pin[1]='passive'
      if n=='EL34' and num in ('1','3','4','5','8'):
       if num=='8':child(pin,'name')[1]='K'
       if num in ('1','3','8'):pin[1]='passive'
   self.symbols[name]=s;self.origin[name]=libid+('; project-local electrode pin-type correction; EL34 pin8=K' if lib=='Valve' else '')
  return name
 def custom_box(self,name,pins,width=30):
  props=f'(property "Reference" "T" (at 0 20 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 17 0) (effects (font (size 1.27 1.27))))'
  ys=[p[2] for p in pins];h=max(8,max(abs(y) for y in ys)+2.54)
  geom=f'(symbol "{name}_0_1" (rectangle (start {-width/2} {h}) (end {width/2} {-h}) (stroke (width 0.254) (type default)) (fill (type background))))'
  pp=[]
  for number,label,y,side in pins:
   x=(-1 if side=='L' else 1)*(width/2+5.08);ang=0 if side=='L' else 180
   pp.append(f'(pin passive line (at {x} {y} {ang}) (length 5.08) (name {q(label)} (effects (font (size 1 1)))) (number {q(number)} (effects (font (size 1 1)))))')
  self.symbols[name]=parse(f'(symbol "{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board no) {props} {geom} (symbol "{name}_1_1" '+''.join(pp)+'))');self.origin[name]='Project logical terminals; supplier lead mapping pending'
  return name
 def pins(self,name,unit):
  out=[]
  for sub in children(self.symbols[name],'symbol'):
   match=re.search(r'_(\d+)_(\d+)$',sub[1])
   if match and int(match[1]) in (0,unit) and int(match[2]) in (0,1):out+=children(sub,'pin')
  return out
 def save_library(self):
  d=self.out/'libraries';d.mkdir(exist_ok=True)
  (d/'Renegade_Draft.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator renegade_factory)\n'+'\n'.join(serialize(s) for s in self.symbols.values())+'\n)\n')
  (d/'symbol-provenance.json').write_text(json.dumps(self.origin,indent=2)+'\n')
class Sheet:
 def __init__(self,f,project,name,title,page,rootid,sheetid=None):
  self.f=f;self.project=project;self.name=name;self.title=title;self.page=page;self.id=uid(project+'/'+name);self.path='/'+rootid+('/'+sheetid if sheetid else '');self.items=[];self.used=set();self.count=0
 def text(self,s,x,y,size=1.27,bold=False):self.items.append(f'(text {q(s)} (at {x} {y} 0) (effects (font (size {size} {size}) {"bold" if bold else ""}) (justify left top)) (uuid {uid(self.project+self.name+"text"+str(len(self.items)))}))')
 def sym(self,lib,ref,value,x,y,nets,unit=1,rot=0,source='',rating='',status='proposed',datasheet=''):
  name=lib if lib in self.f.symbols else self.f.get(lib);self.used.add(name);self.count+=1
  key=f'{self.project}/{self.name}/{ref}/{unit}';suid=uid(key)
  def prop(n,v,yy,hide=False):return f'(property {q(n)} {q(v)} (at {x+7.62} {yy} 0) (effects (font (size 1 1)) (justify left) {"hide" if hide else ""}))'
  custom=name in ('PowerTransformer_Logical','ControlTransformer_Logical','OutputTransformer_Logical','ReverbTransformer_Logical','SpringTank_Logical')
  shift=20.32 if custom else (8.89 if name=='Valve_EL34' else (10.16 if name.startswith(('74xx_','Power_Supervisor_','Regulator_Linear_','Connector_Audio_','Switch_')) else 6.35))
  props=prop('Reference',ref,y-shift)+prop('Value',value,y-shift+2.54)
  props+=prop('Footprint','',y,True)+prop('Datasheet',datasheet,y,True)+prop('Source',source,y,True)+prop('Rating',rating,y,True)+prop('Design_status',status,y,True)
  pins=self.f.pins(name,unit);present={child(p,'number')[1] for p in pins};assert set(nets)==present,(ref,unit,present,set(nets))
  parts=[];r=math.radians(rot)
  for p in pins:
   n=child(p,'number')[1];px,py,a=map(float,child(p,'at')[1:]);xx=x+px*math.cos(r)+py*math.sin(r);yy=y+px*math.sin(r)-py*math.cos(r)
   xx,yy=round(xx,4),round(yy,4);parts.append(f'(pin {q(n)} (uuid {uid(key+"/pin/"+n)}))')
   net=nets[n]
   if net is None:self.items.append(f'(no_connect (at {xx} {yy}) (uuid {uid(key+"/nc/"+n)}))');continue
   angle=(a-rot)%360;dx,dy={0:(-5.08,0),90:(0,5.08),180:(5.08,0),270:(0,-5.08)}[angle]
   if dy and abs(xx-x)<0.001:
    same_y=[pp for pp in pins if float(child(pp,'at')[2])==py]
    if len(same_y)>=3:dy*=2
   ex,ey=round(xx+dx,4),round(yy+dy,4);vertices=[(xx,yy),(ex,ey)]
   # Fan vertical pins outward; horizontal labels stay clear of bodies and each other.
   if dy:
    fan=-5.08 if xx<x else 5.08
    ex=round(ex+fan,4);vertices.append((ex,ey));ang=180 if fan<0 else 0
   else:ang=0 if dx>0 else 180
   just='right' if ang==180 else 'left';tx,ty=ex,ey
   for seg,(p1,p2) in enumerate(zip(vertices,vertices[1:])):
    self.items.append(f'(wire (pts (xy {p1[0]} {p1[1]}) (xy {p2[0]} {p2[1]})) (stroke (width 0) (type default)) (uuid {uid(key+"/wire/"+n+"/"+str(seg))}))')
   self.items.append(f'(global_label {q(net)} (shape passive) (at {tx} {ty} {ang}) (effects (font (size 0.95 0.95)) (justify {just})) (uuid {uid(key+"/label/"+n)}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {tx} {ty} {ang}) (effects (font (size 0.95 0.95)) hide)))')
  self.items.append(f'(symbol (lib_id "Renegade_Draft:{name}") (at {x} {y} {rot}) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid {suid}) {props} '+''.join(parts)+f'(instances (project {q(self.project)} (path {q(self.path)} (reference {q(ref)}) (unit {unit})))))')
  self.f.records.append({'project':self.project,'sheet':self.name,'reference':ref,'unit':unit,'value':value,'symbol':name,'pins':nets,'source':source,'rating':rating,'status':status,'datasheet':datasheet})
 def grid(self,lib,ref,val,nets,i,**kw):
  i-=getattr(self,'grid_offset',0)
  x=50.8+(i%5)*76.2;y=55.88+(i//5)*35.56;self.sym(lib,ref,val,x,y,nets,**kw)
 def write(self,dir):
  self.text('DRAFT v0.2 | Named nets connect across sheets | Build-part models, ratings and fit review pending',16,16,1.25,True)
  libs='\n'.join(serialize(['symbol','Renegade_Draft:'+n]+copy.deepcopy(self.f.symbols[n][2:])) for n in sorted(self.used))
  short={'root':'Renegade 220 V + spring reverb','01_clean':'Clean preamp','02_dirty':'Dirty gain stages','02b_dirty_tone':'Dirty follower and tone controls','03_routing':'Channels and effects loop','04_output':'Phase inverter and EL34 output','04b_output_transformer':'Output transformer and speaker taps','05_supplies':'Mains and high-voltage supply','05b_bias_reverb_supply':'Bias, heater reference and reverb rail','06_heaters':'Heaters, earth and chassis','07_reverb':'Tube spring reverb and mixer','08_control_supply':'Relay and logic power','09_controller':'Pedal inputs and debounce','09b_latches_drivers':'Latches, reset and relay drivers','10_logic_power':'Logic power and unused gates'}.get(self.name,self.title)
  s=f'(kicad_sch (version 20250114) (generator "renegade_factory") (uuid {self.id}) (paper "A3") (title_block (title {q(short)}) (date "2026-10-04") (rev "0.2-DRAFT") (comment 1 "Engineering draft - not a fabrication release")) (lib_symbols {libs})\n'+'\n'.join(self.items)+f'\n(sheet_instances (path "/" (page "{self.page}"))))\n'
  (Path(dir)/(self.name+'.kicad_sch')).write_text(s)
