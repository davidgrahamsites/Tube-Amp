"""Conservative two-layer grid routing, verified by native DRC after execution.
All pads are actual loaded footprints; no inferred pad numbers.
"""
import pcbnew as pcb,math,json,heapq,time
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];path=ROOT/'pcb/Renegade_Reverb.kicad_pcb'
b=pcb.LoadBoard(str(path));STEP=.5;W=320;H=200
layers=[pcb.F_Cu,pcb.B_Cu];occupied=[defaultdict(set),defaultdict(set)];pads=defaultdict(list);routes=[];vias=set()
def pt(v):return (round(pcb.ToMM(v.x)/STEP),round(pcb.ToMM(v.y)/STEP))
def mm(p):return pcb.VECTOR2I(pcb.FromMM(p[0]*STEP),pcb.FromMM(p[1]*STEP))
def block(x,y,rx,ry,n):
 for ix in range(math.floor((x-rx)/STEP),math.ceil((x+rx)/STEP)+1):
  for iy in range(math.floor((y-ry)/STEP),math.ceil((y+ry)/STEP)+1):
   if abs(ix*STEP-x)<=rx and abs(iy*STEP-y)<=ry:
    for l in range(2):occupied[l][(ix,iy)].add(n)
for f in b.GetFootprints():
 for p in f.Pads():
  pos=p.GetPosition();n=p.GetNetCode();x,y=pcb.ToMM(pos.x),pcb.ToMM(pos.y)
  size=p.GetSize();sx,sy=pcb.ToMM(size.x),pcb.ToMM(size.y)
  if round(p.GetOrientationDegrees())%180:sx,sy=sy,sx
  block(x,y,sx/2+.65,sy/2+.65,n if n else -1)
  if n:pads[n].append((pt(pos),pos,f.GetReference(),p.GetNumber()))
# Retain 2mm copper margin and mounting-hole envelope.
for n,ps in pads.items():
 for p,_,r,num in ps:
  for l in range(2):
   bad=occupied[l][p]-{n}
   assert not bad,('placement blocks pad',r,num,p,bad)
def free(p,l,n):
 x,y=p;return 4<=x<=W-4 and 4<=y<=H-4 and not (occupied[l].get(p,set())-{n})
def pathfind(n,start,goals):
 target=list(goals);xmin=min(p[0] for p,l in target);xmax=max(p[0] for p,l in target);ymin=min(p[1] for p,l in target);ymax=max(p[1] for p,l in target)
 def heur(p):return max(xmin-p[0],0,p[0]-xmax)+max(ymin-p[1],0,p[1]-ymax)
 heap=[];dist={};prev={};seq=0
 for l in [0,1]:
  st=(start[0],start[1],l,4);dist[st]=0;heapq.heappush(heap,(heur(start),0,seq,st));seq+=1
 while heap:
  _,cost,_,s=heapq.heappop(heap);x,y,l,d=s;p=(x,y)
  if cost!=dist[s]:continue
  if (p,l) in goals:
   ans=[s]
   while s in prev:s=prev[s];ans.append(s)
   return list(reversed(ans))
  for nd,(dx,dy) in enumerate([(-1,0),(1,0),(0,-1),(0,1),(0,0)]):
   q=(x+dx,y+dy);nl=1-l if nd==4 else l
   if not free(q,nl,n):continue
   if nd==4:
    if any(not free((x+ox,y+oy),ll,n) for ll in range(2) for ox,oy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]):continue
   nc=cost+(25 if nd==4 else 1)+(1 if nd!=4 and d!=4 and nd!=d else 0)+(.15 if (nl==0 and dy==0 or nl==1 and dx==0) and nd!=4 else 0)
   ns=(q[0],q[1],nl,nd)
   if nc<dist.get(ns,1e99):dist[ns]=nc;prev[ns]=s;heapq.heappush(heap,(nc+heur(q),nc,seq,ns));seq+=1
 return None
def occupy(n,p,l,r=1):
 for dx in range(-r,r+1):
  for dy in range(-r,r+1):occupied[l][(p[0]+dx,p[1]+dy)].add(n)
def track(n,a,z,l):
 if a==z:return
 t=pcb.PCB_TRACK(b);t.SetStart(a);t.SetEnd(z);t.SetLayer(layers[l]);t.SetWidth(pcb.FromMM(.3));t.SetNetCode(n);b.Add(t)
order=sorted(pads,key=lambda n:(b.FindNet(n).GetNetname()=='GND',len(pads[n]),max(p[0][0] for p in pads[n])-min(p[0][0] for p in pads[n])+max(p[0][1] for p in pads[n])-min(p[0][1] for p in pads[n])))
fail=[]
for n in order:
 ps=pads[n][:];p0=ps.pop(0)[0];tree={(p0,0),(p0,1)};netpaths=[]
 while ps:
  target=min(ps,key=lambda pp:min(abs(pp[0][0]-p[0])+abs(pp[0][1]-p[1]) for p,l in tree));ps.remove(target);ans=pathfind(n,target[0],tree)
  if ans is None:fail.append([b.FindNet(n).GetNetname(),target[2:]]);continue
  for i,(x,y,l,d) in enumerate(ans):
   p=(x,y);tree.add((p,l));occupy(n,p,l)
   if i and ans[i-1][2]!=l:
    for ll in range(2):occupy(n,p,ll,2)
    if (p,n) not in vias:
     via=pcb.PCB_VIA(b);via.SetPosition(mm(p));via.SetWidth(pcb.FromMM(.8));via.SetDrill(pcb.FromMM(.4));via.SetViaType(pcb.VIATYPE_THROUGH);via.SetLayerPair(pcb.F_Cu,pcb.B_Cu);via.SetNetCode(n);b.Add(via);vias.add((p,n))
  # Consolidate collinear grid edges.
  start=ans[0];last=start;direction=None
  for cur in ans[1:]:
   dr=(cur[0]-last[0],cur[1]-last[1],cur[2]-last[2])
   if dr[2] or (direction is not None and dr!=direction):track(n,mm(start[:2]),mm(last[:2]),last[2]);start=last
   if dr[2]:start=cur;direction=None
   else:direction=dr
   last=cur
  track(n,mm(start[:2]),mm(last[:2]),last[2]);netpaths.append(ans)
 # Connect exact native pad centers to their grid points on both layers.
 for p,exact,ref,num in pads[n]:
  for l in range(2):track(n,exact,mm(p),l)
 print(b.FindNet(n).GetNetname(),len(pads[n]),'pads',len(netpaths),'branches',flush=True)
pcb.SaveBoard(str(path),b)
report={'failed_branches':fail,'vias':len(vias),'tracks':len(list(b.GetTracks())),'grid_mm':STEP,'clearance_strategy':'Inflated native pads and conservative grid reservation; native DRC authoritative'}
(ROOT/'validation/routing.json').write_text(json.dumps(report,indent=2));print(report)
