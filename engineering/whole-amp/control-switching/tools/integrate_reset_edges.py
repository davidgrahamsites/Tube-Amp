"""Guarded electrical repair: use U1C/D to condition reset, preserving other blocks."""
import copy, hashlib, json, subprocess, sys, uuid
from pathlib import Path
M=Path(__file__).resolve().parents[1]; ROOT=M.parents[2]
sys.path.insert(0,str(M.parent/'tools')); import native_sexpr as v
from integrate_drivers import spans, emit, prop
Q=json.dumps
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade/reset-edge/2026-11-24/'+s))
CIR='engineering/whole-amp/reverb-600/circuit.json'
LATCH='engineering/whole-amp/reverb-600/cad/09b_latches_drivers.kicad_sch'
POWER='engineering/whole-amp/reverb-600/cad/10_logic_power.kicad_sch'
PCB='engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb'
def ref(x):return prop(x,'Reference')[2].strip('"')
def wire(p,q):
 return v.parse(f'(wire (pts (xy {p[0]} {p[1]}) (xy {q[0]} {q[1]})) (stroke (width 0) (type default)) (uuid {uid(str(p)+str(q))}))')
def label(name,x,y,global_=False):
 kind='global_label' if global_ else 'label'
 shape='(shape passive)' if global_ else ''
 return v.parse(f'({kind} {Q(name)} {shape} (at {x} {y} 0) (effects (font (size 1.15 1.15)) (justify left bottom)) (uuid {uid(name)}))')
def main():
 assert sys.argv[1:]==['--apply'] and not (M/'results/edge-integration.json').exists()
 contract=json.loads((M/'edge-contract.json').read_text());base=contract['baseline_commit']
 paths=[CIR,LATCH,POWER,PCB]; old={p:(ROOT/p).read_text() for p in paths}
 for p,t in old.items():assert t==subprocess.check_output(['/usr/bin/git','show',base+':'+p],cwd=ROOT).decode(),p
 circuit=json.loads(old[CIR]); latch=v.parse(old[LATCH]); power=v.parse(old[POWER]); board=v.parse(old[PCB])
 # Apply only declared circuit pin changes, keeping the two gates in the controller block.
 for c in circuit['components']:
  for pin in c['pins']:
   key=c['reference']+'.'+pin
   if key in contract['pin_changes']:
    before,after=contract['pin_changes'][key];assert c['pins'][pin]==before
    c['pins'][pin]=after
  if c['reference']=='U1' and c['unit'] in [3,4]:c['sheet']='09b_latches_drivers'
 # Move existing physical units, retaining their UUIDs. Do not regenerate other sheets.
 moved=[s for s in v.children(power,'symbol') if ref(s)=='U1' and v.field(s,'unit')[1] in ['3','4']]
 assert len(moved)==2
 remove_ids={v.field(s,'uuid')[1] for s in moved}
 for s in v.children(power,'symbol'):
  if ref(s) in ['#PWR1401','#PWR1403']:remove_ids.add(v.field(s,'uuid')[1])
 for x in power[1:]:
  if not isinstance(x,list):continue
  if x[0]=='wire' and v.field(x,'pts')[1:] in [[['xy','57.15','80.01'],['xy','62.23','80.01']],[['xy','137.16','80.01'],['xy','142.24','80.01']]]:remove_ids.add(v.field(x,'uuid')[1])
  if x[0]=='no_connect' and v.field(x,'at')[1:] in [['77.47','80.01'],['157.48','80.01']]:remove_ids.add(v.field(x,'uuid')[1])
 assert len(remove_ids)==8
 def uidfield(x):return v.field(x,'uuid')[1] if isinstance(x,list) and v.children(x,'uuid') else None
 power=[x for x in power if uidfield(x) not in remove_ids]
 for x in v.children(power,'text'):
  x[1]=x[1].replace('LOGIC PACKAGE POWER AND UNUSED GATES','LOGIC PACKAGE POWER AND REMAINING UNUSED GATES').replace('Unused HC14 inputs','U1E/F inputs')
 lib=copy.deepcopy(next(x for x in v.children(v.field(power,'lib_symbols'),'symbol') if x[1]=='"Renegade_Draft:74xx_74HC14"'))
 v.field(latch,'lib_symbols').append(lib)
 for s,x in zip(moved,[359.41,400.05]):
  ox,oy=map(float,v.field(s,'at')[1:3]);dx=x-ox;dy=304.8-oy
  v.field(s,'at')[1:3]=[str(x),'304.8']
  for p in v.children(s,'property'):
   a=v.field(p,'at');a[1:3]=[str(round(float(a[1])+dx,6)),str(round(float(a[2])+dy,6))]
  path=v.field(v.field(v.field(s,'instances'),'project'),'path')
  path[1]='"/97ca3088-a174-52f9-956d-0a38bb8e2f56/0774e6be-6282-5572-be57-238f3edfef89"'
  latch.append(s)
 # Separate raw supervisor net from the existing long reset bus at its lower end.
 remove_pairs=[[(309.88,304.8),(314.96,304.8)],[(314.96,288.29),(314.96,304.8)],[(314.96,288.29),(340.36,288.29)],[(340.36,283.21),(340.36,288.29)]]
 removed=[]
 for w in v.children(latch,'wire'):
  if [tuple(map(float,p[1:])) for p in v.field(w,'pts')[1:]] in remove_pairs:removed.append(w)
 assert len(removed)==4
 latch=[x for x in latch if x not in removed and not (isinstance(x,list) and x[0]=='junction' and v.field(x,'at')[1:]==['314.96','288.29'])]
 for p,q in [((309.88,304.8),(340.36,304.8)),((340.36,304.8),(351.79,304.8)),((340.36,283.21),(340.36,304.8)),((367.03,304.8),(392.43,304.8)),((407.67,304.8),(417.83,304.8))]:latch.append(wire(p,q))
 latch.extend([label('RESET_N',314.96,288.29,True),label('RESET_N',417.83,304.8,True),label('RESET_RAW_N',321.31,304.8,True),label('RESET_INV',378.46,304.8,True)])
 # UUIDs must be unique even for labels sharing one net.
 v.field(latch[-4],'uuid')[1]=uid('RESET_N_bus')
 latch.append(v.parse(f'(junction (at 340.36 304.8) (diameter 0) (color 0 0 0 0) (uuid {uid("raw-junction")}))'))
 for x in v.children(latch,'text'):
  if 'U3 reset replacement' in x[1]:
   x[1]=Q('U1C/D: clean reset edges; preserve active-low polarity.\n[TARGET] Each output load <=50pF, including sockets/traces.\n[TBD-MEASURE] Brownout, power-up and switch coincidence.\nU3 threshold/carrier still PENDING; see edge-review.md.')
   v.field(x,'at')[1:3]=['350','335']
 # Board pad identities follow the same declared pin map. No existing copper on
 # RESET_N or the two formerly NC outputs; ground escapes must be reviewed by DRC.
 fps=v.fps(board)
 for key,(before,after) in contract['pin_changes'].items():
  r,pin=key.split('.');p=next(x for x in v.children(fps[r],'pad') if x[1]==Q(pin));n=v.field(p,'net')
  assert n[1]==Q(before) if before is not None else n[1].startswith('"unconnected-')
  n[1]=Q(after)
 # Replace only changed top-level objects; unaffected bytes remain unchanged.
 def patch_top(text,a):
  original=v.parse(text);orig={uidfield(x):x for x in original[1:] if uidfield(x)};now={uidfield(x):x for x in a[1:] if uidfield(x)}
  edits=[]
  kinds={x[0] for x in original[1:] if isinstance(x,list)}
  for kind in kinds:
   for start,end in spans(text,kind):
    x=v.parse(text[start:end]);i=uidfield(x)
    if i and i not in now:edits.append((start,end,''))
    elif i and x!=now[i]:edits.append((start,end,emit(now[i])))
    elif kind=='lib_symbols' and x!=v.field(a,kind):edits.append((start,end,emit(v.field(a,kind))))
  for start,end,t in sorted(edits,reverse=True):text=text[:start]+t+text[end:]
  new=[x for x in a[1:] if uidfield(x) and uidfield(x) not in orig]
  return text.rstrip()[:-1]+' '+' '.join(emit(x) for x in new)+')\n'
 changes={CIR:json.dumps(circuit,indent=2)+'\n',LATCH:patch_top(old[LATCH],latch),POWER:patch_top(old[POWER],power),PCB:patch_top(old[PCB],board)}
 for p,t in changes.items():
  if p!=CIR:v.parse(t)
  (ROOT/p).write_text(t)
 (M/'results/edge-integration.json').write_text(json.dumps(dict(baseline_commit=base,pin_changes=contract['pin_changes'],before_sha256={p:hashlib.sha256(t.encode()).hexdigest() for p,t in old.items()},after_sha256={p:hashlib.sha256(t.encode()).hexdigest() for p,t in changes.items()},routing_complete=False,fabrication_ready=False),indent=2)+'\n')
 print('Integrated reset edge topology; native export/DRC and routing checks required.')
if __name__=='__main__':main()
