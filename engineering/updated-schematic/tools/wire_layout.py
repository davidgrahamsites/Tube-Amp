"""Presentation-only redraw of preserved native v0.2 sheets.
Manual placement is in wire-layout.json. All pins/nets come from the native
symbol instances and existing register; verify fresh native pin partitions.
"""
from pathlib import Path
from collections import defaultdict,Counter
import copy,hashlib,heapq,json,math,zipfile
from kicad_factory import parse,serialize,child,children,uid,resolved
ROOT=Path(__file__).resolve().parents[1]
STEP=1.27

def grid(v):return int(round(float(v)/STEP))
def mm(p):return [round(v*STEP,4) for v in p]
def key(ref,unit):return ref if unit==1 else ref+'/'+str(unit)
def pt(x,y):return (grid(x),grid(y))
def node(k,*v):return [k,*map(str,v)]
def text(s,x,y,size=1.27):
 return ['text',s,node('at',x,y,0),['effects',['font',node('size',size,size)],['justify','left','top']],['uuid',uid('layout/'+s+'/'+str(x)+'/'+str(y))]]

class Router:
 def __init__(self,w,h,blocks,reserved):
  self.w=grid(w-18);self.h=grid(h-48);self.blocks=blocks;self.reserved=reserved
  self.edges={};self.points=defaultdict(set);self.netedges=defaultdict(set);self.stop_points=defaultdict(set);self.protected=defaultdict(set)
 def add(self,n,a,b):
  assert a[0]==b[0] or a[1]==b[1],(n,a,b)
  dx=(b[0]>a[0])-(b[0]<a[0]);dy=(b[1]>a[1])-(b[1]<a[1]);p=a
  while p!=b:
   q=(p[0]+dx,p[1]+dy);e=tuple(sorted([p,q]));assert self.edges.get(e,n)==n,(n,e,self.edges.get(e));self.edges[e]=n;self.netedges[n].add(e);self.points[p].add(n);self.points[q].add(n);p=q
 def path(self,n,start,goals):
  # Manhattan router permits only straight perpendicular crossings.
  # No bend/branch/terminal can occur at a foreign wire crossing.
  heap=[];dist={(start,4):0};prev={};seq=0
  xmin=min(p[0] for p in goals);xmax=max(p[0] for p in goals);ymin=min(p[1] for p in goals);ymax=max(p[1] for p in goals)
  def heur(p):return max(xmin-p[0],0,p[0]-xmax)+max(ymin-p[1],0,p[1]-ymax)
  heapq.heappush(heap,(heur(start),0,seq,start,4))
  dirs=[(-1,0),(1,0),(0,-1),(0,1)]
  while heap:
   _,cost,_,p,d=heapq.heappop(heap)
   if cost!=dist.get((p,d)):continue
   if p in goals:
    path=[p];s=(p,d)
    while s in prev:s=prev[s];path.append(s[0])
    return list(reversed(path))
   foreign=self.points[p]-{n}
   for nd,(dx,dy) in enumerate(dirs):
    if foreign and d!=nd:continue
    q=(p[0]+dx,p[1]+dy)
    if not (grid(16)<=q[0]<=self.w and grid(34)<=q[1]<=self.h):continue
    if q in self.blocks and q not in self.reserved.get(n,set()):continue
    if any(q in ps for nn,ps in self.reserved.items() if nn!=n):continue
    e=tuple(sorted([p,q]));other=self.edges.get(e)
    if other is not None and other!=n:continue
    # Enter a crossing only through the perpendicular direction, never at a junction or terminal.
    fn=self.points[q]-{n}
    if fn:
     incident=[]
     for dd,(ax,ay) in enumerate(dirs):
      en=self.edges.get(tuple(sorted([q,(q[0]+ax,q[1]+ay)])))
      if en in fn:incident.append(dd)
     if sorted(incident) not in ([0,1],[2,3]):continue
     if (nd<2)==(incident[0]<2):continue
    nc=cost+1+(4 if d!=4 and d!=nd else 0)+(12 if fn else 0)
    state=(q,nd)
    if nc<dist.get(state,10**9):
     dist[state]=nc;prev[state]=(p,d);seq+=1;heapq.heappush(heap,(nc+heur(q),nc,seq,q,nd))
  raise ValueError('Cannot route '+n+' from '+str(mm(start)))
 def tree(self,n,terminals):
  terms=list(dict.fromkeys(terminals));tree={terms.pop(0)}
  while terms:
   p=min(terms,key=lambda p:min(abs(p[0]-q[0])+abs(p[1]-q[1]) for q in tree));terms.remove(p)
   path=self.path(n,p,tree)
   for a,b in zip(path,path[1:]):self.add(n,a,b)
   tree.update(path)
 def output(self,seed):
  out=[];degrees=defaultdict(Counter)
  for n,edges in self.netedges.items():
   adjacency=defaultdict(set)
   for a,b in edges:adjacency[a].add(b);adjacency[b].add(a)
   # Remove unused lead tails without touching any pin, label or power attachment.
   pending=[p for p,qs in adjacency.items() if len(qs)==1 and p not in self.protected[n]]
   while pending:
    p=pending.pop()
    if p not in adjacency or len(adjacency[p])!=1 or p in self.protected[n]:continue
    q=next(iter(adjacency[p]));adjacency[q].remove(p);del adjacency[p]
    if len(adjacency[q])==1 and q not in self.protected[n]:pending.append(q)
   stops=self.stop_points[n] & adjacency.keys() | {p for p,qs in adjacency.items() if len(qs)!=2 or len({q[0] for q in qs})!=1 and len({q[1] for q in qs})!=1}
   visited=set()
   for start in sorted(stops):
    for q in sorted(adjacency[start]):
     e=tuple(sorted([start,q]))
     if e in visited:continue
     visited.add(e);last=start;end=q
     while end not in stops:
      nxt=next(v for v in adjacency[end] if v!=last);visited.add(tuple(sorted([end,nxt])));last,end=end,nxt
     a,b=mm(start),mm(end)
     out.append(['wire',['pts',node('xy',*a),node('xy',*b)],['stroke',node('width',0),['type','default']],['uuid',uid(seed+'/wire/'+n+str(a)+str(b))]])
   for p,qs in adjacency.items():
    if len(qs)>=3:
     assert self.points[p]=={n},('junction crossing',n,p)
     out.append(['junction',node('at',*mm(p)),node('diameter',0),node('color',0,0,0,0),['uuid',uid(seed+'/junction/'+n+str(p))]])
  return out

def global_label(n,p,angle=0):
 x,y=mm(p)
 return ['global_label',n,['shape','passive'],node('at',x,y,angle),['effects',['font',node('size',1.1,1.1)],['justify','left' if angle==0 else 'right']],['uuid',uid('layout/label/'+n+str(p))],['property','Intersheetrefs','',node('at',x,y,angle),['effects',['font',node('size',1,1)],'hide']]]

def redraw():
 config=json.loads((ROOT/'wire-layout.json').read_text())
 guard=ROOT/'wire-layout-files.json'
 if guard.exists():
  changed=[n for n,h in json.loads(guard.read_text()).items() if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
  assert not changed,'Preserve native edits before re-layout: '+str(changed)
 spec=json.loads((ROOT/'design-connectivity.json').read_text())
 records=[c for c in spec['components'] if c['project']=='Renegade_220V_Reverb']
 cross=defaultdict(set)
 for c in records:
  for n in c['pins'].values():
   if n:cross[n].add(c['sheet'])
 report={};files=[]
 with zipfile.ZipFile(ROOT/'validation/label-layout-v0.2.zip') as archive:
  for name,cfg in config.items():
   source=parse(archive.read(name+'.kicad_sch').decode());lib=child(source,'lib_symbols');syms=children(source,'symbol')
   lookup={key(next(p[2] for p in children(s,'property') if p[1]=='Reference'),int(child(s,'unit')[1])):s for s in syms}
   recs={key(c['reference'],c['unit']):c for c in records if c['sheet']==name}
   assert set(lookup)==set(cfg['positions']), (name,set(lookup)^set(cfg['positions']))
   w,h=(594,420) if cfg.get('paper')=='A2' else (420,297)
   child(source,'paper')[1]=cfg.get('paper','A3')
   title=child(source,'title_block');child(title,'rev')[1]='0.3 DRAFT'
   source=[v for v in source if not(isinstance(v,list) and v[0] in {'wire','global_label','label','no_connect','junction','symbol','text'})]
   blocks=set();reserved=defaultdict(set);terms=defaultdict(list);pinpos={};extras=[]
   for k,s in lookup.items():
    c=recs[k];x,y,rot=cfg['positions'][k];x,y=mm(pt(x,y));child(s,'at')[1:]=list(map(str,[x,y,(-rot)%360]))
    symbolname=c['symbol'];ls=next(t for t in children(lib,'symbol') if t[1]=='Renegade_Draft:'+symbolname)
    pins=[]
    for sub in children(ls,'symbol'):
     u,style=map(int,sub[1].rsplit('_',2)[1:])
     if u in (0,c['unit']) and style in (0,1):pins.extend(children(sub,'pin'))
    # Compact traditional properties; detailed selection notes live in register.
    value=c['value']
    short=cfg.get('values',{}).get(k,value)
    if symbolname.startswith('Valve_'):short='12AT7' if 'ECC81' in symbolname else ('EL34' if 'EL34' in symbolname else '12AX7')
    if symbolname.startswith('Relay_'):short='G5V-2-H1 /12V'
    if symbolname.startswith('74xx_'):short=value.replace('SN','')
    if len(short)>32:short=short[:29]+'...'
    for p in children(s,'property'):
     if p[1] not in ('Reference','Value'):continue
     if p[1]=='Value':p[2]=short
     if symbolname.startswith(('Valve_','Transistor_')):px,py=x+9,y-6+(2.5 if p[1]=='Value' else 0)
     elif symbolname.startswith(('Device_R','Device_C','Device_L','Device_Fuse')) and rot in (0,180):px,py=x+4,y-1.27+(2.54 if p[1]=='Value' else 0)
     else:px,py=x-3.81,y-(21.59 if 'Transformer' in symbolname or 'Tank' in symbolname else 10.16)+(2.54 if p[1]=='Value' else 0)
     if symbolname=='Device_R_Potentiometer':px,py=x+8.89,y-7.62+(2.54 if p[1]=='Value' else 0)
     if k in cfg.get('properties',{}):px,py=cfg['properties'][k];py+=2.54 if p[1]=='Value' else 0
     child(p,'at')[1:]=list(map(str,[px,py,90 if rot in (90,270) else 0]));eff=child(p,'effects');child(eff,'font')[1]=node('size',1.15,1.15)
     just=child(eff,'justify')
     if just:just[1:]=['left']
     else:eff.append(['justify','left'])
     # Keep the short reference/value box clear of routes.
     bw=grid(max(len(p[2])*0.62,3));gx,gy=pt(px,py)
     blocks.update((xx,yy) for xx in range(gx,gx+bw+1) for yy in range(gy-1,gy+2))
    vp=next(p for p in children(s,'property') if p[1]=='Value')
    if vp[2]!=c['value']:
     vp[1]='Display'
     s.append(['property','Value',c['value'],node('at',x,y,0),['effects',['font',node('size',1,1)],'hide']])
    if symbolname.startswith('Valve_'):bx,by=(6.35,8.89) if c['unit']!=3 and not (symbolname=='Valve_EL34' and c['unit']==2) else (5.08,8.89)
    elif 'Transformer' in symbolname or 'Tank' in symbolname:bx,by=(15.24,18 if 'PowerTransformer' in symbolname else 12.7)
    elif symbolname.startswith(('74xx_','Power_Supervisor_')):bx,by=(6.35,6.35)
    elif symbolname.startswith('Regulator_'):bx,by=(6.35,3.81)
    elif symbolname.startswith('Relay_'):bx,by=(5.08,5.08)
    elif symbolname.startswith('Connector_'):bx,by=(4.4,5.5)
    elif symbolname.startswith('Switch_'):bx,by=(3.81,3.81)
    elif symbolname.startswith('Transistor_'):bx,by=(3.81,3.81)
    elif symbolname=='power_PWR_FLAG':bx,by=(2.54,2.54)
    else:bx,by=(2.54,2.54)
    if rot in (90,270):bx,by=by,bx
    gx,gy=pt(x,y);blocks.update((xx,yy) for xx in range(gx-grid(bx),gx+grid(bx)+1) for yy in range(gy-grid(by),gy+grid(by)+1))
    r=math.radians(rot)
    for pin in pins:
     num=child(pin,'number')[1];px,py,a=map(float,child(pin,'at')[1:]);p=pt(x+px*math.cos(r)+py*math.sin(r),y+px*math.sin(r)-py*math.cos(r));net=c['pins'][num];pinpos[k+':'+num]=p
     if net is None:
      extras.append(['no_connect',node('at',*mm(p)),['uuid',uid(name+'/nc/'+k+num)]]);continue
     angle=(a-rot)%360;dx,dy={0:(-1,0),90:(0,1),180:(1,0),270:(0,-1)}[angle]
     count=4 if symbolname not in ('Valve_EL34',) else 6
     end=(p[0]+dx*count,p[1]+dy*count)
     # All pin leads are reserved before routing to prevent accidental shorts.
     for i in range(count+1):reserved[net].add((p[0]+dx*i,p[1]+dy*i))
     terms[net].append(end)
     extras.append(('lead',net,p,end))
    source.append(s)
   # Explicit manual pins-to-wire waypoints supplement routing of hard topologies.
   router=Router(w,h,blocks,reserved)
   for e in extras:
    if isinstance(e,tuple):
     router.add(*e[1:]);router.stop_points[e[1]].update(e[2:]);router.protected[e[1]].add(e[2])
    else:source.append(e)
   labels=[];groundpoints=[]
   # Conventional local ground symbols, grouped only for nearby parallel branches.
   grounds=terms.pop('GND',[]);clusters=[]
   for p in sorted(grounds):
    target=next((g for g in clusters if abs(p[0]-g[0][0])+abs(p[1]-g[0][1])<=grid(30)),None)
    if target is None:clusters.append([p])
    else:target.append(p)
   for i,g in enumerate(clusters):
    n='GND';router.tree(n,g);p=max(g,key=lambda p:(p[1],p[0]));groundpoints.append(p)
   # PE copper bond is electrically identical to GND; retained explicitly on heater sheet.
   for n,xy in cfg.get('anchors',{}).items():terms[n].append(pt(*xy))
   # Small signal nets first, then shared rails and sheet interfaces.
   order=sorted(terms,key=lambda n:(n in ('+5V','+12V','B_EARLY','B_PRE','B_SCREEN','HEAT_A','HEAT_B'), max(p[0] for p in terms[n])-min(p[0] for p in terms[n])+max(p[1] for p in terms[n])-min(p[1] for p in terms[n])))
   for n in order:
    router.tree(n,terms[n])
    if len(cross[n])>1 or n=='PE':
     p=pt(*cfg['anchors'][n]) if n in cfg.get('anchors',{}) else terms[n][0]
     angle=180 if p[0]<grid(w/2) else 0
     router.stop_points[n].add(p);router.protected[n].add(p)
     gl=global_label(n,p,angle);child(gl,'uuid')[1]=uid(name+'/label/'+n);labels.append(gl)
   if name=='06_heaters':
    # One explicit star bond; alias is intentionally retained in ERC.
    pe=terms['PE'][0];g=pt(90,210);router.tree('PE',[pe,g]);router.protected['PE'].add(g);router.stop_points['PE'].add(g);labels.append(global_label('GND',g,0))
   # Add standard GND power symbols; they only name an existing ground wire.
   gs=resolved('power','GND');gs[1]='power:GND'
   for sub in children(gs,'symbol'):sub[1]='GND'+sub[1][len('GND'):]
   lib.append(gs)
   for i,p in enumerate(groundpoints):
    x,y=mm(p);ref='#PWR'+str((list(config).index(name)+1)*100+i+1);router.stop_points['GND'].add(p);router.protected['GND'].add(p);inst=next(v for v in children(lookup[next(iter(lookup))],'instances'))
    project=child(inst,'project');path=child(project,'path')[1]
    source.append(['symbol',['lib_id','power:GND'],node('at',x,y,0),node('unit',1),['in_bom','yes'],['on_board','yes'],['dnp','no'],['uuid',uid(name+'/ground/'+str(i))],['property','Reference',ref,node('at',x,y,0),['effects',['font',node('size',1,1)],'hide']],['property','Value','GND',node('at',x,y+5.08,0),['effects',['font',node('size',1,1)]]],['pin','1',['uuid',uid(name+'/groundpin/'+str(i))]],['instances',['project','Renegade_220V_Reverb',['path',path,['reference',ref],node('unit',1)]]]])
   source.extend(router.output(name));source.extend(labels)
   source.append(text('RENEGADE | WIRED SCHEMATIC v0.3 | ENGINEERING DRAFT',16,16,1.5))
   for t in cfg.get('notes',[]):source.append(text(t[0],t[1],t[2],t[3] if len(t)>3 else 1.27))
   f=ROOT/(name+'.kicad_sch');f.write_text(serialize(source)+'\n');files.append(f)
   report[name]={'symbols':len(syms),'global_labels':len(labels),'ground_symbols':len(groundpoints),'wire_segments':len([v for v in source if isinstance(v,list) and v[0]=='wire']),'junctions':len([v for v in source if isinstance(v,list) and v[0]=='junction'])}
  f=ROOT/'Renegade_220V_Reverb.kicad_sch';root=parse(archive.read(f.name).decode());child(child(root,'title_block'),'rev')[1]='0.3 DRAFT'
  for t in children(root,'text'):
   t[1]=t[1].replace('revision 0.2','revision 0.3').replace('Black named nets are electrical connections across this hierarchy.','Continuous wires connect each circuit; named interfaces connect between sheets.').replace('DRAFT v0.2 | Named nets connect across sheets','DRAFT v0.3 | Continuous wiring within circuit sheets')
  f.write_text(serialize(root)+'\n');files.append(f)
 (ROOT/'validation/wire-layout-report.json').write_text(json.dumps(report,indent=2)+'\n')
 guard.write_text(json.dumps({str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':redraw()
