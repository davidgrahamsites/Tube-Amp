"""Correct documented DRC findings without changing component pads or net assignments."""
from pathlib import Path
import json
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
KEEP = []
changes = []
for name in ['Main', 'Power', 'Control', 'Reverb']:
    path = ROOT / 'boards' / f'Renegade_{name}.kicad_pcb'
    board = p.LoadBoard(str(path))
    KEEP.append(board)
    fps = list(board.GetFootprints())
    KEEP.extend(fps)
    for f in fps:
        ref = f.GetReference()
        if str(f.GetFPID().GetLibItemName()).startswith('Yageo_FMP200'):
            pos = f.GetPosition()
            f.Reference().SetPosition(p.VECTOR2I(pos.x + p.FromMM(7.62), pos.y - p.FromMM(3.5)))
            changes.append([name, ref, 'reference above resistor body'])
        if name == 'Reverb' and ref in ['C614', 'R618']:
            x, y = {'C614': (132.5, 68), 'R618': (137, 35)}[ref]
            f.Reference().SetPosition(p.VECTOR2I(p.FromMM(x), p.FromMM(y)))
            changes.append([name, ref, 'reference clear of adjacent body'])
    if name == 'Reverb':
        # The grid landing is 0.12 mm from D602 pad 2's exact centre. Its
        # plated pad already joins both layers; the additional via is redundant.
        tracks = list(board.GetTracks())
        KEEP.extend(tracks)
        for t in tracks:
            if isinstance(t, p.PCB_VIA) and t.GetNetname() == '-15V':
                pos = t.GetPosition()
                if pos.x == p.FromMM(45.5) and pos.y == p.FromMM(44):
                    board.Remove(t)
                    changes.append([name, '-15V', 'removed redundant via inside D602 pad 2'])
    p.SaveBoard(str(path), board)
(ROOT / 'review/layout-corrections.json').write_text(json.dumps(changes, indent=2) + '\n')
