"""Read-only P057 nominal and rigid-lead rejection checks. Run with KiCad Python."""
from pathlib import Path
import hashlib
import itertools
import json
import math
import pcbnew as pcb
import wx

MODULE = Path(__file__).resolve().parents[1]
REPO = MODULE.parents[2]
BOARD = REPO / 'engineering/whole-amp/pcb-measured-r/boards/Renegade_Power.kicad_pcb'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xy(point):
    return [round(pcb.ToMM(point.x), 6), round(pcb.ToMM(point.y), 6)]


def opposite_pair_reject(board_pitch, part_pitch, diameter, hole):
    # Necessary condition for any rotation/translation: opposite lead centres
    # cannot be farther apart than hole centres plus available diametral play.
    return math.hypot(*part_pitch) > math.hypot(*board_pitch) + hole - diameter + 1e-9


def box(centre, size):
    return [centre[0]-size[0]/2, centre[1]-size[1]/2,
            centre[0]+size[0]/2, centre[1]+size[1]/2]


def separation(a, b):
    dx = max(a[0]-b[2], b[0]-a[2], 0)
    dy = max(a[1]-b[3], b[1]-a[3], 0)
    overlap = min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])
    return {'overlap': overlap, 'edge_distance_mm': round(math.hypot(dx, dy), 6)}


def main():
    app = wx.App(False)
    ppath = MODULE / 'panasonic-contract.json'
    cpath = MODULE.parent / 'fc6136-fit-contract.json'
    pan = json.loads(ppath.read_text())
    crc = json.loads(cpath.read_text())
    before = sha(BOARD)
    board = pcb.LoadBoard(str(BOARD))
    rows = []
    for fp in board.GetFootprints():
        if fp.GetReference() not in crc['references']:
            continue
        assert fp.GetOrientationDegrees() in (0, 180)
        assert fp.GetFPID().GetUniStringLibId() == 'Renegade_Whole:Panasonic_EZPV60506MTC'
        pads = list(fp.Pads())
        positions = [xy(p.GetPosition()) for p in pads]
        assert len(pads) == 4 and len(set(map(tuple, positions))) == 4
        axes = [sorted(set(p[i] for p in positions)) for i in (0, 1)]
        assert all(len(a) == 2 for a in axes)
        pitch = [round(a[1]-a[0], 6) for a in axes]
        drills = [xy(p.GetDrillSize()) for p in pads]
        assert all(p.GetDrillShape() == pcb.PAD_DRILL_SHAPE_CIRCLE for p in pads)
        assert all(d == drills[0] and d[0] == d[1] for d in drills)
        centre = [sum(p[i] for p in positions)/4 for i in (0, 1)]
        witness = [x+t for x, t in zip(pan['pitch_nominal_mm'], pan['pitch_tolerance_plus_minus_mm'])]
        dmax = pan['lead_nominal_diameter_mm'] + pan['lead_diameter_tolerance_plus_minus_mm']
        max_pan = [v+t for v, t in zip(pan['body_nominal_L_W_H_mm'], pan['body_tolerance_plus_minus_mm'])]
        max_crc = [v+t for v, t in zip(crc['body_nominal_W_T_H_mm'], crc['body_tolerance_plus_minus_mm'])]
        rows.append({'reference': fp.GetReference(), 'pitch_mm': pitch, 'hole_diameter_nominal_mm': drills[0][0],
                     'pads': [{'number': p.GetNumber(), 'at_mm': xy(p.GetPosition()), 'net': p.GetNetname()} for p in pads],
                     'panasonic_nominal_pitch_matches': pitch == pan['pitch_nominal_mm'],
                     'panasonic_max_lead_diameter_mm': dmax,
                     'panasonic_rigid_max_pitch_witness_mm': witness,
                     'panasonic_rigid_witness_rejected_even_with_nominal_holes': opposite_pair_reject(pitch, witness, dmax, drills[0][0]),
                     'panasonic_max_body_box_mm': box(centre, max_pan),
                     'crc_max_body_box_mm': box(centre, max_crc)})
    assert {r['reference'] for r in rows} == set(crc['references'])
    pairs = []
    for a, b in itertools.combinations(sorted(rows, key=lambda r: r['reference']), 2):
        pairs.append({'references': [a['reference'], b['reference']],
                      'panasonic': separation(a['panasonic_max_body_box_mm'], b['panasonic_max_body_box_mm']),
                      'crc': separation(a['crc_max_body_box_mm'], b['crc_max_body_box_mm'])})
    controls = {
        'nominal_max_leads_not_rejected': not opposite_pair_reject([52.5, 10.2], [52.5, 10.2], 1.4, 1.8),
        'large_holes_not_rejected': not opposite_pair_reject([52.5, 10.2], [53.5, 11.2], 1.4, 3.2),
        'wide_pitch_rejected': opposite_pair_reject([52.5, 10.2], [53.5, 11.2], 1.4, 1.8),
        'touching_not_overlap': not separation([0, 0, 2, 2], [2, 0, 4, 2])['overlap'],
        'overlap_detected': separation([0, 0, 2, 2], [1, 1, 3, 3])['overlap'],
        'native_unchanged': sha(BOARD) == before}
    assert all(controls.values())
    inputs = [BOARD, ppath, cpath, MODULE / 'evidence/Panasonic-EZPV-R9.pdf', Path(__file__)]
    result = {'scope': 'Four P057 packages only; rigid insertion rejection and centered body screen, not footprint approval',
              'source_sha256': {str(p.relative_to(REPO)): sha(p) for p in inputs}, 'controls': controls,
              'rows': sorted(rows, key=lambda r: r['reference']), 'body_pairs': pairs,
              'panasonic_centered_rectangular_grid_hole_diameter_without_pcb_tolerance_or_allowance_mm':
                  round(dmax + math.hypot(*pan['pitch_tolerance_plus_minus_mm']), 6),
              'that_diameter_is_a_geometric_example_not_a_drill_recommendation': True,
              'native_modified': False, 'candidate_adopted': False, 'fabrication_ready': False}
    (MODULE / 'results/package-checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'controls': controls, 'rows': len(rows), 'body_pairs': pairs}, indent=2))


if __name__ == '__main__':
    main()
