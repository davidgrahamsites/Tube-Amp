"""Exact-part KNSCHA film geometry; manufacturer PDFs in ../evidence."""
from pathlib import Path
import json
import pcbnew as p
IO = p.PCB_IO_KICAD_SEXPR()

ROOT = Path(__file__).resolve().parent
LIB = ROOT / 'Renegade_Selected.pretty'
SYSTEM = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
report = []
for mpn, thickness, height in [('MEB104J63V82CB0236', 2.5, 6.5), ('MEB105J63V82CB0235', 5, 10.5)]:
    name = 'KNSCHA_' + mpn
    generic = f'C_Rect_L7.2mm_W{thickness:.1f}mm_P5.00mm'
    f = IO.FootprintLoad(str(SYSTEM / 'Capacitor_THT.pretty'), generic)
    assert f, generic
    f.SetFPID(p.LIB_ID('Renegade_Selected', name))
    f.SetValue(mpn)
    f.Models().clear()  # Generic model is not exact-part evidence.
    f.SetLibDescription(f'{mpn}; nominal 7.2 x {thickness} x H{height}mm, body tolerance +/-0.5mm; pitch5mm +/-0.5; datasheet-specific max-body courtyard.')
    for pad in f.Pads():
        pad.SetDrillSize(p.VECTOR2I(p.FromMM(.9), p.FromMM(.9)))
        pad.SetSize(p.VECTOR2I(p.FromMM(1.8), p.FromMM(1.8)))
    for item in list(f.GraphicalItems()):
        if item.GetLayer() == p.F_CrtYd:
            f.Remove(item)
    left, right = 2.5 - 7.7 / 2 - .25, 2.5 + 7.7 / 2 + .25
    half = (thickness + .5) / 2 + .25
    corners = [(left, -half), (right, -half), (right, half), (left, half)]
    for a, b in zip(corners, corners[1:] + corners[:1]):
        line = p.PCB_SHAPE(f)
        line.SetShape(p.SHAPE_T_SEGMENT)
        line.SetStart(p.VECTOR2I(*[p.FromMM(v) for v in a]))
        line.SetEnd(p.VECTOR2I(*[p.FromMM(v) for v in b]))
        line.SetLayer(p.F_CrtYd)
        line.SetWidth(p.FromMM(.05))
        f.Add(line)
    IO.FootprintSave(str(LIB), f)
    check = IO.FootprintLoad(str(LIB), name)
    pads = sorted(check.Pads(), key=lambda pad: pad.GetNumber())
    assert [pad.GetNumber() for pad in pads] == ['1', '2']
    assert p.ToMM(pads[1].GetPosition().x - pads[0].GetPosition().x) == 5
    assert all(p.ToMM(pad.GetDrillSize().x) == .9 for pad in pads)
    report.append(dict(mpn=mpn, footprint='Renegade_Selected:' + name,
                       body_max_mm=[7.7, thickness + .5, height + .5],
                       pitch_mm=5, drill_mm=.9, native_reload_pass=True))
(ROOT / 'knscha-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
