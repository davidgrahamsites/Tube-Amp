"""CB-009 cabinet datums, source observations and guard dimensions."""
import json
from pathlib import Path
MODULE = Path(__file__).resolve().parents[1]
REGISTER = MODULE / 'fit-register.json'
OUT_JSON = MODULE / 'review' / 'rear-cover-sink.json'
OUT_SVG = MODULE / 'review' / 'rear-cover-sink.svg'

reg = json.loads(REGISTER.read_text())
cab = reg['cabinet']
meas = cab['user_measurements']
pub = cab['published_external']

SOURCES = {
    'register': 'engineering/whole-amp/mechanical/fit-register.json (cabinet.user_measurements: B, P1, P2-clear, P3, A)',
    'cb008': 'engineering/whole-amp/mechanical/review/guard-sink-fit.json (flat_base_candidate, assumptions)',
    'feedback': 'brain/feedback/events.json FB-068 (cover top level with top underside), FB-070 (no mount to '
                'removable cover), FB-071/072 (rear withdrawal, drill access), FB-073 (P1, P2-clear, cover ON), '
                'FB-074 (P3, cover OFF), FB-069 (tube glow through oval slots), FB-190 (this task)',
    'measurement_guide': 'engineering/whole-amp/mechanical/review/measurement-guide-2026-11-21.md '
                         '(P2-clear replaces the earlier P2-to-outside-edge instruction)',
    'supplier_side_view': {
        'file': 'engineering/solid-state-reverb/evidence/cabinet-size-02.jpg',
        'sha256': 'be6d0342f1f22dff1ae578409b2ff1df406cb0d7a613b9b3f21a589770df33f8',
        'read': 'top depth 215, bottom depth 242, height 420; dashed rear strip 18 deep, set 11 in from the '
                'rear edge, starting 25 below the top and ending 25 above the bottom; front strips 9 x 48',
    },
    'supplier_top_view': {
        'file': 'engineering/solid-state-reverb/evidence/cabinet-size-01.jpg',
        'sha256': '8bc19e61f3903e7223f5790ebd92e51833ab6e8fa6d01a3118d72a47732fb08b',
        'read': 'top notch 67 deep from the cabinet rear edge, 2-R31, 156+156 straight, 172+172 stepped',
    },
    'supplier_front_view': {
        'file': 'engineering/solid-state-reverb/evidence/cabinet-size-03.jpg',
        'sha256': 'e2c7cbc3f1398c7a5e9699a0c2018d4f3e085c76ca8df07a8e4fa339462f6ca4',
        'read': 'baffle 468 x 380; section shows two 9 mm layers (18 total at the 30 mm frame strips)',
    },
    'photos': 'engineering/whole-amp/mechanical/evidence/received-cabinet-2026-11-21/ '
              '(cabinet-04.jpg rear/top with upper cover ON; speaker-offset-rear.jpg upper cover OFF, '
              'side cleats visible). Qualitative only per the evidence CONTEXT.md.',
    'fischer': {
        'url': 'https://www.fischerelektronik.de/web_fischer/en_GB/heatsinks/A01/Standard%20extruded%20heatsinks/PR/SK81_/index.xhtml',
        'read_on': '2026-11-28',
        'read': 'width 100, height 15, plate thickness 4, lengths 37.5/50/75/100/1000, thermal resistance '
                '3.4 - 1.9 K/W (no length mapping, no conditions printed), black anodised',
        'not_read': 'https://www.farnell.com/datasheets/3171141.pdf timed out twice on 2026-11-28. Fin count, fin '
                    'pitch, tolerances, drilling and the K/W value at 50 mm were NOT read in this check.',
    },
}

# ------------------------------------------------------------------ parameters
PARAM = {
    # Fischer SK 81 50 SA (product page)
    'sink_width': 100.0, 'sink_profile_height': 15.0, 'sink_base': 4.0, 'sink_length': 50.0,
    'sink_tol': 0.38,              # ASSUMED, carried from CB-008; Fischer tolerance not read
    # stack assumptions carried from CB-008
    'guard_air_gap': 6.0, 'guard_material': 1.5, 'wall_bracket': 2.0,
    # new assumptions in this check
    'cover_gap_min': 5.0,          # guard to cover inner face: air, cover bow, speaker-vibration rattle, removal tilt
    'front_gap': 3.0,              # tray front to baffle rear face: insertion clearance
    'side_clear': 3.0,             # pocket side clearance to the guard
    'tray_wall': 2.0,
    'tray_depth': 130.0, 'tray_width': 440.0, 'tray_height': 85.0,   # 21 November search envelope, proposal only
    'z_sink': 45.0,                # ASSUMED sink centre below the top underside; chassis elevation is unassigned
    # measurement uncertainty: the user gave none; these are ASSUMED tape-reading bounds
    'u_B': 2.0, 'u_P2': 2.0,
    'tweed_wrap': 1.5,             # ASSUMED covering thickness on a cut wooden edge
}
P = PARAM
G = P['guard_air_gap'] + P['guard_material']
sink_max = P['sink_profile_height'] + P['sink_tol']
need_contact = P['wall_bracket'] + sink_max + G            # CB-008 figure, 24.88
need_service = need_contact + P['cover_gap_min']
guard_w = P['sink_width'] + P['sink_tol'] + 2 * G          # fins vertical: 100 across, 50 up
guard_h = P['sink_length'] + P['sink_tol'] + 2 * G

B = meas['B_rear_edge_depth_mm']
P2 = meas['P2_clear_opening_mm']
A = meas['A_rear_clear_width_mm']
P3 = meas['P3_obstruction_report']['P3_inside_height_mm']
NOTCH = cab['top_opening']['depth_mm']                     # 67, supplier drawing
DRAW = {'top_depth': pub['depth_top'], 'bottom_depth': pub['depth_bottom'], 'height': pub['height'],
        'rear_recess': 11.0, 'cleat_depth': 18.0, 'cleat_top_offset': 25.0,
        'front_strip': 9.0, 'baffle_stack': 18.0}
slope = (DRAW['bottom_depth'] - DRAW['top_depth']) / DRAW['height']   # depth gained per mm of descent

# ------------------------------------------------------- 1. cover inner face
# Same-datum pair requested by the task: P2 to the OUTER edge and P2-clear, one ruler setup.
# The register holds only P2-clear. The outer reading was never recorded (the instruction was
# replaced before the user answered; see measurement guide and FB-073).
cover = {
    'same_datum_P2_outer_recorded': False,
    'same_datum_estimate_supported': False,
    'reason': 'Register and feedback ledger hold P2-clear = %g mm (cover ON) only. No P2-to-outside-edge value '
              'exists. A subtraction of two measured values on one datum cannot be made.' % P2,
    'mixed_datum_estimates_mm': {
        'E1_drawing_notch_minus_P2_clear': NOTCH - P2,
        'E1_note': 'Supplier notch %g (cabinet rear edge to handle-side cut edge, bare-wood drawing) minus measured '
                   'P2-clear %g. Mixed drawing/measured datum. The same drawing overstates the received straight '
                   'width by 4-5 mm (312 vs 307-308), so the notch may also be short by the covering.' % (NOTCH, P2),
        'E2_notch_less_tweed_minus_P2_clear': NOTCH - P['tweed_wrap'] - P2,
        'E3_drawing_rear_recess': DRAW['rear_recess'],
        'E3_note': 'Supplier side view sets the dashed rear strip 11 in from the rear edge. Read as the seat for '
                   'the rear covers. This reading of the drawing is an interpretation.',
    },
}
c_lo = min(DRAW['rear_recess'], NOTCH - P['tweed_wrap'] - P2 - P['u_P2'])
c_hi = NOTCH - P2 + P['u_P2']
c_mid = NOTCH - P2
cover['inner_face_inboard_of_rear_edge_mm'] = {'low': c_lo, 'central': c_mid, 'high': c_hi}
cover['status'] = 'ESTIMATE ONLY. Bounded %.1f to %.1f mm, central %.1f. Not a measurement.' % (c_lo, c_hi, c_mid)

# ------------------------------------------------ 2. longitudinal datum of B
# H1: register reading. B runs baffle rear face -> cabinet rear edge.
# H2: supplier drawing. Baffle rear face -> rear edge at the top = 215 - 9 - 18 = 188; then
#     188 - 11 - 18 = 159 to the FRONT face of the rear cleat, within 1 mm of the reported 160.
draw_baffle_to_edge_top = DRAW['top_depth'] - DRAW['front_strip'] - DRAW['baffle_stack']
draw_baffle_to_cleat_top = draw_baffle_to_edge_top - DRAW['rear_recess'] - DRAW['cleat_depth']
datum = {
    'B_reported': B,
    'B_register_interpretation': meas['B_interpretation'],
    'B_measurement_height': meas['measurement_height_mm'],
    'drawing_baffle_rear_to_rear_edge_at_top': draw_baffle_to_edge_top,
    'drawing_baffle_rear_to_cleat_front_at_top': draw_baffle_to_cleat_top,
    'conflict_mm': draw_baffle_to_edge_top - B,
    'finding': 'The drawing puts the cabinet rear edge %.0f mm behind the baffle at the top, %.0f mm more than '
               'B. The drawing distance to the front of the rear cleat is %.0f mm, 1 mm from B. Either the '
               'received cabinet is %.0f mm shallower inside than drawn, or B ended on the cleat and not on the '
               'rear edge. The register cannot tell which.'
               % (draw_baffle_to_edge_top, draw_baffle_to_edge_top - B, draw_baffle_to_cleat_top,
                  draw_baffle_to_edge_top - B),
    'H1': 'B = baffle rear face to cabinet rear edge (as recorded).',
    'H2': 'B = baffle rear face to rear-cleat front face (drawing-consistent). Rear edge = B + cleat 18 + recess 11.',
}

# ------------------------------------------------------ 3. height taper/offset
# The front slopes: 215 at the top, 242 at the bottom. If the baffle follows the front, depth
# grows by `slope` per mm of descent. B has no recorded height.
taper_cases = {
    'B_taken_at_sink_height': 0.0,
    'B_taken_at_top_z0': slope * (P['z_sink'] - 0.0),
    'B_taken_at_mid_height': slope * (P['z_sink'] - P3 / 2),
    'B_taken_at_floor': slope * (P['z_sink'] - P3),
}
taper = {
    'slope_mm_per_mm': round(slope, 5),
    'basis': '(242 - 215) / 420 from the supplier side view; assumes the baffle is parallel to the sloped front',
    'z_sink_assumed': P['z_sink'],
    'depth_correction_at_sink_mm': {k: round(v, 2) for k, v in taper_cases.items()},
    'baffle_step': 'Supplier front view shows 9 + 9 mm layers at the 30 mm frame strips. If the frame strip is on '
                   'the rear face, depth is 9 mm less within 30 mm of the baffle edges than at the board. Which '
                   'face carries the strip is not established.',
    'offset_range_mm': [round(min(taper_cases.values()), 2), round(max(taper_cases.values()), 2)],
}

# ----------------------------------------- 4. interior on and near the fins
# Cleats seen in speaker-offset-rear.jpg: one strip inside each side wall, cover screws into them.
PHOTO = {'cabinet_outer_px': [478, 1478], 'side_inner_px': [515, 1440], 'cleat_inner_px': [560, 1395]}
px_per_mm = (PHOTO['cabinet_outer_px'][1] - PHOTO['cabinet_outer_px'][0]) / pub['width']
between_sides_photo = (PHOTO['side_inner_px'][1] - PHOTO['side_inner_px'][0]) / px_per_mm
between_cleats_photo = (PHOTO['cleat_inner_px'][1] - PHOTO['cleat_inner_px'][0]) / px_per_mm
near_fins = {
    'cleats': 'Side cleats only are visible. Drawing: 18 deep, from 25 below the top. Width not drawn.',
    'photo_scale_px_per_mm': round(px_per_mm, 3),
    'photo_between_sides_mm': round(between_sides_photo, 0),
    'photo_between_cleats_mm': round(between_cleats_photo, 0),
    'photo_check': 'Photo scale returns %.0f mm between the side walls against measured A = %g. Same method gives '
                   '%.0f mm between the cleats. LOW confidence: pixel pick from a displayed 2000 px frame, '
                   'perspective uncorrected. Assume +/-8 mm.' % (between_sides_photo, A, between_cleats_photo),
    'sink_zone': 'A guarded sink %.1f wide on the centre of the rear wall is %.0f mm from either cleat. The cleats '
                 'do not touch the sink. They limit the tray, not the fins.'
                 % (guard_w, (between_cleats_photo - guard_w) / 2),
    'oval_slots': 'Two oval slots in the upper cover (FB-069). Position and size are not in the register. A sink '
                  'behind a slot blocks that tube sightline; a sink between or below the slots has no outlet '
                  'above it except the gap to the cover.',
}
