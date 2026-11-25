"""Native fill inspection; does not save or refill the input board."""
from pathlib import Path
import hashlib,json,math,sys
import wx
APP=wx.App(False)
import pcbnew as p
M=Path(__file__).resolve().parents[1];src=Path(sys.argv[1]);b=p.LoadBoard(str(src));b.BuildConnectivity();keep=[b]
zones=list(b.Zones());keep+=zones;planes=[z for z in zones if not z.GetIsRuleArea()];assert len(planes)==1
z=planes[0];assert z.GetLayer()==p.B_Cu and z.GetNetname()=='GND' and z.IsFilled();poly=z.GetFilledPolysList(p.B_Cu)
assert poly.OutlineCount()==1 and not z.IsIsland(p.B_Cu,0)
mounts=[]
for ref in ['H1','H2','H3','H4']:
 f=b.FindFootprintByReference(ref);keep.append(f);q=f.GetPosition()
 for r in [0,1,2,3,4,4.49]:
  for i in range(64):assert not z.HitTestFilledArea(p.B_Cu,p.VECTOR2I(q.x+p.FromMM(r*math.cos(i*math.pi/32)),q.y+p.FromMM(r*math.sin(i*math.pi/32))))
 mounts.append({'reference':ref,'sampled_exclusion_radius_mm':4.49,'samples':384,'passed':True})
pads=[]
for f in b.GetFootprints():
 keep.append(f)
 for pad in f.Pads():
  keep.append(pad)
  if pad.GetNetname()=='GND':pads.append([f.GetReference(),pad.GetNumber()])
# Filled polygon includes cut-outs and is tested through native geometry, not image colors.
report={'kicad_version':p.GetBuildVersion(),'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'zone_count':len(zones),'plane_count':1,'plane_layer':'B.Cu','plane_net':'GND','filled':True,'filled_polygon_count':1,'floating_island':False,'filled_area_mm2':poly.Area()/1e12,'board_area_mm2':16000,'ground_pad_count':len(pads),'ground_pads':sorted(pads),'mount_exclusions':mounts,'current_capacity_or_EMI_qualified':False,'fabrication_ready':False}
(M/'results/fill.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['ground_pads','mount_exclusions']},indent=2))
