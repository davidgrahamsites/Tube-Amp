from pathlib import Path as _GuardPath
if (_GuardPath(__file__).resolve().parents[1]/'NATIVE_EDIT_GUARD').exists():
 raise RuntimeError('Saved native CAD is authoritative. Preserve it before intentionally regenerating this historical experiment.')
from pathlib import Path
import pcbnew as p,json,random,math,shutil,re,functools
R=Path(__file__).resolve().parents[1];path=R/'pcb/Power/Renegade_Power.kicad_pcb';shutil.copy2(path,path.with_suffix('.shelf-placement.kicad_pcb'));raw=re.sub(r'\n\t\((?:segment|via|arc)\n.*?\n\t\)', '', path.read_text(), flags=re.S);temp=path.with_suffix('.placement-temp.kicad_pcb');temp.write_text(raw);b=p.LoadBoard(str(temp));parts={f.GetReference():f for f in b.GetFootprints()};data=json.loads((R/'board-plan.json').read_text());refs=data['boards']['Power']['refs']
for ref in ['C13','D6']:
 f=parts[ref];bb=f.GetBoundingBox(False,False);cx=bb.GetX()+bb.GetWidth()//2;cy=bb.GetY()+bb.GetHeight()//2;f.Rotate(p.VECTOR2I(cx,cy),p.EDA_ANGLE(180,p.DEGREES_T))
fixed=['C26','C25','C13','C12','C29','C30'];small=[r for r in refs if r not in fixed];slots=[(22+28*x,95+15*y) for x in range(5) for y in range(5) if not(x<2 and y<2)];assert len(slots)==len(small)
a=dict(zip(small,slots));a.update({'C29':(22,102.5),'C30':(50,102.5)})
for r in fixed[:4]:
 bb=parts[r].GetBoundingBox(False,False);a[r]=(p.ToMM(bb.GetX()+bb.GetWidth()//2),p.ToMM(bb.GetY()+bb.GetHeight()//2))
netparts={}
for r in refs:
 for n in data['components'][r]['pins'].values():
  if n and n!='GND':netparts.setdefault(n,set()).add(r)
def cost():
 v=0
 for rs in netparts.values():
  xs=[a[r][0] for r in rs];ys=[a[r][1] for r in rs];v+=max(xs)-min(xs)+max(ys)-min(ys)
 return v
random.seed(331);score=cost()
for k in range(30000):
 x,z=random.sample(small,2);a[x],a[z]=a[z],a[x];v=cost();temp=12*(1-k/30000)+.01
 if v<score or random.random()<math.exp(min(0,(score-v)/temp)):score=v
 else:a[x],a[z]=a[z],a[x]
for r in small+fixed[4:]:
 f=parts[r];bb=f.GetBoundingBox(False,False);q=f.GetPosition();cx=bb.GetX()+bb.GetWidth()//2;cy=bb.GetY()+bb.GetHeight()//2;xy=a[r];f.SetPosition(p.VECTOR2I(q.x+p.FromMM(xy[0])-cx,q.y+p.FromMM(xy[1])-cy))
ports=[q for q in parts.values() if q.GetReference().startswith('JP')];spots=[(10+28*x,y) for x in range(6) for y in [8,167]];targets=[]
for f in ports:
 net=next(iter(f.Pads())).GetNetname();ps=[pad.GetPosition() for r in refs for pad in parts[r].Pads() if pad.GetNetname()==net];targets.append((sum(p.ToMM(q.x) for q in ps)/len(ps),sum(p.ToMM(q.y) for q in ps)/len(ps)))
@functools.lru_cache(None)
def solve(i,mask):
 if i==len(ports):return (0,())
 best=(float('inf'),())
 for j,xy in enumerate(spots):
  if mask>>j&1:continue
  c,seq=solve(i+1,mask|1<<j);c+=abs(targets[i][0]-xy[0])+abs(targets[i][1]-xy[1])
  if c<best[0]:best=(c,(j,)+seq)
 return best
for f,j in zip(ports,solve(0,0)[1]):
 x,y=spots[j];f.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));f.Reference().SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y+(-3.3 if y==8 else 3.3))))
p.SaveBoard(str(path),b);(path.parent/'functional-placement.json').write_text(json.dumps({'xy':a,'wire_span_cost':score,'status':'experimental; no fabrication release'},indent=2));print('cost',score)
