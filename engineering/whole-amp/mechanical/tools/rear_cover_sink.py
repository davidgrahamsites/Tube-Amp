"""CB-009 independent check: Fischer SK 81 50 SA clearance to the upper rear cover.

Reads ../fit-register.json (read-only). Writes ../review/rear-cover-sink.json and
../review/rear-cover-sink.svg. Arithmetic screen only. No CAD, no native edit, no fit release.

Every length is millimetres. Depth axis x: 0 at the baffle rear face, positive toward the
rear. Height axis z: 0 at the underside of the cabinet top, positive downward.
Change PARAM and rerun; nothing else is hard-coded in the checks.
"""
import hashlib
import itertools
import json
from pathlib import Path

from rear_cover_geometry import (
    A, B, DRAW, G, NOTCH,
    OUT_JSON, OUT_SVG, P, P2, PARAM,
    REGISTER, SOURCES, between_cleats_photo, c_hi, c_lo,
    c_mid, cover, datum, draw_baffle_to_cleat_top, draw_baffle_to_edge_top,
    guard_h, guard_w, near_fins, need_contact,
    need_service, reg, sink_max, slope, taper,
    taper_cases
)

# ------------------------------------------------------------- 5. fit checks
checks = []


def add(cid, title, verdict, margin=None, note=''):
    checks.append({'id': cid, 'title': title, 'verdict': verdict,
                   'margin_mm': None if margin is None else round(margin, 2), 'note': note})


def interior(h, c, dB=0.0, dz=0.0):
    """Baffle rear face to cover inner face at the sink height."""
    edge = B + dB + dz if h == 'H1' else B + dB + dz + DRAW['cleat_depth'] + DRAW['rear_recess']
    return edge - c


def behind_tray(h, c, dB=0.0, dz=0.0, tray=None):
    return interior(h, c, dB, dz) - P['front_gap'] - (P['tray_depth'] if tray is None else tray)


scen = {}
for h in ('H1', 'H2'):
    cen = behind_tray(h, c_mid)
    lo = min(behind_tray(h, c, dB, dz) for c, dB, dz in itertools.product(
        (c_lo, c_hi), (-P['u_B'], P['u_B']), taper_cases.values()))
    hi = max(behind_tray(h, c, dB, dz) for c, dB, dz in itertools.product(
        (c_lo, c_hi), (-P['u_B'], P['u_B']), taper_cases.values()))
    lo_local = min(behind_tray(h, c, dB, 0.0) for c, dB in itertools.product((c_lo, c_hi), (-P['u_B'], P['u_B'])))
    scen[h] = {
        'interior_baffle_to_cover_mm': round(interior(h, c_mid), 2),
        'space_behind_130_tray_mm': {'central': round(cen, 2), 'worst_B_at_sink_height': round(lo_local, 2),
                                     'worst_all_cases': round(lo, 2), 'best_all_cases': round(hi, 2)},
        'margin_guarded_contact_mm': round(cen + P['front_gap'] - need_contact, 2),
        'margin_guarded_service_mm': {'central': round(cen - need_service, 2),
                                      'worst_B_at_sink_height': round(lo_local - need_service, 2),
                                      'worst_all_cases': round(lo - need_service, 2),
                                      'best_all_cases': round(hi - need_service, 2)},
        'pocket_depth_needed_mm': {'central': round(max(0.0, need_service - cen), 1),
                                   'worst_B_at_sink_height': round(max(0.0, need_service - lo_local), 1),
                                   'worst_all_cases': round(max(0.0, need_service - lo), 1)},
        'max_tray_depth_no_pocket_mm': {'central': round(P['tray_depth'] + cen - need_service, 1),
                                        'worst_B_at_sink_height': round(P['tray_depth'] + lo_local - need_service, 1),
                                        'worst_all_cases': round(P['tray_depth'] + lo - need_service, 1)},
        'cleat_front_from_baffle_mm': round(interior(h, DRAW['rear_recess']) - DRAW['cleat_depth'], 1),
    }
    scen[h]['tray_rear_past_cleat_front_mm'] = round(
        P['front_gap'] + P['tray_depth'] - scen[h]['cleat_front_from_baffle_mm'], 1)

cb008_margin = B - P['tray_depth'] - need_contact
add('R0', 'CB-008 depth margin for the 130 tray (+%.2f) holds with the cover on' % cb008_margin, 'FAIL',
    scen['H1']['margin_guarded_contact_mm'],
    'CB-008 used B - 130 - %.2f with zero cover thickness and zero gaps. Subtract the cover (%.0f central) '
    'under the recorded datum H1 and the guard is %.1f mm INTO the cover.' % (need_contact, c_mid,
                                                                            -scen['H1']['margin_guarded_contact_mm']))
for h in ('H1', 'H2'):
    m = scen[h]['margin_guarded_service_mm']
    v = 'FAIL' if m['central'] < 0 else ('CONDITIONAL' if m['worst_all_cases'] < 0 else 'PASS')
    add('R1-' + h, 'Guarded sink on the flat rear wall of the 130 tray, cover ON (%s)' % h, v, m['central'],
        'Need %.2f = bracket %.1f + sink %.2f + guard %.1f + cover gap %.1f. Behind tray %.1f central. '
        'Range of margin %.1f to %.1f over cover, tape and B-height cases.'
        % (need_service, P['wall_bracket'], sink_max, G, P['cover_gap_min'],
           scen[h]['space_behind_130_tray_mm']['central'], m['worst_all_cases'], m['best_all_cases']))
bare = scen['H1']['space_behind_130_tray_mm']['central'] - (P['wall_bracket'] + sink_max)
add('R2', 'Bare sink, no guard, flat rear wall, cover ON (H1)', 'FAIL', bare - P['cover_gap_min'],
    'Fin tips %.1f mm from the wood before the %.1f mm gap rule. No guard for service with the cover off.'
    % (bare, P['cover_gap_min']))

# stepped pocket: a full-height vertical channel in the rear wall, open top and bottom
pocket = {}
for h in ('H1', 'H2'):
    p = scen[h]['pocket_depth_needed_mm']
    w = guard_w + 2 * P['side_clear']
    left = {k: round(P['tray_depth'] - v - 2 * P['tray_wall'], 1) for k, v in p.items()}
    pocket[h] = {
        'depth_mm': p, 'width_mm': round(w, 1), 'height_mm': 'full tray height %g, open top and bottom' % P['tray_height'],
        'internal_depth_left_at_pocket_mm': left,
        'plan_area_lost_mm2': {k: round(v * w) for k, v in p.items()},
        'share_of_tray_plan_percent': {k: round(100 * v * w / (P['tray_width'] * P['tray_depth']), 2)
                                       for k, v in p.items()},
    }
p1 = pocket['H1']
add('R3', 'Stepped pocket in the rear wall, 130 tray kept (H1)', 'CONDITIONAL', None,
    'Pocket %.1f deep central, %.1f if B was taken at sink height with worst tape/cover, %.1f worst of all cases; '
    '%.1f wide. Leaves %.1f / %.1f / %.1f mm internal depth over that width. Costs %.2f%% of tray plan area '
    '(central). The PA carrier sits on the inside of the pocket wall.'
    % (p1['depth_mm']['central'], p1['depth_mm']['worst_B_at_sink_height'], p1['depth_mm']['worst_all_cases'],
       p1['width_mm'], p1['internal_depth_left_at_pocket_mm']['central'],
       p1['internal_depth_left_at_pocket_mm']['worst_B_at_sink_height'],
       p1['internal_depth_left_at_pocket_mm']['worst_all_cases'], p1['share_of_tray_plan_percent']['central']))
t1 = scen['H1']['max_tray_depth_no_pocket_mm']
add('R4', 'Shorter tray, flat rear wall, no pocket (H1)', 'FAIL', t1['central'] - P['tray_depth'],
    'Tray depth must drop to %.1f central (%.1f / %.1f worst). That removes %.0f mm from the whole 440 mm width '
    '(%.0f mm2) to serve a %.0f mm wide part. Present Main is 140 deep and Control 110: neither depth survives.'
    % (t1['central'], t1['worst_B_at_sink_height'], t1['worst_all_cases'], P['tray_depth'] - t1['central'],
       (P['tray_depth'] - t1['central']) * P['tray_width'], guard_w))

# withdrawal and cover independence
add('W1', 'Rear cover removal independent of sink and guard (FB-070)', 'PASS', P['cover_gap_min'],
    'Sink and guard fasten to the cassette only. The cover seats in the rear recess and leaves rearward. Holds '
    'only while the %.1f mm guard-to-cover gap is kept; no part may bear on or fasten to the cover.' % P['cover_gap_min'])
wm = between_cleats_photo - P['tray_width']
add('W2', '440 mm tray withdraws rearward between the side cleats', 'FAIL' if wm < -8 else 'CONDITIONAL', wm,
    'Photo estimate %.0f mm between cleats (+/-8, low confidence) against a 440 mm tray. Measured A = %g is the '
    'wall-to-wall width, per the same photo scale. Measure the cleat-to-cleat width before fixing tray width.'
    % (between_cleats_photo, A))
for h in ('H1', 'H2'):
    over = scen[h]['tray_rear_past_cleat_front_mm']
    add('W3-' + h, 'Tray rear corners clear the cleat front faces (%s)' % h,
        'FAIL' if over > 0 else 'PASS', -over,
        'Cleat front %.1f mm from the baffle; tray rear at %.1f. Applies only if the tray is wider than the '
        'cleat-to-cleat width.' % (scen[h]['cleat_front_from_baffle_mm'], P['front_gap'] + P['tray_depth']))
add('W4', 'Cassette with sink passes the upper-cover aperture height', 'NOT_EVALUABLE', None,
    'Upper cover height, lower cover top edge and chassis elevation are not in the register.')
add('W5', 'Sink fasteners', 'CONDITIONAL', None,
    'Base %.1f mm. M3 from inside the cassette into tapped base holes gives about 8 threads and nothing proud of '
    'the fins. Drilling/tapping is a modification of a stock part: order Fischer CNC option or accept it. Screws '
    'must be reachable with the cassette on the bench, not through the cover.' % P['sink_base'])
add('W6', 'Guard fastening', 'CONDITIONAL', None,
    'Guard %.1f x %.1f mm fastens to the cassette rear wall, bonded to chassis earth, open top and bottom. '
    'It must not reach the cover screws or cleats.' % (guard_w, guard_h))

# thermal and wood (not a fit result)
P_W = 2.844
thermal = {
    'power_W': P_W, 'cb007_installed_allocation_K_per_W': 4.0,
    'fischer_family_K_per_W': [1.9, 3.4],
    'bound_for_50mm': 'The 50 mm cut is no worse than the 37.5 mm figure if 3.4 K/W belongs to 37.5 mm. That '
                      'mapping is not printed on the page read. Value at 50 mm NOT READ.',
    'margin_to_allocation_K_per_W_if_3.4': round(4.0 - 3.4, 2),
    'sink_estimate_C_at_60C_air_and_4K_per_W': round(60 + 4.0 * P_W, 1),
    'air_path': 'Behind the cover the sink stands in a slot %.1f mm deep (base wall to wood, H1 central with '
                'pocket) between the cassette and the cover. Catalogue free-air figures do not apply. Inlet is '
                'the open back below the upper cover; outlet is the oval slots or the top of the gap. A pocket '
                'closed at top or bottom, or a control panel sealing the top, stops the chimney.'
                % (need_service - P['wall_bracket']),
    'wood': 'At about %.0f C metal and a %.1f mm gap the wood and covering are not a fire question. The open '
            'points are trapped warm air under the cabinet top, heat from the tubes into the same slot, and '
            'covering adhesive. Measure wood-face and local air temperature in the closed cabinet.'
            % (60 + 4.0 * P_W, P['cover_gap_min']),
    'verdict': 'HOLD. Installed K/W behind the cover is unproven.',
}
add('T1', 'Installed cooling behind the wooden cover', 'NOT_EVALUABLE', None, thermal['verdict'])

alternative = {
    'underside': 'Sink on the cassette underside, fins down, %.2f mm drop with guard. Independent of the rear '
                 'cover and of B. Fins-down is a poor natural-convection attitude and the air is cabinet air '
                 '(CB-008 C4c). Withdrawal must clear that drop over the lower cover edge: not measured.' % need_contact,
    'side_wall': 'Rejected by CB-008 C3: 27 mm total side spare.',
}

missing = [
    {'id': 'M1', 'cover': 'ON', 'what': 'Same-datum P2 pair',
     'how': 'One ruler placement at the opening centre. Zero on the cut wooden edge nearest the handle. Read '
            '(a) the inner edge of the cover top, (b) the outer face of the cover top, (c) the cabinet rear edge '
            '(hold a straightedge across the two side-wall rear edges and read where it crosses the ruler).',
     'gives': 'cover thickness = b - a; cover inset = c - b; cover inner face inboard of rear edge = c - a'},
    {'id': 'M2', 'cover': 'OFF', 'what': 'Cover thickness direct',
     'how': 'Lay the removed upper cover flat. Measure thickness at the top edge and at one oval slot, covering included.',
     'gives': 'check on M1 (b - a)'},
    {'id': 'M3', 'cover': 'OFF', 'what': 'Depth B on a stated datum, three heights',
     'how': 'Straightedge across the two side-wall rear edges. Ruler from the baffle rear face to the straightedge, '
            'on the cabinet centre line, at 30, 70 and 110 mm below the underside of the top. State whether the '
            'ruler started on the flat board or on a raised frame strip.',
     'gives': 'decides H1 against H2 (160 or about 188), the taper, and the baffle step'},
    {'id': 'M4', 'cover': 'OFF', 'what': 'Rear cleats',
     'how': 'Clear width between the left and right cleats. Cleat depth front-to-back. Distance from the baffle '
            'rear face to the cleat front face at 70 mm below the top. Rear edge to the cleat rear face (the recess).',
     'gives': 'tray width limit for withdrawal (W2, W3) and a second value for the cover seat'},
    {'id': 'M5', 'cover': 'OFF, cover on the bench', 'what': 'Upper cover and slots',
     'how': 'Cover height. For each oval slot: top edge of cover to slot top and slot bottom; nearest cover end to '
            'slot start and slot end.',
     'gives': 'W4, the air outlet and the tube sightline keepout'},
    {'id': 'M6', 'cover': 'either', 'what': 'Outside depth of the cabinet top',
     'how': 'Front edge to rear edge on the top face, covering included. Drawing says 215.',
     'gives': 'tells whether the received cabinet follows the drawing depth'},
]

fails = [c['id'] for c in checks if c['verdict'] == 'FAIL']
result = {
    'task': 'CB-009 independent mechanical check: rear-cover clearance of Fischer SK 81 50 SA',
    'checked_on': '2026-11-28',
    'scope': 'Arithmetic screen from the register, the supplier drawings and photographs. Not CAD, not a measured '
             'fit, not a placement or fabrication release. No register, native or CAD file changed.',
    'coverage_input_sha256': hashlib.sha256(json.dumps({'measurements': {k:reg['cabinet']['user_measurements'][k] for k in ('B_rear_edge_depth_mm','P2_clear_opening_mm','A_rear_clear_width_mm','P3_obstruction_report','upper_cover_installed_AB')}, 'external':reg['cabinet']['published_external'], 'opening':reg['cabinet']['top_opening']},sort_keys=True).encode()).hexdigest(),
    'sources': SOURCES, 'parameters': PARAM,
    'stack_mm': {'sink_max': round(sink_max, 2), 'guard': G, 'need_contact': round(need_contact, 2),
                 'need_with_cover_gap': round(need_service, 2),
                 'guarded_elevation_w_h': [round(guard_w, 2), round(guard_h, 2)]},
    'cover_inner_face': cover, 'longitudinal_datum': datum, 'height_taper': taper,
    'interior_near_fins': near_fins, 'scenarios': scen, 'pocket': pocket,
    'checks': checks, 'failed_checks': fails, 'thermal': thermal, 'alternatives': alternative,
    'missing_measurements': missing,
    'verdict': 'HOLD. Actual clearance is not determined. Under the datum as recorded (H1) the guarded sink on a '
               'flat rear wall of the 130 mm tray overlaps the cover by %.1f mm, or %.1f mm short with the gaps. '
               'Under the drawing-consistent datum (H2) it clears by %.1f mm with the gaps. M1 and M3 decide.'
               % (-scen['H1']['margin_guarded_contact_mm'], -scen['H1']['margin_guarded_service_mm']['central'],
                  scen['H2']['margin_guarded_service_mm']['central']),
    'recommendation': [
        'Do not place the return stage on the +5.12 mm CB-008 margin. It omits the cover.',
        'Take M1 and M3 first. They need a ruler and a straightedge and settle a 28 mm question.',
        'If H1 holds: use a full-height open-ended pocket about %.0f mm deep and %.0f mm wide in the rear wall, '
        'sized on the measured values. Do not shorten the whole tray.' % (p1['depth_mm']['central'] + 0.5, p1['width_mm'] + 0.5),
        'If H2 holds: the flat rear wall works for depth. Cleat width then limits the tray, not the sink.',
        'Either way: fasten sink and guard to the cassette only, keep 5 mm to the cover, and measure the installed '
        'case temperature before release.',
    ],
}
# The subsequent direct reading supersedes both inferred depths at this location.
ab = reg['cabinet']['user_measurements']['upper_cover_installed_AB']['distance_mm']
flat_needed = P['front_gap'] + P['tray_depth'] + need_service
trial_recess = 15.0
result['direct_cover_on_check'] = dict(
    measured_approx_mm=ab, measurement_uncertainty_mm=None, flat_needed_mm=round(flat_needed,2),
    flat_guard_to_wood_mm=round(ab-flat_needed+P['cover_gap_min'],2),
    recess_min_for_5mm_gap_mm=round(flat_needed-ab,2), trial_recess_mm=trial_recess,
    trial_recess_width_mm=p1['width_mm'], clear_internal_depth_mm=P['tray_depth']-trial_recess-2*P['tray_wall'],
    minimum_AB_for_trial_mm=round(flat_needed-trial_recess,2),
    trial_guard_to_wood_mm=round(ab-flat_needed+P['cover_gap_min']+trial_recess,2))
result['historical_datum_verdict'] = result['verdict']
result['verdict'] = 'Hold flat-wall placement. The direct cover-on reading is approximate. A 15 mm open-ended recess passes the local depth screen; verify the full guard and withdrawal path with a template.'
result['recommendation'] = ['Use the direct A–B reading at this location. Trial a 15 mm open-ended recess and retain independent cover removal. Check the full guard footprint, hardware and cover sweep with a template and verify installed cooling.']
result['missing_measurements'] = {'prior_datum_study': missing, 'current': 'Confirm the minimum gap over the full assembly at mock-up. The direct A–B reading is adequate for this trial.'}
OUT_JSON.write_text(json.dumps(result, indent=2) + '\n')

# ------------------------------------------------------------------ drawing
S = 3.0
out = []


def rect(x, y, w, h, style):
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" %s/>' % (x, y, w, h, style))


def text(x, y, s, size=11, anchor='start', extra=''):
    out.append('<text x="%.1f" y="%.1f" font-size="%d" text-anchor="%s" %s>%s</text>' % (x, y, size, anchor, extra, s))


def dim(x1, x2, y, label):
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#444" stroke-width="0.8"/>' % (x1, y, x2, y))
    for x in (x1, x2):
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#444" stroke-width="0.8"/>' % (x, y - 4, x, y + 4))
    text((x1 + x2) / 2, y - 5, label, 10, 'middle')


def section(ox, recess, title):
    def x(mm):
        return ox+mm*S

    wall = P['front_gap']+P['tray_depth']-recess
    guard_end = wall+need_contact
    text(ox-30,85,title,18,'start','font-weight="bold"')
    rect(x(-6),115,6*S,230,'fill="#b48753"')
    rect(x(ab),115,8*S,230,'fill="#d1a66f"')
    rect(x(P['front_gap']),134,(wall-P['front_gap'])*S,180,'fill="#dbe6ed" stroke="#345"')
    text(x(12),162,'Metal cassette',15)
    if recess:
        dim(x(wall),x(wall+recess),193,'15 mm')
    depth = P['wall_bracket']
    rect(x(wall),208,depth*S,66,'fill="#667781"')
    rect(x(wall+depth),208,sink_max*S,66,'fill="#364954"')
    rect(x(wall+depth+sink_max),202,G*S,78,'fill="none" stroke="#ba592e" stroke-width="2"')
    text(x(64),252,'Fischer sink and guard',13)
    dim(x(0),x(ab),372,'A to B about 155 mm')
    text(x(0),335,'A',14,'middle')
    text(x(ab),335,'B',14,'middle')
    gap=ab-guard_end
    label = ('Guard overlaps wood by about %.1f mm' % -gap if gap<0
             else 'About %.1f mm clear from guard to wood' % gap)
    text(ox,423,label,15,'start','fill="%s"' % ('#983816' if gap<0 else '#205f49'))


W,H=1260,535
text(40,42,'Fischer SK 81 50 SA · upper cabinet side section',24,'start','font-weight="bold"')
section(70,0,'Flat 130 mm tray')
section(690,trial_recess,'15 mm local recess')
text(40,476,'Allow 5 mm behind the guard. Trial a 121.4 mm wide recess with open ends. Mount the heatsink and guard on the metal cassette.',15)
text(40,505,'A is the speaker-board rear face. B is the inward surface of the installed rear cover. Verify the full assembly with a template.',14)
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
       'font-family="Helvetica, Arial, sans-serif"><rect width="100%%" height="100%%" fill="#fff"/>%s</svg>\n'
       % (W, H, W, H, ''.join(out)))
OUT_SVG.write_text(svg)

for c in checks:
    print('%-6s %-14s margin=%-8s %s' % (c['id'], c['verdict'], c['margin_mm'], c['title']))
print('cover', cover['inner_face_inboard_of_rear_edge_mm'])
for h in ('H1', 'H2'):
    print(h, json.dumps(scen[h]))
print('pocket H1', json.dumps(pocket['H1']))
