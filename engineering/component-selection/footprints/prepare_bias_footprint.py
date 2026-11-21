"""Prepare one selected-part library footprint with KiCad10 native API; no board edits."""
from pathlib import Path
import pcbnew,json
root=Path(__file__).resolve().parent;lib=root/'Renegade_Selected.pretty';lib.mkdir(exist_ok=True)
src='/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Capacitor_THT.pretty'
f=pcbnew.FootprintLoad(src,'CP_Radial_D8.0mm_P3.50mm')
name='Samyoung_NFA_10u_200V_D8_P3.5'
f.SetFPID(pcbnew.LIB_ID('Renegade_Selected',name));f.SetValue('10u 200V NFA')
f.SetLibDescription('Samyoung NFA200VB10M8*11.5_LO; approval710-011 2020-06-23. D8.5mm max,13mm max height,pitch3.5+/-0.5mm,leads0.6+/-0.05mm. Pad1 positive. Courtyard9mm diameter. No exact3D model.')
f.SetKeywords('Samyoung NFA C371316 polarized capacitor 200V');f.Models().clear()
for g in f.GraphicalItems():
 if g.GetLayer()==pcbnew.F_CrtYd:g.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(6.25),0))
io=pcbnew.PCB_IO_KICAD_SEXPR();io.FootprintSave(str(lib),f)
g=pcbnew.FootprintLoad(str(lib),name);assert g
pads=sorted(g.Pads(),key=lambda p:p.GetNumber());assert len(pads)==2
assert abs(pcbnew.ToMM(pads[1].GetPosition().x-pads[0].GetPosition().x)-3.5)<1e-6
for p in pads:assert abs(pcbnew.ToMM(p.GetDrillSize().x)-.8)<1e-6
(root/'verification.json').write_text(json.dumps({'kicad':pcbnew.Version(),'footprint':name,'native_reload':True,'pad_count':2,'pad1':'positive; GND for C27/C28','pitch_mm':3.5,'drill_mm':.8,'pad_diameter_mm':1.6,'maximum_lead_mm':.65,'courtyard_diameter_mm':9,'max_body_diameter_mm':8.5,'max_height_mm':13,'status':'library footprint prepared; board integration and final render review pending'},indent=2)+'\n')
print('Saved and natively reloaded',lib/(name+'.kicad_mod'))
