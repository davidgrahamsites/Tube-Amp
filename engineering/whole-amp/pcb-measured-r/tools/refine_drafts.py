"""Keep BOM metadata out of silkscreen; correct two measured courtyard conflicts."""
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
    for f in board.GetFootprints():
        fields = list(f.GetFields())
        KEEP.extend(fields)
        for field in fields:
            if field.GetName() not in ['Reference', 'Value']:
                field.SetVisible(False)
        if name == 'Reverb' and f.GetReference() in ['RV601', 'C612']:
            x, y = {'RV601': (82, 22), 'C612': (52, 54)}[f.GetReference()]
            f.SetPosition(p.VECTOR2I(p.FromMM(x), p.FromMM(y)))
            changes.append({'reference': f.GetReference(), 'position_mm': [x, y],
                            'reason': 'Separate maximum-body courtyards'})
    if name == 'Reverb':
        tracks = list(board.GetTracks())
        KEEP.extend(tracks)
        for track in tracks:
            board.Remove(track)
        for item in board.GetDrawings():
            if isinstance(item, p.PCB_TEXT) and 'SPRING v0.4' in item.GetText():
                item.SetText('RENEGADE 600R-1 / LV DRAFT')
    p.SaveBoard(str(path), board)
(ROOT / 'review/refinement.json').write_text(json.dumps({
    'metadata_fields_hidden': ['Selected_MPN', 'Package_Status', 'Status'],
    'reason': 'BOM/properties retained; engineering notes are not component silkscreen',
    'placements': changes, 'requires_reverb_reroute': True}, indent=2) + '\n')
