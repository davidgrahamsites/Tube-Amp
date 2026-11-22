"""Move C321 1mm toward the top edge to clear CLK_REV after larger-pad integration."""
from pathlib import Path
import hashlib
import json
import sys
import pcbnew as p
root = Path(__file__).resolve().parents[1]
path = root / 'boards/Renegade_Control.kicad_pcb'
out = root / 'review/c321-clearance-repair.json'
refine = '--refine' in sys.argv
prior = json.loads(out.read_text()) if out.exists() else None
assert (prior and not prior.get('refinement')) if refine else not prior, 'Repair stage already applied'
before = hashlib.sha256(path.read_bytes()).hexdigest()
project = path.with_suffix('.kicad_pro')
project_bytes = project.read_bytes()
b = p.LoadBoard(str(path))
f = next(f for f in b.GetFootprints() if f.GetReference() == 'C321')
old = {pad.GetNumber(): pad.GetPosition() for pad in f.Pads()}
assert p.ToMM(f.GetPosition().y) == (43.375 if refine else 44.375)
delta = [-0.5, 0] if refine else [0, -1]
f.SetPosition(f.GetPosition() + p.VECTOR2I(*[p.FromMM(v) for v in delta]))
for pad in f.Pads():
    for t in b.GetTracks():
        if t.GetNetCode() != pad.GetNetCode(): continue
        if t.GetStart() == old[pad.GetNumber()]: t.SetStart(pad.GetPosition())
        if t.GetEnd() == old[pad.GetNumber()]: t.SetEnd(pad.GetPosition())
p.SaveBoard(str(path), b)
project.write_bytes(project_bytes)
entry = {'reason': 'CLK_REV-to-C321 pad2 clearance after exact 1.8mm pads',
 'offset_mm': delta, 'before_sha256': before, 'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
 'verification': 'Run fresh native DRC and pad/net audit'}
if refine:
    prior['refinement'] = entry
    entry = prior
out.write_text(json.dumps(entry, indent=2)+'\n')
