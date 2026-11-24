"""Read-only candidate/native mismatch screen; run with KiCad Python.

Input: exact candidate drawing extraction and current Power board.
Output: review/fc6136-fit.json. A successful execution can report a rejected fit.
No candidate adoption, drill sizing or tolerance approval is performed here.
"""
from pathlib import Path
from itertools import combinations
import hashlib
import json
import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xy(v):
    return [round(pcb.ToMM(v.x), 6), round(pcb.ToMM(v.y), 6)]


def pitch_impossible(pitch, hole, required_min):
    # Even zero-diameter straight leads cannot reach farther than the two
    # outside hole edges. This is rejection only, never acceptance of a fit.
    return pitch + hole < required_min


def overlap(a, b):
    return [round(min(a[i+2], b[i+2]) - max(a[i], b[i]), 6) for i in (0, 1)]


def main():
    contract = REPO/'engineering/component-selection/fc6136-fit-contract.json'
    data = json.loads(contract.read_text())
    drawing = REPO/data['source']
    board_path = ROOT/'boards/Renegade_Power.kicad_pcb'
    before = sha(board_path)
    board = pcb.LoadBoard(str(board_path))
    rows = []
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        if ref not in data['references']:
            continue
        assert footprint.GetOrientationDegrees() in (0, 180), 'Extend projection adapter for other rotations'
        pads = list(footprint.Pads())
        assert len(pads) == 4
        coords = [xy(p.GetPosition()) for p in pads]
        axes = [sorted(set(c[i] for c in coords)) for i in (0, 1)]
        assert all(len(v) == 2 for v in axes), 'Expected four-corner grid'
        assert len({tuple(c) for c in coords}) == 4
        pitch = [round(v[1]-v[0], 6) for v in axes]
        drills = [xy(p.GetDrillSize()) for p in pads]
        assert all(p.GetDrillShape() == pcb.PAD_DRILL_SHAPE_CIRCLE for p in pads)
        assert all(d[0] == d[1] for d in drills)
        minimum = [v-t for v, t in zip(data['pitch_nominal_mm'], data['pitch_tolerance_plus_minus_mm'])]
        rejected = [pitch_impossible(pitch[i], max(d[i] for d in drills), minimum[i]) for i in (0, 1)]
        centre = [sum(c[i] for c in coords)/4 for i in (0, 1)]
        size = [v+t for v, t in zip(data['body_nominal_W_T_H_mm'], data['body_tolerance_plus_minus_mm'])]
        bounds = [centre[0]-size[0]/2, centre[1]-size[1]/2, centre[0]+size[0]/2, centre[1]+size[1]/2]
        rows.append(dict(reference=ref, native_footprint=footprint.GetFPID().GetUniStringLibId(),
                         pitch_mm=pitch, pad_centroid_mm=centre,
                         drill_sizes_mm=drills, impossible_straight_lead_fit_axes=rejected,
                         candidate_max_body_bounds_mm=bounds, candidate_max_body_height_mm=size[2],
                         pads=[dict(number=p.GetNumber(), at_mm=xy(p.GetPosition()), net=p.GetNetname()) for p in pads]))
    assert {r['reference'] for r in rows} == set(data['references'])
    collisions = []
    for a, b in combinations(rows, 2):
        common = overlap(a['candidate_max_body_bounds_mm'], b['candidate_max_body_bounds_mm'])
        if min(common) > 0:
            collisions.append(dict(references=[a['reference'], b['reference']], overlap_xy_mm=common))
    controls = dict(reject_wrong_pitch=pitch_impossible(10.2, 1.8, 19.8),
                    aligned_pitch_not_rejected=not pitch_impossible(20.3, 1.8, 19.8),
                    touching_boxes_not_collision=min(overlap([0, 0, 2, 2], [2, 0, 4, 2])) == 0,
                    overlapping_boxes_detected=overlap([0, 0, 2, 2], [1, 1, 3, 3]) == [1, 1],
                    native_unchanged=sha(board_path) == before)
    assert all(controls.values())
    result = dict(scope='FC6136 candidate rejection screen against current native Power board; not universal component fit',
                  source_hashes={str(p.relative_to(REPO)): sha(p) for p in [contract, drawing, board_path, Path(__file__)]},
                  controls=controls, audit_completed=True,
                  candidate_can_drop_into_native=not any(any(r['impossible_straight_lead_fit_axes']) for r in rows) and not collisions,
                  rows=sorted(rows, key=lambda r: r['reference']), projected_body_collisions=collisions,
                  projection_assumption=data['body_projection_assumption'], pending=data['pending'],
                  native_modified=False, fabrication_ready=False)
    (ROOT/'review/fc6136-fit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ['audit_completed', 'candidate_can_drop_into_native', 'controls', 'projected_body_collisions']}, indent=2))


if __name__ == '__main__':
    main()
