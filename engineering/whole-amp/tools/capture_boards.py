from pathlib import Path as _GuardPath
if (_GuardPath(__file__).resolve().parents[1]/'NATIVE_EDIT_GUARD').exists():
 raise RuntimeError('Saved native CAD is authoritative. Preserve it before intentionally regenerating this historical experiment.')
import pcbnew as pcb,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];data=json.loads((R/'board-plan.json').read_text());LIB=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
wire_layers=pcb.LSET.ExternalCuMask();wire_layers.AddLayer(pcb.F_Mask);wire_layers.AddLayer(pcb.B_Mask)
errors=[]
for name in ['Main','Power','Control']:
 spec=data['boards'][name];w,h=spec['size'];b=pcb.BOARD();b.SetCopperLayerCount(2);netnames={n for r in spec['refs'] for n in data['components'][r]['pins'].values() if n};nets={}
 for n in sorted(netnames):v=pcb.NETINFO_ITEM(b,n);b.Add(v);nets[n]=v
 loaded=[]
 for r in spec['refs']:
  c=data['components'][r];lib,fn=c['footprint'].split(':');f=pcb.FootprintLoad(str((R/'libraries' if lib=='Renegade_Whole' else LIB)/(lib+'.pretty')),fn)
  if not f:errors.append((r,c['footprint']));continue
  f.SetReference(r);f.SetValue(c['value']);f.SetFPID(pcb.LIB_ID(lib,fn));f.Value().SetVisible(False)
  physical={p.GetNumber() for p in f.Pads() if p.GetNumber()};assert physical==set(c['pins']),(r,physical,c['pins'])
  for p in f.Pads():
   if c['pins'][p.GetNumber()]:p.SetNet(nets[c['pins'][p.GetNumber()]])
  loaded.append((r,f))
 # Shelf placement by actual courtyard dimensions; leave room for routing and edge ports.
 x=12;y=20;shelf=0;positions={}
 for r,f in (sorted(loaded,key=lambda rf:-pcb.ToMM(rf[1].GetBoundingBox(False,False).GetHeight())) if name=='Power' else loaded):
  bbox=f.GetBoundingBox(False,False);bw=pcb.ToMM(bbox.GetWidth());bh=pcb.ToMM(bbox.GetHeight())
  gap=7 if name!='Control' else 4
  if x+bw>w-12:x=12;y+=shelf+gap;shelf=0
  # Translate bbox corner to the shelf location, avoiding rotations or guessed body origins.
  f.SetPosition(pcb.VECTOR2I(pcb.FromMM(x)-bbox.GetX(),pcb.FromMM(y)-bbox.GetY()));b.Add(f);positions[r]=[pcb.ToMM(f.GetPosition().x),pcb.ToMM(f.GetPosition().y)]
  x+=bw+gap;shelf=max(shelf,bh)
  if y+bh>h-15:errors.append((name,'shelf overflow',r,y+bh))
 # Individually labelled wire pads, split across the top and bottom edge.
 ports=[]
 for i,n in enumerate(spec['ports']):
  top=i%2==0;j=i//2;px=10+j*(w-20)/max(1,math.ceil(len(spec['ports'])/2)-1);py=8 if top else h-8
  f=pcb.FOOTPRINT(b);ref='J'+name[0]+str(i+1).zfill(3);f.SetReference(ref);f.SetValue(n);f.Value().SetVisible(False);f.SetPosition(pcb.VECTOR2I(pcb.FromMM(px),pcb.FromMM(py)))
  p=pcb.PAD(f);p.SetNumber('1');p.SetShape(pcb.PAD_SHAPE_CIRCLE);p.SetAttribute(pcb.PAD_ATTRIB_PTH);p.SetSize(pcb.VECTOR2I(pcb.FromMM(3),pcb.FromMM(3)));p.SetDrillSize(pcb.VECTOR2I(pcb.FromMM(1.3),pcb.FromMM(1.3)));p.SetLayerSet(wire_layers);p.SetNet(nets[n]);p.SetPosition(f.GetPosition());f.Add(p);b.Add(f);ports.append({'reference':ref,'net':n,'xy':[px,py],'drill':1.3,'pad':3})
 for idx,(xx,yy) in enumerate([(4,4),(w-4,4),(w-4,h-4),(4,h-4)],1):
  f=pcb.FootprintLoad(str(LIB/'MountingHole.pretty'),'MountingHole_3.2mm_M3');f.SetReference('H'+str(idx));f.SetPosition(pcb.VECTOR2I(pcb.FromMM(xx),pcb.FromMM(yy)));f.Value().SetVisible(False);b.Add(f)
 for a,z in [((0,0),(w,0)),((w,0),(w,h)),((w,h),(0,h)),((0,h),(0,0))]:
  e=pcb.PCB_SHAPE();e.SetShape(pcb.SHAPE_T_SEGMENT);e.SetStart(pcb.VECTOR2I(*[pcb.FromMM(v) for v in a]));e.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(v) for v in z]));e.SetLayer(pcb.Edge_Cuts);e.SetWidth(pcb.FromMM(.05));b.Add(e)
 out=R/'pcb'/name;out.mkdir(exist_ok=True);pcb.SaveBoard(str(out/('Renegade_'+name+'.kicad_pcb')),b)
 (out/'placements.json').write_text(json.dumps({'parts':positions,'ports':ports,'layout_status':'initial unrouted; no fabrication release'},indent=2))
 print(name,'parts',len(loaded),'extent',y+shelf,'height',h,flush=True)
(R/'validation/footprint-capture.json').write_text(json.dumps({'errors':errors},indent=2));print(errors)
