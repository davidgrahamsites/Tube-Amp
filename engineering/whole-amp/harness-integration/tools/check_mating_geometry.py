#!/usr/bin/env python3
"""Resolve candidate connector datums; never certify an unplaced assembly."""
import hashlib
import json
from pathlib import Path
import pcbnew

MODULE = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edge_screen(edge_y, peg_y, maximum):
    distance = peg_y - edge_y
    return 0 <= distance <= maximum


def main():
    spec_path = MODULE / 'mating-geometry.json'
    contract_path = MODULE / 'connector-contract.json'
    spec = json.loads(spec_path.read_text())
    contract = json.loads(contract_path.read_text())
    h, m = spec['header'], spec['mate']
    sources = {s['file']: sha(MODULE / s['file']) for s in spec['sources']}
    assert all(sources[s['file']] == s['sha256'] for s in spec['sources'])
    c = contract['candidate']
    fp_path = Path(c['native_library']) / (c['footprint'] + '.kicad_mod')
    fp = pcbnew.FootprintLoad(c['native_library'], c['footprint'])
    points = []
    for item in fp.GraphicalItems():
        if isinstance(item, pcbnew.PCB_SHAPE) and item.GetLayer() == pcbnew.F_Fab:
            for p in (item.GetStart(), item.GetEnd()):
                points.append((pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)))
    low = [min(p[i] for p in points) for i in (0, 1)]
    high = [max(p[i] for p in points) for i in (0, 1)]
    peg = next(p for p in fp.Pads() if p.GetNumber() == '')
    peg_y = pcbnew.ToMM(peg.GetPosition().y)
    front = h['peg_y_mm'] - h['front_to_peg_nominal_mm']
    rear = front + h['front_to_rear_body_nominal_mm']
    width = h['body_A_nominal_mm'] + 2*h['side_step_each_nominal_mm']
    mate_exit = rear - m['right_angle_mated_length_mm']
    edge_min = peg_y - h['edge_to_peg_max_mm']
    comparisons = {
        'peg_y_matches_library': abs(peg_y-h['peg_y_mm']) < 1e-6,
        'front_matches_library': abs(front-low[1]) < 1e-6,
        'rear_matches_library': abs(rear-high[1]) < 1e-6,
        'stepped_width_matches_library': abs(width-(high[0]-low[0])) < 1e-6,
        'edge_limit_matches_contract': h['edge_to_peg_max_mm'] == c['board_edge_limit_mm'],
        'header_only_courtyard_not_mate': mate_exit < front,
    }
    assert all(comparisons.values()), comparisons
    controls = {
        'at_limit': edge_screen(edge_min, peg_y, h['edge_to_peg_max_mm']),
        'one_micron_over_limit': edge_screen(edge_min-.001, peg_y, h['edge_to_peg_max_mm']),
        'edge_past_peg': edge_screen(peg_y+.001, peg_y, h['edge_to_peg_max_mm']),
        # Mistaking pin row y=0 for the peg gives edge=-10.16; using the
        # front face as datum can instead permit a genuinely invalid edge.
        'incorrect_front_datum_example': edge_screen(front-10, peg_y, h['edge_to_peg_max_mm']),
    }
    assert list(controls.values()) == [True, False, False, False]
    paths = sorted((MODULE.parent / 'pcb-measured-r/boards').glob('*.kicad_pcb'))
    native = {str(p.relative_to(MODULE.parent)): sha(p) for p in paths}
    assert len(native) == 4
    result = {
        'id': spec['id'], 'inputs_sha256': {**sources, 'mating-geometry.json': sha(spec_path),
            'connector-contract.json': sha(contract_path), 'installed_footprint': sha(fp_path),
            'factory': sha(Path(__file__))},
        'nominal_library_comparisons': comparisons, 'edge_controls': controls,
        'derived_mm': {'header_front_y': round(front, 6), 'header_rear_y': round(rear, 6),
            'header_stepped_width': round(width, 6), 'mate_wire_exit_y': round(mate_exit, 6),
            'mate_extension_beyond_header_front': round(front-mate_exit, 6),
            'mating_side_edge_minimum_y': round(edge_min, 6)},
        'native_board_sha256': native, 'actual_placements_checked': 0,
        'evidence_checks_pass': True, 'assembled_fit_qualified': False,
        'native_adoption': False, 'unresolved': spec['limits'],
    }
    (MODULE/'results/mating-geometry-checks.json').write_text(json.dumps(result, indent=2)+'\n')
    # Side-view coordinates: horizontal is footprint y; vertical is height z.
    sx = lambda y: 90+(y+20)*21
    sz = lambda z: 325-z*16
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="480" viewBox="0 0 900 480">
<rect width="900" height="480" fill="#f5f3ed"/>
<g font-family="sans-serif" fill="#182c37">
<text x="35" y="35" font-size="22">HI-004 · Right-angle pot connector</text>
<text x="35" y="65" font-size="15">Nominal side-view bounds only · No wire, tolerance or withdrawal allowance</text>
<rect x="{sx(mate_exit):.2f}" y="{sz(m['right_angle_mated_height_mm']):.2f}" width="{m['right_angle_mated_length_mm']*21:.2f}" height="{m['right_angle_mated_height_mm']*16:.2f}" fill="#e4b95b" fill-opacity="0.18" stroke="#94661a" stroke-width="2" stroke-dasharray="7 5"/>
<rect x="{sx(front):.2f}" y="{sz(h['body_height_nominal_mm']):.2f}" width="{(rear-front)*21:.2f}" height="{h['body_height_nominal_mm']*16:.2f}" fill="#418398" fill-opacity="0.35" stroke="#245b6c" stroke-width="2"/>
<line x1="{sx(-10):.2f}" y1="325" x2="{sx(6):.2f}" y2="325" stroke="#182c37" stroke-width="5"/>
<line x1="{sx(peg_y):.2f}" y1="300" x2="{sx(peg_y):.2f}" y2="383" stroke="#182c37" stroke-dasharray="4 4"/>
<circle cx="{sx(peg_y):.2f}" cy="325" r="5" fill="#182c37"/>
<line x1="{sx(edge_min):.2f}" y1="375" x2="{sx(peg_y):.2f}" y2="375" stroke="#94661a" stroke-width="2"/>
<line x1="{sx(edge_min):.2f}" y1="315" x2="{sx(edge_min):.2f}" y2="385" stroke="#94661a" stroke-dasharray="4 4"/>
<text x="35" y="110" font-size="16">Amber: mated family envelope, 17.56 × 10.81 mm</text>
<text x="{sx(front)+8:.2f}" y="265" font-size="15">Header body</text>
<text x="{sx(-10):.2f}" y="350" font-size="14">Example PCB edge y = −10</text>
<text x="{sx(edge_min):.2f}" y="405" font-size="15">10.16 mm maximum: board edge to peg centre</text>
<text x="35" y="445" font-size="15">Mate adds {front-mate_exit:.2f} mm beyond header front; latching callout is 11.0 mm above PCB.</text>
</g></svg>'''
    (MODULE/'results/mating-geometry.svg').write_text(svg+'\n')
    assert native == {str(p.relative_to(MODULE.parent)): sha(p) for p in paths}
    print(json.dumps({'comparisons':comparisons,'controls':controls,'derived_mm':result['derived_mm'],
                      'assembled_fit_qualified':False}, indent=2))


if __name__ == '__main__':
    main()
