"""Make temporary 45-degree chamfer candidates. Never overwrites source boards.

Only degree-two same-width, same-net/layer right-angle endpoint joins outside
pads/vias are changed. Trim at most0.20mm and one quarter of each leg. Native
DRC and pad-map review are mandatory before an integration owner adopts output.
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import shutil
import sys
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
manifest = {"operation": "right-angle chamfer candidates", "adopted": False, "boards": {}}
KEEP = []
for name in ['Main', 'Power', 'Control', 'Reverb']:
    src = ROOT / 'boards' / f'Renegade_{name}.kicad_pcb'
    dst = OUT / src.name
    assert not dst.exists(), 'Do not overwrite a prior candidate'
    b = p.LoadBoard(str(src)); KEEP.append(b)
    nodes = defaultdict(list)
    via_pts = {(t.GetPosition().x, t.GetPosition().y) for t in b.GetTracks() if isinstance(t, p.PCB_VIA)}
    for t in b.GetTracks():
        if isinstance(t, (p.PCB_VIA, p.PCB_ARC)): continue
        for start in [True, False]:
            v = t.GetStart() if start else t.GetEnd()
            nodes[(t.GetNetCode(), t.GetLayer(), v.x, v.y)].append((t, start))
    changes = []
    for (net, layer, x, y), entries in nodes.items():
        at = p.VECTOR2I(x, y)
        if len(entries) != 2 or (x, y) in via_pts: continue
        if any(q.GetNetCode() == net and q.HitTest(at) for f in b.GetFootprints() for q in f.Pads()): continue
        (a, sa), (z, sz) = entries
        if a.GetWidth() != z.GetWidth(): continue
        va = (a.GetEnd() if sa else a.GetStart()) - at
        vz = (z.GetEnd() if sz else z.GetStart()) - at
        la, lz = math.hypot(va.x, va.y), math.hypot(vz.x, vz.y)
        if not la or not lz or abs((va.x*vz.x+va.y*vz.y)/(la*lz)) > 1e-5: continue
        trim = min(p.FromMM(.20), la/4, lz/4)
        if trim < p.FromMM(.05): continue
        pa = at+p.VECTOR2I(round(va.x*trim/la), round(va.y*trim/la))
        pz = at+p.VECTOR2I(round(vz.x*trim/lz), round(vz.y*trim/lz))
        (a.SetStart if sa else a.SetEnd)(pa)
        (z.SetStart if sz else z.SetEnd)(pz)
        link = p.PCB_TRACK(b); link.SetNetCode(net); link.SetLayer(layer)
        link.SetWidth(a.GetWidth()); link.SetStart(pa); link.SetEnd(pz); b.Add(link)
        changes.append({"net": a.GetNetname(), "layer": b.GetLayerName(layer), "corner_mm": [p.ToMM(x), p.ToMM(y)], "trim_mm": p.ToMM(round(trim))})
    # KiCad may serialize project defaults; save only in temporary destination,
    # then overwrite candidate settings with exact authoritative bytes.
    p.SaveBoard(str(dst), b)
    for ext in ['.kicad_pro', '.kicad_dru']:
        if src.with_suffix(ext).exists(): shutil.copyfile(src.with_suffix(ext), dst.with_suffix(ext))
    manifest['boards'][name] = {"source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(), "candidate_sha256": hashlib.sha256(dst.read_bytes()).hexdigest(), "changes": changes}
(OUT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(json.dumps({n:len(r['changes']) for n,r in manifest['boards'].items()}))
