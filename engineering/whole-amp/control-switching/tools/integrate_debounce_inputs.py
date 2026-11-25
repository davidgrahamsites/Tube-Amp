"""Bounded native debounce repair. Historical generators must not overwrite this delta."""
import copy, hashlib, json, sys, uuid
from pathlib import Path
from integrate_drivers import spans, emit, prop
M=Path(__file__).resolve().parents[1]; ROOT=M.parents[2]
sys.path.insert(0,str(M.parent/'tools')); import native_sexpr as v
Q=json.dumps
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade/debounce-input/2026-11-25/'+s))
CIR='engineering/whole-amp/reverb-600/circuit.json'
SCH='engineering/whole-amp/reverb-600/cad/09_controller.kicad_sch'
PCB='engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb'
FP='engineering/component-selection/footprints/Renegade_Selected.pretty/Yageo_RT0603_IPC_Nominal.kicad_mod'
LIB='Renegade_Selected:Yageo_RT0603_IPC_Nominal'
def identity(x):return v.field(x,'uuid')[1] if isinstance(x,list) and v.children(x,'uuid') else None
def patch(text,a):
 old=v.parse(text); before={identity(x):x for x in old[1:] if identity(x)}; after={identity(x):x for x in a[1:] if identity(x)}; edits=[]
 for kind in {x[0] for x in old[1:] if isinstance(x,list)}:
  for start,end in spans(text,kind):
   x=v.parse(text[start:end]); i=identity(x)
   if i and i not in after:edits.append((start,end,''))
   elif i and x!=after[i]:edits.append((start,end,emit(after[i])))
 for start,end,t in sorted(edits,reverse=True):text=text[:start]+t+text[end:]
 return text.rstrip()[:-1]+'\n'+'\n'.join(emit(x) for x in a[1:] if identity(x) and identity(x) not in before)+')\n'
def main():
 assert sys.argv[1:]==['--apply']
 dest=M/'results/debounce-input'; base=json.loads((dest/'baseline.json').read_text())
 for p in [CIR,SCH,PCB]: assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==base['sha256'][p],p
 old={p:(ROOT/p).read_text() for p in [CIR,SCH,PCB]}; c=json.loads(old[CIR]);a=v.parse(old[SCH]);b=v.parse(old[PCB])
 assert not any(x['reference'] in ['R304','R314'] for x in c['components'])
 template=next(x for x in v.children(a,'symbol') if prop(x,'Reference')[2]=='"R303"')
 fp=v.parse(Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod').read_text());fp[1]=Q('Yageo_RT0603_IPC_Nominal');prop(fp,'Value')[2]=Q('10k')
 # Retained IPC nominal pattern: 0.8 x 0.95 mm pads, 1.65 mm centre spacing.
 (ROOT/FP).write_text(emit(fp)+'\n')
 for ref,net,pin,y,px,py in [('R304','DB_CH','1',95.25,70.5,17.8),('R314','DB_REV','3',204.47,70.5,30.5)]:
  out=net+'_INPUT'; sym=copy.deepcopy(template)
  def fresh(x):
   for t in x:
    if isinstance(t,list):
     if t[0]=='uuid':t[1]=uid(ref+t[1])
     else:fresh(t)
  fresh(sym);v.field(sym,'at')[1:3]=['273.05',str(y)]
  for p in v.children(sym,'property'):v.field(p,'at')[1:3]=['273.05',str(y-10.16)]
  for name,value in [('Reference',ref),('Value','10k'),('Footprint',LIB),('Source','VAL-056 / LCSC C95204'),('Datasheet','https://yageogroup.com/content/datasheet/asset/file/pyu-rt_1-to-0-01_rohs_l'),('Rating','RT0603BRD0710KL; 0.1%, 25ppm/C, 0.1W at70C'),('Design_status','Integrated input current limiter; full power sequence pending')]:prop(sym,name)[2]=Q(value)
  v.field(prop(sym,'Value'),'at')[2]=str(y-7.62)
  v.field(v.field(v.field(v.field(sym,'instances'),'project'),'path'),'reference')[1]=Q(ref)
  a.append(sym)
  target=[['xy','250.19',str(y)],['xy','292.1',str(y)]]
  wires=[w for w in v.children(a,'wire') if v.field(w,'pts')[1:]==target];assert len(wires)==1;a.remove(wires[0])
  for i,(x1,x2) in enumerate([(250.19,269.24),(276.86,292.1)]):
   a.append(v.parse(f'(wire (pts (xy {x1} {y}) (xy {x2} {y})) (stroke (width 0) (type default)) (uuid {uid(ref+"wire"+str(i))}))'))
  a.append(v.parse(f'(label {Q(out)} (at 281.94 {y} 0) (effects (font (size 1.0 1.0)) (justify left bottom)) (uuid {uid(ref+"label")}))'))
  row=copy.deepcopy(next(x for x in c['components'] if x['reference']=='R303'));row.update(reference=ref,value='10k',pins={'1':net,'2':out},selected_mpn='RT0603BRD0710KL',footprint=LIB,source='VAL-056 / LCSC C95204',rating='0.1W at70C,0.1%,25ppm/C',status='engineering integrated; full power sequence pending',datasheet='https://yageogroup.com/content/datasheet/asset/file/pyu-rt_1-to-0-01_rohs_l');c['components'].append(row)
  unit=next(x for x in c['components'] if x['reference']=='U1' and pin in x['pins']);assert unit['pins'][pin]==net;unit['pins'][pin]=out
  p=next(x for x in v.children(v.fps(b)['U1'],'pad') if x[1]==Q(pin));assert v.field(p,'net')[1]==Q(net);v.field(p,'net')[1]=Q(out)
  f=copy.deepcopy(fp);f[1]=Q(LIB);f=[x for x in f if not isinstance(x,list) or x[0] not in ['version','generator']]
  f.extend([['at',str(px),str(py)],['uuid',Q(uid(ref+'fp'))],['path',Q('/97ca3088-a174-52f9-956d-0a38bb8e2f56/ec32d9d4-9b48-5b52-9c2f-397185e020d6/'+v.field(sym,'uuid')[1])]])
  prop(f,'Reference')[2]=Q(ref)
  for p,n in zip(v.children(f,'pad'),[net,out]):p.extend([['net',Q(n)],['uuid',Q(uid(ref+'pad'+p[1]))]])
  b.append(f)
  points=([(71.325,17.8),(72.3,17.8),(74.7597,20.2597),(74.7597,21.555)] if ref=='R304' else [(71.325,30.5),(73.8,28.025),(73.8,27.5947),(74.7597,26.635)])
  for i,(p,q) in enumerate(zip(points,points[1:])):
   b.append(v.parse(f'(segment (start {p[0]} {p[1]}) (end {q[0]} {q[1]}) (width 0.3) (layer "F.Cu") (net {Q(out)}) (uuid "{uid(ref+"track"+str(i))}"))'))
 a.append(v.parse(f'(text "R304/R314 limit charged-capacitor current into U1 on power-down.\\n[TARGET] Keep input-side traces short; full sequencing remains unqualified.\\nSee debounce-input-review.md (VAL-056)." (at 267 270 0) (effects (font (size 1.27 1.27)) (justify left top)) (uuid {uid("note")}))'))
 changes={CIR:json.dumps(c,indent=2)+'\n',SCH:patch(old[SCH],a),PCB:patch(old[PCB],b)}
 for p,t in changes.items():
  if p!=CIR:v.parse(t)
  (ROOT/p).write_text(t)
 (dest/'integration.json').write_text(json.dumps({'baseline_commit':base['commit'],'added_refs':['R304','R314'],'pin_changes':{'U1.1':['DB_CH','DB_CH_INPUT'],'U1.3':['DB_REV','DB_REV_INPUT']},'changed_paths':[CIR,SCH,PCB,FP],'after_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [CIR,SCH,PCB,FP]},'routing_complete':False,'fabrication_ready':False},indent=2)+'\n')
 print('Applied bounded two-input repair; native checks required.')
if __name__=='__main__':main()
