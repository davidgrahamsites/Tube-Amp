"""Selected Bourns3296W library footprint; no existing PCB overwritten."""
from pathlib import Path
import pcbnew,json
p=Path(__file__).resolve().parent;lib=p/'Renegade_Selected.pretty'
f=pcbnew.FootprintLoad('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Potentiometer_THT.pretty','Potentiometer_Bourns_3296W_Vertical')
name='Bourns_3296W_TopAdjust_P2.54'
f.SetFPID(pcbnew.LIB_ID('Renegade_Selected',name));f.SetLibDescription('Bourns3296W503LF/104LF; pins1CCW,2wiper,3CW. Pitch2.54; lead0.51+/-0.03mm; body9.53+/-0.25 x4.83+/-0.13mm; courtyard includes max body plus0.5mm per side. Reserve top screwdriver access and max height10.28mm plus seating clearance.')
for g in f.GraphicalItems():
 if isinstance(g,pcbnew.PCB_SHAPE) and g.GetLayer()==pcbnew.F_CrtYd:
  if g.GetShape()==pcbnew.SHAPE_T_RECT:
   g.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(-7.93),pcbnew.FromMM(-2.98)))
   g.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(2.85),pcbnew.FromMM(2.99)))
io=pcbnew.PCB_IO_KICAD_SEXPR();io.FootprintSave(str(lib),f)
f=pcbnew.FootprintLoad(str(lib),name);rows=[]
for pad in sorted(f.Pads(),key=lambda x:x.GetNumber()):
 rows.append({'pin':pad.GetNumber(),'x_mm':pcbnew.ToMM(pad.GetPosition().x),'y_mm':pcbnew.ToMM(pad.GetPosition().y),'drill_mm':pcbnew.ToMM(pad.GetDrillSize().x)})
assert [x['x_mm'] for x in rows]==[0,-2.54,-5.08]
assert all(x['drill_mm']==.8 for x in rows)
(p/'trimmer-verification.json').write_text(json.dumps({'kicad':pcbnew.Version(),'footprint':name,'native_reload':True,'pads':rows,'max_lead_mm':.54,'status':'native geometry checked; SVG visual review and PCB integration pending'},indent=2)+'\n')
print(rows)
