"""Exact KYET film bodies and lead patterns from individual approval sheets."""
from pathlib import Path
import pcbnew,json
p=Path(__file__).resolve().parent;lib=p/'Renegade_Selected.pretty';out=[]
parts=[('KP223J2J1001',12,10,4.5,10,.6),('KP104J2J1006',12,11,5.5,10,.6),('KP473J2J1001',12,11,5.5,10,.6),('KP105J2J2002',22.5,16,8.5,20,.8),('KP684J2J1502',17,14.5,8.5,15,.8)]
def pos(x,y):return pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y))
for mpn,w,h,t,pitch,lead in parts:
 name='KYET_'+mpn;f=pcbnew.FOOTPRINT(None);f.SetFPID(pcbnew.LIB_ID('Renegade_Selected',name));f.SetValue(mpn);f.SetReference('REF**');f.SetAttributes(pcbnew.FP_THROUGH_HOLE)
 f.SetLibDescription(f'KYET {mpn};630V5% polypropylene; body W{w} H{h} T{t}, each+/-1mm; pitch{pitch}+/-0.5mm; lead{lead}+/-0.05mm. Courtyard max body plus0.5mm. No3D model. Temperature<=100C. Peak voltage/ripple and layout isolation require review.')
 for layer,dx,dy in [(pcbnew.F_Fab,0,0),(pcbnew.F_SilkS,.15,.15),(pcbnew.F_CrtYd,1,1)]:
  g=pcbnew.PCB_SHAPE(f);g.SetShape(pcbnew.SHAPE_T_RECT);g.SetStart(pos((pitch-w)/2-dx,-t/2-dy));g.SetEnd(pos((pitch+w)/2+dx,t/2+dy));g.SetLayer(layer);g.SetWidth(pcbnew.FromMM(.12 if layer==pcbnew.F_SilkS else .05));f.Add(g)
 for n,x in [('1',0),('2',pitch)]:
  pad=pcbnew.PAD(f);pad.SetNumber(n);pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH);pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE);pad.SetPosition(pos(x,0));drill=.9 if lead==.6 else 1.1;pad.SetDrillSize(pos(drill,drill));pad.SetSize(pos(drill+.9,drill+.9));pad.SetLayerSet(pcbnew.LSET.AllCuMask());layers=pad.GetLayerSet();layers.AddLayer(pcbnew.F_Mask);layers.AddLayer(pcbnew.B_Mask);pad.SetLayerSet(layers);f.Add(pad)
 f.Reference().SetPosition(pos(pitch/2,-t/2-2));f.Reference().SetTextSize(pos(1,1));f.Value().SetPosition(pos(pitch/2,t/2+2));f.Value().SetTextSize(pos(1,1));f.Value().SetLayer(pcbnew.F_Fab)
 pcbnew.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib),f);g=pcbnew.FootprintLoad(str(lib),name);pads=sorted(g.Pads(),key=lambda x:x.GetNumber());assert len(pads)==2;assert abs(pcbnew.ToMM(pads[1].GetPosition().x)-pitch)<1e-6
 out.append(dict(mpn=mpn,footprint=name,kicad=pcbnew.Version(),native_reload=True,pitch_mm=pitch,drill_mm=drill,max_body_mm=[w+1,h+1,t+1],max_lead_mm=lead+.05,status='native geometry checked; export/review/integration pending'))
(p/'film-verification.json').write_text(json.dumps(out,indent=2)+'\n');print('five native footprints reloaded')
