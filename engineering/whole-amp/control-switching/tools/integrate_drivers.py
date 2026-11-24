"""One-time bounded native driver and controller-clamp correction; never regenerate sheets."""
import copy,hashlib,json,subprocess,sys,uuid
from pathlib import Path
M=Path(__file__).resolve().parents[1];ROOT=M.parents[2];BASE='a9fd3fb5e12f23d84b21dd751f16ec957ed9e62e'
sys.path.insert(0,str(M.parent/'tools'));import native_sexpr as v
Q=json.dumps
UID=lambda n:str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade/driver/2026-11-24/'+n))
def emit(x):return '('+' '.join(emit(t) if isinstance(t,list) else str(t) for t in x)+')'
def prop(x,name):return next(p for p in v.children(x,'property') if p[1]==Q(name))
def renew(x):
 for t in x:
  if isinstance(t,list):
   if t[0]=='uuid':t[1]=UID(t[1])
   else:renew(t)
def spans(text,kind,level=1):
 depth=0;quoted=False;escaped=False;start=None
 for i,ch in enumerate(text):
  if quoted:
   if escaped:escaped=False
   elif ch=='\\':escaped=True
   elif ch=='"':quoted=False
  elif ch=='"':quoted=True
  elif ch=='(':
   if depth==level and text.startswith('('+kind+' ',i):start=i
   depth+=1
  elif ch==')':
   depth-=1
   if depth==level and start is not None:yield start,i+1;start=None

def main():
 assert sys.argv[1:]==['--apply'] and not (M/'results/integration.json').exists()
 paths=['engineering/whole-amp/reverb-600/circuit.json','engineering/whole-amp/reverb-600/cad/09b_latches_drivers.kicad_sch','engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb','engineering/whole-amp/reverb-600/cad/libraries/Renegade_Draft.kicad_sym']
 old={p:(ROOT/p).read_text() for p in paths}
 for p,t in old.items():assert t==subprocess.check_output(['/usr/bin/git','show',BASE+':'+p],cwd=ROOT).decode(),p
 circuit=json.loads(old[paths[0]]);a=v.parse(old[paths[1]]);b=v.parse(old[paths[2]])
 libname='Transistor_FET_AO3400A';fpname='AOS_SOT23_PO00001N';fp='Renegade_Selected:'+fpname
 ds='https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf'
 symbols={prop(x,'Reference')[2].strip('"'):x for x in v.children(a,'symbol')}
 newlib=copy.deepcopy(next(x for x in v.children(v.field(a,'lib_symbols'),'symbol') if x[1]=='"Renegade_Draft:Transistor_FET_2N7000"'))
 newlib[1]=Q('Renegade_Draft:'+libname)
 for x in v.children(newlib,'symbol'):
  x[1]=x[1].replace('Transistor_FET_2N7000',libname)
  for pin in v.children(x,'pin'):
   n=v.field(pin,'number');n[1]={'"1"':'"2"','"2"':'"1"','"3"':'"3"'}[n[1]]
 for name,value in [('Value','AO3400A'),('Footprint',fp),('Datasheet',ds),('Description','AOS AO3400A, 30V N-channel, G1 S2 D3; local drain clamp required')]:
  if any(p[1]==Q(name) for p in v.children(newlib,'property')):prop(newlib,name)[2]=Q(value)
 replacements=[]
 for ref in ['Q1','Q2']:
  sym=copy.deepcopy(symbols[ref]);v.field(sym,'lib_id')[1]=newlib[1]
  for name,value in [('Value','AO3400A'),('Footprint',fp),('Datasheet',ds),('Source','VAL-028'),('Rating','30V; RDS max48mOhm at2.5V/25C; local clamp'),('Design_status','Engineering integrated; assembled transient qualification pending')]:prop(sym,name)[2]=Q(value)
  for pin in v.children(sym,'pin'):pin[1]={'"1"':'"2"','"2"':'"1"','"3"':'"3"'}[pin[1]]
  for start,end in spans(old[paths[1]],'symbol'):
   x=v.parse(old[paths[1]][start:end])
   if prop(x,'Reference')[2]==Q(ref):replacements.append((start,end,emit(sym)))
  row=next(x for x in circuit['components'] if x['reference']==ref)
  row.update(value='AO3400A',symbol=libname,pins={'1':row['pins']['2'],'2':row['pins']['1'],'3':row['pins']['3']},datasheet=ds,footprint=fp,selected_mpn='AO3400A',source='VAL-028',rating='30V; 48mOhm max at2.5V/25C; local drain clamp',status='engineering integrated; actual transient and thermal qualification pending')
 sch=old[paths[1]]
 for start,end,text in sorted(replacements,reverse=True):sch=sch[:start]+text+sch[end:]
 sch=sch.replace('(lib_symbols ','(lib_symbols '+emit(newlib)+' ',1)
 extra=[];diode_ids={}
 for ref,template,dy,net in [('D333','D331',0,'COIL_CH'),('D342','D341',129.54,'COIL_REV')]:
  assert ref not in symbols
  sym=copy.deepcopy(symbols[template]);renew(sym);diode_ids[ref]=v.field(sym,'uuid')[1]
  v.field(sym,'at')[1:]=['265.43',str(95.25+dy),'270']
  for p in v.children(sym,'property'):v.field(p,'at')[1:]=['270.51',str(88.9+dy),'0']
  prop(sym,'Reference')[2]=Q(ref);prop(sym,'Value')[2]='"1N4007"';v.field(prop(sym,'Value'),'at')[2]=str(91.44+dy)
  prop(sym,'Assembly')[2]='"Control"';prop(sym,'Source')[2]='"VAL-028"';prop(sym,'Rating')[2]='"Controller drain clamp; keep remote coil diodes"'
  prop(sym,'Datasheet')[2]='"https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf"'
  v.field(v.field(v.field(v.field(sym,'instances'),'project'),'path'),'reference')[1]=Q(ref)
  extra.append(emit(sym))
  points=[((265.43,91.44+dy),(265.43,76.2+dy)),((265.43,76.2+dy),(289.56,76.2+dy)),((265.43,99.06+dy),(265.43,104.14+dy))]
  for i,(p,q) in enumerate(points):extra.append(f'(wire (pts (xy {p[0]} {p[1]}) (xy {q[0]} {q[1]})) (stroke (width 0) (type default)) (uuid {UID(ref+str(i))}))')
  for i,(x,y) in enumerate([(289.56,76.2+dy),(265.43,104.14+dy)]):extra.append(f'(junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid {UID(ref+"junction"+str(i))}))')
  row=copy.deepcopy(next(x for x in circuit['components'] if x['reference']==template));row.update(reference=ref,value='1N4007',source='VAL-028',rating='Controller local drain clamp; retain remote coil diode',status='engineering integrated; assembled forward-recovery/transient qualification pending',datasheet='https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf');circuit['components'].append(row)
 extra.append(f'(text "D333 / D342: Control, beside driver drains.\\nRetain D331 / D332 / D341 at remote coils." (at 270 155 0) (effects (font (size 1.27 1.27)) (justify left top)) (uuid {UID("clamp-note")}))')
 sch=sch.rstrip()[:-1]+' '+' '.join(extra)+')\n'
 # Exact AOS recommended SMD lands; no lead holes. Courtyard includes max body/lead envelope.
 fptext=f'''(footprint "{fpname}" (version 20260101) (generator "renegade_driver") (layer "F.Cu")
 (descr "AOS SOT23 PO-00001N; 0.8x0.8 lands; row2.4, pair1.9; G1 S2 D3; height max1.25")
 (property "Reference" "REF**" (at 0 -2.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))
 (property "Value" "AO3400A" (at 0 2.5) (layer "F.Fab") hide (effects (font (size 1 1) (thickness .15))))
 (attr smd)
 (fp_rect (start -1.55 -.9) (end 1.55 .9) (stroke (width .1) (type solid)) (fill none) (layer "F.Fab"))
 (fp_rect (start -1.85 -1.85) (end 1.85 1.85) (stroke (width .05) (type solid)) (fill none) (layer "F.CrtYd"))
 (fp_line (start -1.65 -.75) (end -1.65 .65) (stroke (width .12) (type solid)) (layer "F.SilkS"))
 (fp_line (start 1.65 -.75) (end 1.65 .65) (stroke (width .12) (type solid)) (layer "F.SilkS"))
 (fp_circle (center -1.65 1.2) (end -1.55 1.2) (stroke (width .1) (type solid)) (fill solid) (layer "F.SilkS"))
 (pad "1" smd rect (at -.95 1.2) (size .8 .8) (layers "F.Cu" "F.Paste" "F.Mask"))
 (pad "2" smd rect (at .95 1.2) (size .8 .8) (layers "F.Cu" "F.Paste" "F.Mask"))
 (pad "3" smd rect (at 0 -1.2) (size .8 .8) (layers "F.Cu" "F.Paste" "F.Mask")))\n'''
 fps=v.fps(b);board=old[paths[2]];replacement={};add=[];routes=[];vias=[]
 def route(layer,net,pts,width=.4):
  for p,q in zip(pts,pts[1:]):routes.append((layer,net,p,q,width))
 for ref,dref,dx,net,gate in [('Q1','D333',0,'COIL_CH','CH_GATE'),('Q2','D342',60.68,'COIL_REV','REV_GATE')]:
  f=v.parse(fptext);f[1]=Q(fp);f=[x for x in f if not isinstance(x,list) or x[0] not in ['version','generator']]
  f.extend([copy.deepcopy(v.field(fps[ref],'uuid')),['at',str(114.495+dx),'45.105'],copy.deepcopy(v.field(fps[ref],'path'))]);prop(f,'Reference')[2]=Q(ref)
  for pad,n in zip(v.children(f,'pad'),[gate,'GND',net]):pad.extend([['net',Q(n)],['uuid',Q(UID(ref+'pad'+pad[1]))]])
  replacement[ref]=emit(f)
  # Existing B.Cu drain track endpoint stays untouched; an adjacent via joins new SMD drain.
  vias.append((117.035+dx,45.105,net));route('F.Cu',net,[(114.495+dx,43.905),(115.835+dx,43.905),(117.035+dx,45.105)])
  # Local diode horizontally mirrored: anode beside drain, cathode toward supply.
  f=v.parse((ROOT/'engineering/component-selection/footprints/Renegade_Selected.pretty/Onsemi_1N4007RLG_P10.16.kicad_mod').read_text());f[1]='"Renegade_Selected:Onsemi_1N4007RLG_P10.16"'
  f=[x for x in f if not isinstance(x,list) or x[0] not in ['version','generator','fp_text']]
  f.extend([['at',str(125+dx),'40','180'],['uuid',Q(UID(dref+'footprint'))],['path',Q('/97ca3088-a174-52f9-956d-0a38bb8e2f56/0774e6be-6282-5572-be57-238f3edfef89/'+diode_ids[dref])]])
  for name,val,y in [('Reference',dref,2.6),('Value','1N4007',0)]:
   f.append(['property',Q(name),Q(val),['at','5.08',str(y),'180'],['layer','"F.SilkS"' if name=='Reference' else '"F.Fab"'],['effects',['font',['size','1','1'],['thickness','.15']]]])
  for pad,n in zip(v.children(f,'pad'),['+12V',net]):pad.extend([['net',Q(n)],['uuid',Q(UID(dref+'pad'+pad[1]))]])
  add.append(emit(f));route('F.Cu',net,[(114.495+dx,43.905),(114.495+dx,40.345),(114.84+dx,40)])
  # Gate and source local paths preserve the logical G/S swap, with 45-degree bends.
  route('F.Cu',gate,[(89.535+dx,43.875),(95.685+dx,43.875)],.25)
  vias.append((111.545+dx,46.305,gate))
  route('B.Cu',gate,[(95.685+dx,43.875),(95.685+dx,51),(96.685+dx,52),(110.545+dx,52),(111.545+dx,51),(111.545+dx,46.305)],.25)
  route('F.Cu',gate,[(111.545+dx,46.305),(113.545+dx,46.305)],.25)
  route('F.Cu','GND',[(105.845+dx,43.875),(105.845+dx,47.505),(106.845+dx,48.505),(114.445+dx,48.505),(115.445+dx,47.505),(115.445+dx,46.305)])
 route('F.Cu','+12V',[(125,40),(125,33),(126,32),(184.68,32),(185.68,33),(185.68,40)])
 route('F.Cu','+12V',[(185.68,40),(185.68,60),(182.104,63.576),(182.104,68.125)])
 for start,end in reversed(list(spans(board,'footprint'))):
  f=v.parse(board[start:end]);ref=prop(f,'Reference')[2].strip('"')
  if ref in replacement:board=board[:start]+replacement[ref]+board[end:]
 for i,(layer,net,p,q,width) in enumerate(routes):add.append(f'(segment (start {p[0]:.6f} {p[1]:.6f}) (end {q[0]:.6f} {q[1]:.6f}) (width {width}) (layer "{layer}") (net "{net}") (uuid "{UID("track"+str(i))}"))')
 for i,(x,y,net) in enumerate(vias):add.append(f'(via (at {x:.6f} {y:.6f}) (size 0.8) (drill 0.4) (layers "F.Cu" "B.Cu") (net "{net}") (uuid "{UID("via"+str(i))}"))')
 board=board.rstrip()[:-1]+'\n'+'\n'.join(add)+')\n'
 local=copy.deepcopy(newlib);local[1]=Q(libname);library=old[paths[3]].rstrip()[:-1]+'\n'+emit(local)+')\n'
 changes={paths[0]:json.dumps(circuit,indent=2)+'\n',paths[1]:sch,paths[2]:board,paths[3]:library}
 for t in [sch,board,library,fptext]:v.parse(t)
 for p,t in changes.items():(ROOT/p).write_text(t)
 (ROOT/f'engineering/component-selection/footprints/Renegade_Selected.pretty/{fpname}.kicad_mod').write_text(fptext)
 (M/'results/integration.json').write_text(json.dumps(dict(baseline_commit=BASE,changed_refs=['Q1','Q2'],added_refs=['D333','D342'],added_track_count=len(routes),added_via_count=len(vias),before_sha256={p:hashlib.sha256(t.encode()).hexdigest() for p,t in old.items()},after_sha256={p:hashlib.sha256(t.encode()).hexdigest() for p,t in changes.items()},fabrication_ready=False),indent=2)+'\n')
 print('Integrated AO3400A pins/packages and two controller drain clamps; native gates still required.')
if __name__=='__main__':main()
