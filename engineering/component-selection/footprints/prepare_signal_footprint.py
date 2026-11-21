from pathlib import Path
import pcbnew,json
p=Path(__file__).resolve().parent;lib=p/'Renegade_Selected.pretty'
f=pcbnew.FootprintLoad('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Resistor_THT.pretty','R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal');name='Yageo_MFR50S_MF0207_P10.16'
f.SetFPID(pcbnew.LIB_ID('Renegade_Selected',name));f.SetValue('MFR50S_MF0207');f.Models().clear();f.SetLibDescription('YageoMFR50S orMF0207; nominal6.3+/-0.5 x2.4+/-0.2mm; lead0.55+/-0.05mm; formed10.16mm pitch; max-body courtyard; power/voltage by exact MPN and temperature.')
# Standard Fab body is6.3x2.5; a conservative geometric envelope for nominal2.4mm body.
for pad in f.Pads():pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(.8),pcbnew.FromMM(.8)))
pcbnew.PCB_IO_KICAD_SEXPR().FootprintSave(str(lib),f);g=pcbnew.FootprintLoad(str(lib),name);pads=sorted(g.Pads(),key=lambda x:x.GetNumber());assert len(pads)==2 and pcbnew.ToMM(pads[1].GetPosition().x)==10.16
(p/'signal-verification.json').write_text(json.dumps(dict(kicad=pcbnew.Version(),footprint=name,native_reload=True,pitch_mm=10.16,drill_mm=.8,max_lead_mm=.6,status='native reload passed; export/review/integration pending'),indent=2)+'\n')
