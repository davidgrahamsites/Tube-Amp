"""Native selected Yageo FMP200 footprint; no board modification."""
from pathlib import Path
import pcbnew,json
root=Path(__file__).resolve().parent;lib=root/'Renegade_Selected.pretty'
f=pcbnew.FootprintLoad('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Resistor_THT.pretty','R_Axial_DIN0309_L9.0mm_D3.2mm_P15.24mm_Horizontal')
name='Yageo_FMP200_L9.0_D3.9_P15.24'
f.SetFPID(pcbnew.LIB_ID('Renegade_Selected',name));f.SetValue('FMP200');f.Models().clear()
f.SetLibDescription('Yageo FMP200; body9.0+/-0.5 x diameter3.9+/-0.3mm; lead0.55+/-0.05mm; formed pitch15.24mm. Courtyard includes maximum body. No exact3D model. Thermal standoff required per assembly plan.')
for g in f.GraphicalItems():
 layer=g.GetLayer()
 if not isinstance(g,pcbnew.PCB_SHAPE):continue
 if layer in [pcbnew.F_Fab,pcbnew.F_SilkS,pcbnew.F_CrtYd]:
  for getter,setter in [(g.GetStart,g.SetStart),(g.GetEnd,g.SetEnd)]:
   q=getter();y=pcbnew.ToMM(q.y)
   if abs(y)>0.5:
    h=2.35 if layer==pcbnew.F_CrtYd else (2.22 if layer==pcbnew.F_SilkS else 1.95)
    setter(pcbnew.VECTOR2I(q.x,pcbnew.FromMM(h if y>0 else -h)))
for pad in f.Pads():
 pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(.8),pcbnew.FromMM(.8)))
io=pcbnew.PCB_IO_KICAD_SEXPR();io.FootprintSave(str(lib),f)
g=pcbnew.FootprintLoad(str(lib),name);pads=sorted(g.Pads(),key=lambda x:x.GetNumber())
assert len(pads)==2
pitch=pcbnew.ToMM(pads[1].GetPosition().x-pads[0].GetPosition().x)
assert abs(pitch-15.24)<1e-6
assert all(abs(pcbnew.ToMM(p.GetDrillSize().x)-.8)<1e-6 for p in pads)
(root/'fmp-verification.json').write_text(json.dumps(dict(kicad=pcbnew.Version(),footprint=name,native_reload=True,pitch_mm=pitch,drill_mm=.8,maximum_lead_mm=.6,max_body_length_mm=9.5,max_body_diameter_mm=4.2,status='library only; render and board integration pending'),indent=2)+'\n')
print(name,pitch)
