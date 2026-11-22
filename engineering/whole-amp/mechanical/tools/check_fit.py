"""Necessary geometric screens only; no installed assembly approval."""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[1]
r = json.loads((ROOT / 'fit-register.json').read_text())
boards = r['boards']
cab = r['cabinet']['published_external']
baf = r['baffle']
speaker = r['speaker_reference']
area = sum(v[0] * v[1] for v in boards.values())
top_area = cab['width'] * cab['depth_top']
offset = abs(baf['speaker_hole_circle_mm'] - speaker['bolt_circle_mm']) / 2
# Even a zero-diameter pin cannot pass through two non-overlapping holes.
hole_radii_sum = (baf['speaker_hole_diameter_mm'] + speaker['hole_diameter_mm']) / 2
tray = r['layout_options']['two_plane_board_only']['assumed_tray_mm']
gap = r['layout_options']['two_plane_board_only']['gap_mm']
planes = {}
for label in ['plane_A', 'plane_B']:
    names = r['layout_options']['two_plane_board_only'][label]
    width = sum(boards[n][0] for n in names) + gap
    depth = max(boards[n][1] for n in names)
    planes[label] = dict(boards=names, envelope_mm=[width, depth],
                         fits_assumed_tray=width <= tray[0] and depth <= tray[1])
result = {
    'scope': 'Dimension arithmetic; assumptions are not measured clearances',
    'single_plane_top_screen': {
        'board_area_mm2': area, 'external_top_area_mm2': top_area,
        'excess_mm2': area - top_area, 'passes': area <= top_area,
        'limit': 'Only one horizontal plane confined to exterior top footprint; not proof that every 3D arrangement fails'},
    'speaker_existing_holes': {
        'radial_mismatch_mm': offset, 'combined_hole_radii_mm': hole_radii_sum,
        'holes_overlap_even_with_zero_size_pin': offset <= hole_radii_sum,
        'verdict': 'FAIL for unchanged circular holes, same center and matching orientation'},
    'baffle_attachment_dimension_conflict_mm': 218 * 2 - (baf['width_mm'] - 2 * 20),
    'speaker_front_projection_only': {
        'left_margin_mm': baf['speaker_center_x_from_left_as_drawn_mm'] - speaker['outer_diameter_mm']/2,
        'right_margin_mm': baf['width_mm'] - baf['speaker_center_x_from_left_as_drawn_mm'] - speaker['outer_diameter_mm']/2,
        'top_bottom_margin_mm_assuming_centered_height': (baf['height_mm']-speaker['outer_diameter_mm'])/2,
        'installed_rear_clearance_mm': None},
    'two_plane_board_only': planes,
    'tank_screen': {'reference_bare_width_235_vs_baffle_width468_mm': 468 - 235,
                    'installed_floor_clearance': None,
                    'note': 'Baffle width is not a measured free floor dimension; cable/bag/feet/height still unknown'},
    'reference_tank_model_consistency': {
        'RL_equivalent_H_from_800ohm_58ohm_1kHz': math.sqrt(800**2 - 58**2)/(2*math.pi*1000),
        'ohm_from_150mH_58ohm_1kHz': math.hypot(58, 2*math.pi*1000*.15),
        'note': 'Legacy nominal L and Z do not define one exact constant-RL model; do not silently replace simulation model'},
    'assembly_fit_cleared': False,
    'missing_interfaces': r['unknowns']}
# Preserve the old catalogue comparison as history, never as the received envelope.
result['historical_reference_tank_screen'] = result.pop('tank_screen')
result['historical_reference_tank_screen']['scope'] = 'Historical catalogue arithmetic only; not received-unit dimensions'
tank = r.get('tank_received', {}).get('mechanical_measurements')
if tank:
    envelope = [tank[k] for k in ('T1_max_length_mm', 'T2_max_width_mm', 'T3_max_height_mm')]
    assert all(isinstance(x, (int, float)) and x > 0 for x in envelope)
    result['received_tank_screen'] = {
        'outer_envelope_mm': envelope,
        'reported_on': tank['reported_on'],
        'source': tank['source'],
        'datum_basis': tank['datum_basis'],
        'reported_uncertainty_mm': tank['reported_uncertainty_mm'],
        'bounding_plan_area_mm2': envelope[0] * envelope[1],
        'installed_floor_clearance': None,
        'fit_cleared': False,
        'note': 'Reported outer envelope only. Upper cabinet width/depth are not measured free floor space. Add actual plugged RCA leads, cable bends, mounting and assembly clearances.'}
result['speaker_existing_holes']['scope'] = 'HISTORICAL seller-drawing comparison only; not the received cabinet measurement'
measured = r['cabinet'].get('user_measurements', {})
c1 = measured.get('C1_opposite_hole_centres_mm')
c2 = measured.get('C2_opposite_hole_centres_mm')
if c1 is not None and c2 is not None:
    result['received_vs_drawing'] = {
        'source': 'User measurements; exact datums and uncertainty not independently inspected',
        'A_front_mm': measured['A_front_clear_width_mm'],
        'A_rear_mm': measured['A_rear_clear_width_mm'],
        'A_verdict': 'Not directly specified: drawing508 is outside width;468 is separate baffle width',
        'B_mm': measured['B_rear_edge_depth_mm'],
        'B_verdict': 'Not directly specified: drawing215/242 are external top/bottom depths',
        'C1_mm': c1, 'C2_mm': c2,
        'C_pair_difference_mm': abs(c1-c2),
        'drawing_speaker_circle_mm': baf['speaker_hole_circle_mm'],
        'C1_minus_drawing_mm': c1-baf['speaker_hole_circle_mm'],
        'C2_minus_drawing_mm': c2-baf['speaker_hole_circle_mm'],
        'C_verdict': 'DIFFERS' if any(c != baf['speaker_hole_circle_mm'] for c in (c1,c2)) else 'Numerical agreement; manufacturing tolerance not supplied',
        'design_basis': 'Received user-reported spacing; do not drill or select from the conflicting312mm drawing',
        'reference_speaker_radial_offset_each_pair_mm': [abs(c-speaker['bolt_circle_mm'])/2 for c in (c1,c2)],
        'reference_speaker_fit': 'Not qualified: actual studs/holes, cutout, frame and installed depth still need checking'}
aperture = measured.get('S1_aperture')
if aperture:
    result['received_speaker_aperture'] = {
        'reported_diameter_mm': aperture['diameter_mm'],
        'drawing_cutout_diameter_mm': baf['cutout_diameter_mm'],
        'difference_mm': aperture['diameter_mm'] - baf['cutout_diameter_mm'],
        'approximate': aperture['approximate'],
        'nominal_agreement': aperture['diameter_mm'] == baf['cutout_diameter_mm'],
        'source': aperture['source'],
        'fit_cleared': False,
        'note': 'Cutout agreement only; mounting-hole pattern, exact template, basket and installed depth remain separate checks.'}
assert area == 109900
assert offset == 7.5
assert result['baffle_attachment_dimension_conflict_mm'] == 8
(ROOT/'review/fit-screen.json').write_text(json.dumps(result, indent=2)+'\n')
print('Historical drawing screens retained. Received-cabinet comparison:', result.get('received_vs_drawing',{}).get('C_verdict','pending'), '; whole assembly NOT CLEARED.')
