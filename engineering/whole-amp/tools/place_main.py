from pathlib import Path as _GuardPath
if (_GuardPath(__file__).resolve().parents[1]/'NATIVE_EDIT_GUARD').exists():
 raise RuntimeError('Saved native CAD is authoritative. Preserve it before intentionally regenerating this historical experiment.')
"""Experimental functional placement; keeps source references and nets intact."""
from pathlib import Path
import pcbnew as p,json,random,math,shutil,sys
R=Path(__file__).resolve().parents[1];path=R/'pcb/Main/Renegade_Main.kicad_pcb';shutil.copy2(path,path.with_suffix('.shelf-placement.kicad_pcb'))
import re
raw=re.sub(r'\n\t\((?:segment|via|arc)\n.*?\n\t\)', '', path.read_text(), flags=re.S);temp=path.with_suffix('.placement-temp.kicad_pcb');temp.write_text(raw);b=p.LoadBoard(str(temp))
data=json.loads((R/'board-plan.json').read_text());parts={f.GetReference():f for f in b.GetFootprints()};refs=data['boards']['Main']['refs']
# Fixed placement regions keep clean, dirty and phase/output sections distinct.
groups=[['R4','R2','R3','C1','R5','C2','C3','C4','R6','R7','R8','C5','C6','R43'],['R12','R10','R11','C7','C8','R13','C9','R14','R15','R16','C10','C11','R18','R19','R21','R20','C14','R22','R23','C15','C16','C17','R1','K1','K2'],['R24','C19','R25','R29','R30','C22','R26','R28','R27','C20','R31','R32','C21','C23','C24','R33','R34']]
# 8 columns / 7 rows, 34mm x 16mm. Every body checked against available slot.
slots=[(26+34*x,24+16*y) for x in range(8) for y in range(7)]
order=sum(groups,[]);assert set(order)==set(refs) and len(order)==len(slots)
netparts={}
for ref in refs:
 for n in data['components'][ref]['pins'].values():
  if n and n not in ['GND','B_PRE','B_EARLY','+12V','COIL_CH']:netparts.setdefault(n,set()).add(ref)
assign=dict(zip(order,slots));random.seed(617)
def cost(a):
 val=0
 for n,rs in netparts.items():
  xs=[a[r][0] for r in rs];ys=[a[r][1] for r in rs]
  val+=max(xs)-min(xs)+max(ys)-min(ys)
 return val
score=cost(assign)
# Local swaps within each functional region reduce wiring span, without crossing regions.
for k in range(30000):
 g=random.choice(groups);a,z=random.sample(g,2);assign[a],assign[z]=assign[z],assign[a];v=cost(assign);temp=15*(1-k/30000)+.01
 if v<score or random.random()<math.exp(min(0,(score-v)/temp)):score=v
 else:assign[a],assign[z]=assign[z],assign[a]
for ref,xy in assign.items():
 f=parts[ref]
 if ref in ['K1','K2']:f.SetOrientationDegrees(90)
 bb=f.GetBoundingBox(False,False);cx=bb.GetX()+bb.GetWidth()//2;cy=bb.GetY()+bb.GetHeight()//2
 assert p.ToMM(bb.GetWidth())<34 and p.ToMM(bb.GetHeight())<16,(ref,p.ToMM(bb.GetWidth()),p.ToMM(bb.GetHeight()))
 q=f.GetPosition();f.SetPosition(p.VECTOR2I(q.x+p.FromMM(xy[0])-cx,q.y+p.FromMM(xy[1])-cy))
p.SaveBoard(str(path),b);(path.parent/'functional-placement.json').write_text(json.dumps({'xy':assign,'wire_span_cost':score,'status':'experimental; no fabrication release'},indent=2));print('cost',score)
