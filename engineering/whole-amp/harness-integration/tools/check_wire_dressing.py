#!/usr/bin/env python3
"""Export axial wire-restraint reservations without approving physical fit."""
import hashlib
import json
import math
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restraint_screen(distance_mm, minimum_mm):
    if distance_mm is None:
        return 'unknown'
    if not math.isfinite(distance_mm) or distance_mm < 0:
        return 'invalid'
    return 'outside_reserve' if distance_mm >= minimum_mm else 'inside_reserve'


def main():
    inputs = {n: MODULE/n for n in ('wire-dressing.json', 'mating-geometry.json', 'connector-contract.json')}
    w, g, c = (json.loads(inputs[n].read_text()) for n in inputs)
    assert w['circuit_range'][0] <= c['candidate']['cavities'] <= w['circuit_range'][1]
    assert g['header']['part'] == c['candidate']['header']
    assert g['mate']['part'] == c['candidate']['housing']
    reserve = w['planning_policy']['axial_reservation_mm']
    assert reserve >= w['relaxed_wire_minimum_mm'] > 0
    assert w['planning_policy']['direction'] == [0, -1, 0]
    h = g['header']
    front = h['peg_y_mm'] - h['front_to_peg_nominal_mm']
    rear = front + h['front_to_rear_body_nominal_mm']
    exit_y = rear - g['mate']['right_angle_mated_length_mm']
    restraint_y = exit_y-reserve
    # Distances apply to the nearest point of a restraint, not its centre.
    derived = {k: round(v, 6) for k, v in {
        'header_front_y': front, 'header_rear_y': rear,
        'housing_wire_exit_y': exit_y,
        'nearest_allowed_restraint_y_max': restraint_y,
        'header_front_to_restraint': front-restraint_y,
        'header_rear_to_restraint': rear-restraint_y,
        'axial_wire_reserve': reserve}.items()}
    cases = [(None, 'unknown'), (0, 'inside_reserve'), (reserve-.001, 'inside_reserve'),
             (reserve, 'outside_reserve'), (reserve+.001, 'outside_reserve'),
             (-1, 'invalid'), (float('inf'), 'invalid')]
    controls = []
    for value, expected in cases:
        actual = restraint_screen(value, reserve)
        assert actual == expected
        controls.append({'distance_mm': value if value is None or math.isfinite(value) else 'infinity',
                         'expected': expected, 'actual': actual})
    # A 2 mm wide tie centred at the nominal boundary infringes by 1 mm.
    tie_nearest = reserve-2/2
    assert restraint_screen(tie_nearest, reserve) == 'inside_reserve'
    controls.append({'case': 'tie_centre_is_not_nearest_edge', 'nearest_edge_mm': tie_nearest,
                     'actual': restraint_screen(tie_nearest, reserve), 'expected': 'inside_reserve'})
    interfaces = [{'pot': pot, 'board_owner': board, 'candidate_header': h['part'],
                   'candidate_mate': g['mate']['part'], 'local_coordinates': g['coordinates'],
                   'axial_reservation_mm': derived, 'placement_transform': None,
                   'restraint_geometry': None, 'installed_check': 'not_evaluated'}
                  for pot, board in c['panel_pots'].items()]
    boards = sorted((MODULE.parent/'pcb-measured-r/boards').glob('*.kicad_pcb'))
    assert len(boards) == 4
    result = {'id': w['id'], 'inputs_sha256': {n: sha(p) for n,p in inputs.items()},
              'factory_sha256': sha(Path(__file__)), 'source': w['source'],
              'derived_nominal_mm': derived, 'interfaces': interfaces, 'restraint_controls': controls,
              'native_board_sha256': {str(p.relative_to(MODULE.parent)): sha(p) for p in boards},
              'actual_placements_checked': 0, 'dimensional_illustration_verified': False,
              'wire_and_service_qualification': w['service_gates'],
              'evidence_checks_pass': True, 'populated_fit_qualified': False,
              'native_adoption': False}
    (MODULE/'results/wire-dressing-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    # Explanatory drawing; the wire band's height is not a qualified envelope.
    x=lambda y: 55+(y+32)*23
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="440" viewBox="0 0 960 440">
<rect width="960" height="440" fill="#f5f3ed"/>
<g font-family="sans-serif" fill="#182c37">
<text x="30" y="38" font-size="23">HI-005 · Reserve relaxed wire behind the plug</text>
<text x="30" y="68" font-size="16">Straight-exit planning assumption · Nominal axial dimensions · No fit release</text>
<rect x="{x(exit_y):.2f}" y="160" width="{(rear-exit_y)*23:.2f}" height="90" fill="#e4b95b" fill-opacity=".25" stroke="#94661a" stroke-dasharray="7 4"/>
<rect x="{x(front):.2f}" y="190" width="{(rear-front)*23:.2f}" height="60" fill="#418398" fill-opacity=".45" stroke="#245b6c"/>
<text x="{x(exit_y)+10:.2f}" y="145" font-size="16">Mated connector</text>
<line x1="{x(restraint_y):.2f}" x2="{x(exit_y):.2f}" y1="205" y2="205" stroke="#a65032" stroke-width="9"/>
<line x1="{x(restraint_y):.2f}" x2="{x(restraint_y):.2f}" y1="170" y2="280" stroke="#a65032" stroke-dasharray="5 4"/>
<line x1="{x(exit_y):.2f}" x2="{x(exit_y):.2f}" y1="195" y2="280" stroke="#94661a" stroke-dasharray="5 4"/>
<text x="{x(restraint_y)+12:.2f}" y="190" font-size="16">No tie / forced bend</text>
<text x="{x(restraint_y)+22:.2f}" y="240" font-size="17">12.70 mm reserve</text>
<text x="{x(restraint_y)-15:.2f}" y="310" font-size="15">Restraint edge ≤ {restraint_y:.2f}</text>
<text x="{x(exit_y)+5:.2f}" y="280" font-size="15">Wire exit {exit_y:.2f}</text>
<text x="{x(front)+5:.2f}" y="225" font-size="15">Header</text>
<text x="30" y="365" font-size="16">From header front to restraint: {front-restraint_y:.2f} mm nominal; add bends and removal space separately.</text>
<text x="30" y="400" font-size="15">Wire-band thickness is illustrative. Coordinates use pad 1 origin; wire exits toward negative y.</text>
</g></svg>'''
    (MODULE/'results/wire-dressing.svg').write_text(svg+'\n')
    print(json.dumps({'interfaces':len(interfaces),'controls':len(controls),'derived_mm':derived,
                      'actual_placements_checked':0,'populated_fit_qualified':False},indent=2))


if __name__ == '__main__':
    main()
