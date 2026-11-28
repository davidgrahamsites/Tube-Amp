"""CB-008 independent check: Boyd 530002B02500G as PA340CC external sink with guard.

Reads ../fit-register.json (read-only). Writes ../review/guard-sink-fit.json and
../review/guard-sink-fit.svg. Arithmetic screen only: no CAD mutation, no fit release.
Manufacturer dimensions were transcribed by eye from the cited drawing pages;
re-read them against the PDFs (hashes below) before relying on a margin under 1 mm.
"""
import hashlib
import json
import math
from plot_guard_sink import draw
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
REGISTER = MODULE / 'fit-register.json'
OUT_JSON = MODULE / 'review' / 'guard-sink-fit.json'
OUT_SVG = MODULE / 'review' / 'guard-sink-fit.svg'

register = json.loads(REGISTER.read_text())
cab = register['cabinet']
meas = cab['user_measurements']
panel = register['control_panel_study']
spk = register['speaker_reference']
tank = register['tank_received']['mechanical_measurements']

# ---------------------------------------------------------------- sources
SOURCES = {
    'boyd_catalog': {
        'url': 'https://info.boydcorp.com/hubfs/Thermal/Air-Cooling/Boyd-Board-Level-Heatsinks-Catalog.pdf',
        'location': 'printed page 56 (PDF page 58), series 5297/5298/5299/5300; '
                    'flat-back YB32-4G on printed page 61 (PDF page 63)',
        'sha256_when_read': '985d70eb8ab6a8c445ce1eccba7cf25be5d1f4699406f002d9650b84cf12e469',
        'read_on': '2026-11-28',
    },
    'apex_pa340': {
        'url': 'https://www.apexanalog.com/resources/products/pa340u.pdf',
        'location': 'PA340U Rev D page 14, PACKAGE STYLE CC; page 12 HEATSINKING; page 3 note 5',
        'sha256_when_read': '6fc55e08d84ba70c449a4b38f2a0e684b1de70b00e18e6b98a90f62dc7593948',
        'read_on': '2026-11-28',
    },
    'cb007': 'engineering/whole-amp/effects-loop/common-buffer/supply-cutoff.html (thermal paragraphs)',
    'packaging_search_case': 'engineering/whole-amp/mechanical/review/electric-packaging-panel-2026-11-21.md',
    'three_board_concept': 'engineering/whole-amp/mechanical/review/three-board-chassis-concept.md',
}

# ------------------------------------------- Boyd 530002B02500G (catalog)
SINK = {
    'height_A': 63.50, 'width': 41.91, 'depth': 25.40,
    'hole_B_from_base': 18.29, 'hole_C_dia': 3.17, 'hole_x_from_edge': 20.96,
    'channel_width': 17.02, 'web_thickness': 1.57,
    'base_notch_width': 13.72, 'base_notch_height': 3.18,
    'pin_dia': 2.36, 'pin_pitch': 25.40, 'pin_length': 3.96, 'pcb_hole_for_pin': 2.67,
    'listed_device': 'TO-220', 'material': 'aluminium, black anodize',
    'catalog_Rth_K_per_W_at_75C_rise': 2.6,
}
# The series page prints no tolerance. Catalog PDF page 99 prints +/-0.38 mm
# (holes +/-0.25) "unless otherwise specified" for a different product section.
# Used here as an ASSUMED bound, not a manufacturer tolerance for this extrusion.
TOL = 0.38

# ---------------------------------------------- Apex PA340CC 7-pin DDPAK
PKG = {
    'body_width_max': 10.31, 'body_width_min': 10.06,
    'overall_length_max': 15.75, 'overall_length_min': 14.74,
    'thickness_max': 4.57, 'thickness_min': 4.32,
    'lead_pitch': 1.27, 'lead_width_max': 0.91, 'leads': 7,
    'land_tab_w': 13.0, 'land_tab_l': 11.4, 'land_gap': 2.16, 'land_lead_l': 5.08,
    'mounting_hole': None, 'tab_net': '-Vs (ground in the CB-006/007 candidate)',
    'case_limit_C': 85,
}

# ------------------------------ explicit ASSUMPTIONS (not source geometry)
ASSUME = {
    'guard_air_gap_mm': 6.0,        # free air between fin tips and guard
    'guard_material_mm': 1.5,       # perforated guard thickness
    'wall_bracket_mm': 2.0,         # any bracket between sink and wall
    'carrier_pcb_mm': 1.6,          # removable carrier / spreader stack
    'interface_mm': 0.25,           # thermal interface pad
    'm3_washer_dia_mm': 7.0,        # clamp hardware under screw head
    'carrier_placement_tol_mm': 0.5,
    'controls_centred_in_opening': True,
}
G = ASSUME['guard_air_gap_mm'] + ASSUME['guard_material_mm']

checks = []


def add(cid, title, verdict, value=None, limit=None, margin=None, note=''):
    checks.append({'id': cid, 'title': title, 'verdict': verdict,
                   'value_mm': None if value is None else round(value, 3),
                   'limit_mm': None if limit is None else round(limit, 3),
                   'margin_mm': None if margin is None else round(margin, 3),
                   'note': note})


def fit(cid, title, need, avail, note='', conditional=False):
    m = avail - need
    v = 'FAIL' if m < 0 else ('CONDITIONAL' if conditional else 'PASS')
    add(cid, title, v, need, avail, m, note)
    return m


# envelopes at maximum material
w_max, d_max, h_max = SINK['width'] + TOL, SINK['depth'] + TOL, SINK['height_A'] + TOL
env_bare = [w_max, d_max, h_max]
env_guard = [w_max + 2 * G, d_max + 2 * G, h_max + G]          # free-standing, base on a surface
flat_bare = ASSUME['wall_bracket_mm'] + d_max                   # protrusion, lying against a wall
flat_guard = flat_bare + G

# ------------------------------------------------ A. device to sink
add('A1', 'PA340CC fastens directly to the sink', 'FAIL',
    note='Sink is drilled for one TO-220 screw. The DDPAK is surface-mount with no hole '
         '(Apex p.14) and Apex requires solder attachment of the heat slug (p.12). '
         'A soldered carrier/spreader is mandatory; the sink alone is not a PA340 mount.')

chan_min = SINK['channel_width'] - TOL
fit('A2', 'Apex tab land width inside sink channel', PKG['land_tab_w'] + 2 * ASSUME['carrier_placement_tol_mm'],
    chan_min, 'Carrier strip must be narrower than %.2f mm. Compensation parts cannot sit beside the '
              'package inside the channel; the carrier must extend along the extrusion.' % chan_min,
    conditional=True)

chan_depth = (SINK['depth'] - TOL - SINK['web_thickness']) / 2
stack = ASSUME['interface_mm'] + ASSUME['carrier_pcb_mm'] + PKG['thickness_max']
fit('A3', 'Carrier + package stack inside channel depth', stack, chan_depth,
    'Package top stays inside the fin envelope; a top-of-package sensor (TMP235) and a spring '
    'clip must also fit in the remaining depth.', conditional=True)

r_w = ASSUME['m3_washer_dia_mm'] / 2
pkg_len = PKG['land_tab_l'] + PKG['land_gap'] + PKG['land_lead_l']
below = SINK['hole_B_from_base'] - r_w - SINK['base_notch_height']
above = SINK['height_A'] - TOL - SINK['hole_B_from_base'] - r_w
fit('A4a', 'Package footprint fits between base notch and the screw', pkg_len, below,
    'Package cannot sit below the only screw hole.')
fit('A4b', 'Package footprint fits above the screw', pkg_len, above,
    'Fits above the hole, but then one screw clamps one END of the spreader.', conditional=True)
lever = r_w + PKG['land_tab_l'] / 2
add('A5', 'Clamp force over the heat slug', 'FAIL', value=lever,
    note='Heat-slug centre is at least %.2f mm from the single screw axis (cantilever clamp). '
         'Contact pressure under the slug is uncontrolled, so the 1 K/W case-to-sink allocation '
         'in CB-007 is unsupported. Needs a second fastener (drilling the 1.57 mm web = modified part) '
         'or a qualified spring clip over the body.' % lever)
add('A6', 'Thread in the web', 'CONDITIONAL', value=SINK['web_thickness'],
    note='1.57 mm web gives about 3 threads of M3x0.5; use a through screw with nut and washer '
         'in the opposite channel, not a tapped hole.')
lead_span = (PKG['leads'] - 1) * PKG['lead_pitch'] + PKG['lead_width_max']
lat = (chan_min - lead_span) / 2 - ASSUME['carrier_placement_tol_mm']
add('A7', 'Lateral gap, outer leads to grounded fin wall', 'CONDITIONAL', value=lat,
    note='Leads carry up to the 310-350 V rail; tab, web and fins are -Vs/ground. Gap is through '
         'air inside the channel with the carrier edge only %.2f mm from the wall if the carrier '
         'fills the channel. Required creepage/clearance for this rail is not established by this '
         'check; Apex states pin pitch alone is not sufficient above its noted supply voltage.'
         % ((chan_min - (PKG['land_tab_w'] + 2.0)) / 2))

# ------------------------------------------------ B. sink to wall
add('B1', 'Sink has a wall-mounting provision', 'FAIL',
    note='Only two solder pins (dia 2.36, 25.40 pitch, 3.96 long) for a 2.67 mm plated PCB hole. '
         'No flange, no threaded hole, no flat back: both faces are radial fins. It cannot be bolted '
         'to a chassis or cabinet wall, and aluminium wall metal cannot take the solder pins.')
add('B2', 'Heat can cross a wall into this sink', 'FAIL',
    note='Device mounts on the centre web between the fins, on the same side of any wall as the '
         'sink. "Device inside, sink outside" is impossible with this profile: either the PA340 and '
         'its high-voltage carrier leave the enclosure, or the sink stays inside. This contradicts '
         'the CB-007 allocation that keeps the PA carrier at the internal return.')
pin_through = SINK['pin_length'] - ASSUME['carrier_pcb_mm']
add('B3', 'Solder pin projection through a 1.6 mm carrier PCB', 'PASS', value=pin_through,
    note='Manufacturer-intended mount: vertical on a PCB. Pins are electrically the sink (ground).')

# ------------------------------------------------ C. envelope vs proposals
chassis = register['chassis_service_study']
assert all(chassis[k] is None for k in ('candidate_cassette_envelope_mm','rail_section_mm','fastener_positions_mm')), 'Re-evaluate dimensioned chassis'
add('C0', 'Three-board concept supplies a dimensioned wall', 'NOT_EVALUABLE',
    note='The three-board illustration is a workspace visual reference. Heights and rail positions are unscaled '
         'in that concept. The chassis_service_study envelope, '
         'rail section and fastener positions are null in the register. No interference with a '
         'three-board chassis can be computed. Checks C1-C4 use received cabinet measurements and the '
         '21 November search envelopes (four-board study, proposal only).')

# C1 top control opening
frame_w, frame_d = panel['screen_frame_mm']
controls_w, controls_d = 215.0, 48.0   # chassis-service-layout-2026-11-21.md staggered study
end_w = (frame_w - controls_w) / 2
fit('C1a', 'Top panel end zone: guarded sink, long side across', env_guard[0], end_w,
    'End zone = (%g - %g)/2 beside the ten-control study, controls assumed centred.' % (frame_w, controls_w))
fit('C1b', 'Top panel end zone: guarded sink turned 90 deg, depth', env_guard[0], frame_d,
    'Opening clear depth about %g mm with rear cover on.' % frame_d)
m = fit('C1c', 'Top panel end zone: bare sink, rectangular screen', env_bare[0], end_w,
        'Bare fins on the top face: no guard, input/power/indicator area consumed.', conditional=True)
R = cab['top_opening']['corner_radius_mm']
x0, y0 = end_w - env_bare[0], (frame_d - env_bare[1]) / 2   # sink pushed toward the controls
corner = math.hypot(R - x0, R - y0) - R
add('C1d', 'Bare sink corner vs published R%g opening corner' % R,
    'FAIL' if corner > 0 else 'CONDITIONAL', value=corner,
    note='Positive = sink corner lies outside the rounded opening by this amount. Published radius '
         'applied to the received 307 x 53 frame; actual corner shape is unmeasured.')
add('C1e', 'Top-panel protrusion', 'FAIL', value=env_guard[2],
    note='Vertical extrusion stands this high above the control face, beside the knobs '
         '(16.5 mm) and the handle. Handle/bolt keepouts are unknown in the register.')

# C2/C3 rear and side walls of the search cages
depth_avail = meas['B_rear_edge_depth_mm']
width_avail = meas['A_rear_clear_width_mm']
for name, cw, cd in (('440x130 tray', 440.0, 130.0), ('440x145x85 cage', 440.0, 145.0)):
    spare_d = depth_avail - cd
    fit('C2 ' + name + ' bare', 'Rear wall, sink flat on wall, no guard', flat_bare, spare_d,
        'Spare is TOTAL front+rear depth with zero rear-cover thickness: an upper bound.',
        conditional=True)
    fit('C2 ' + name + ' guard', 'Rear wall, sink flat on wall, with guard', flat_guard, spare_d,
        'Also sits behind the wooden rear cover, not in outside air.')
    spare_w = width_avail - cw
    fit('C3 ' + name + ' bare', 'Side wall, sink flat on wall, no guard', flat_bare, spare_w,
        'Spare is TOTAL of both sides; register budgets 15 mm side flange per side for the rails.')

# C4 hanging below the chassis floor on its own carrier PCB (vertical extrusion)
cage_h = 85.0
drop = ASSUME['carrier_pcb_mm'] + h_max + G
height_avail = meas['P3_obstruction_report']['P3_inside_height_mm'] - tank['T3_max_height_mm']
fit('C4a', 'Below chassis floor: height (cage 85 + carrier + sink + guard)', cage_h + drop, height_avail,
    'Chassis elevation in the cabinet is unassigned; tank height subtracted.', conditional=True)
behind_magnet = depth_avail - spk['depth_mm']
fit('C4b', 'Below chassis floor: guard depth vs space behind reference speaker', env_guard[1], behind_magnet,
    'Reference Celestion depth %g mm (not selected). Margin is effectively zero directly behind the '
    'magnet: place it laterally clear of the %g mm magnet or above it.' % (spk['depth_mm'], spk['magnet_diameter_mm']),
    conditional=True)
add('C4c', 'Below chassis floor is an "external wall"', 'FAIL',
    note='This is cabinet-interior air below a tube chassis and behind the speaker. The CB-007 '
         'target of <=60 C effective air is unproven there. Rear withdrawal must also clear a '
         '%.1f mm drop below the chassis floor; fixed-support and lower-panel positions are null.' % drop)

# C5 through the wooden cabinet
wall = (cab['published_external']['width'] - meas['A_rear_clear_width_mm']) / 2
add('C5', 'Sink through the wooden cabinet side', 'FAIL', value=wall,
    note='Derived side thickness (published 508 - measured 467)/2, unverified. A sink on the wood '
         'either ties the removable chassis to the fixed cabinet or needs a separable thermal joint '
         'across about this thickness; cabinet alteration is outside the fixed-cabinet rule.')

# ------------------------------------------------ D. thermal sanity (not a fit check)
P = 2.844
graph = {'reading_rise_C_at_P': [10.0, 15.5], 'central_rise_C': 12.5}
r_lo, r_hi = (x / P for x in graph['reading_rise_C_at_P'])
thermal = {
    'power_W': P,
    'cb007_installed_sink_allocation_K_per_W': 4.0,
    'catalog_headline_K_per_W': SINK['catalog_Rth_K_per_W_at_75C_rise'],
    'catalog_headline_condition': '75 C mounting-surface rise, free air, vertical',
    'graph_53000X_reading_K_per_W_at_power': [round(r_lo, 2), round(r_hi, 2)],
    'graph_central_K_per_W': round(graph['central_rise_C'] / P, 2),
    'graph_reading_confidence': 'LOW: read by eye from the printed natural-convection curve '
                                '(dashed 53000X, lower graph). Re-read or measure.',
    'verdict': 'HOLD',
    'note': 'The 2.6 K/W figure applies only at a 75 C rise. Near 2.8 W the free-air curve reads '
            'about 3.5-5.5 K/W before any guard, wall proximity, non-vertical mounting or '
            'tolerance. The 4 K/W installed allocation therefore has no demonstrated margin.',
    'sink_surface_estimate_C_at_60C_air': round(60 + P * 4.0, 1),
    'touch_note': 'Estimated fin temperature exceeds common accessible-metal touch limits; a guard '
                  'is justified. Limit values must be taken from the applicable safety standard; '
                  'not verified in this check.',
}

# ------------------------------------------------ verdict and alternative
# The Fischer drawing gives a 100 x 50 mm footprint and a 15 mm profile.
# Allow the same guard and dimensional budget as the rejected Boyd case.
fischer_depth = 15 + TOL + G + ASSUME['wall_bracket_mm']
fischer = dict(mpn='SK 81 50 SA', source='https://www.farnell.com/datasheets/3171141.pdf',
               guarded_width_height_depth_mm=[100+TOL+2*G,50+TOL+2*G,fischer_depth],
               base_mm=4, margin_130_tray_mm=depth_avail-130-fischer_depth,
               margin_145_cage_mm=depth_avail-145-fischer_depth,
               family_catalog_K_per_W=[1.9,3.4], guaranteed_installed_K_per_W=None)
fails = [c['id'] for c in checks if c['verdict'] == 'FAIL']
result = {
    'task': 'CB-008 independent mechanical check: PA340CC external sink Boyd 530002B02500G with guard',
    'checked_on': '2026-11-28',
    'scope': 'Arithmetic envelope and interface screen from manufacturer drawings and register '
             'measurements. Not CAD, not a measured fit, not a fabrication or placement release.',
    'register_input_sha256': hashlib.sha256(json.dumps([meas, cab['top_opening'], cab['published_external'],
        panel['screen_frame_mm'], spk, tank, chassis], sort_keys=True).encode()).hexdigest(),
    'sources': SOURCES,
    'sink_mm': SINK, 'assumed_tolerance_mm': TOL, 'package_mm': PKG, 'assumptions': ASSUME,
    'envelopes_mm': {
        'bare_max_w_d_h': [round(x, 2) for x in env_bare],
        'guarded_free_standing_w_d_h': [round(x, 2) for x in env_guard],
        'flat_on_wall_protrusion_bare': round(flat_bare, 2),
        'flat_on_wall_protrusion_guarded': round(flat_guard, 2),
    },
    'flat_base_candidate': fischer,
    'checks': checks,
    'thermal_sanity': thermal,
    'failed_checks': fails,
    'verdict': 'FAIL as an external-wall sink. Keep return-stage placement on hold.',
    'verdict_reasons': [
        'B1/B2: board-level radial-fin part with solder pins only; no flat face or fastener to put '
        'it outside a wall while the PA340 stays inside.',
        'A1/A5: DDPAK needs a soldered carrier, and the single TO-220 screw cannot clamp it properly.',
        'C1-C3: with a guard it does not fit the top opening end zones or the rear/side spare of '
        'either 21 November search envelope.',
        'C0: the three-board concept has no dimensions, so no interference result exists for it.',
        'Thermal: no demonstrated margin against the 4 K/W allocation.',
    ],
    'alternatives': [
        {
            'name': 'ALT-1 same part, used as the manufacturer intends (conditional fit)',
            'description': '530002B02500G soldered by its two pins to the removable PA carrier PCB, '
                           'extrusion vertical, hung below the chassis floor in the open-back air '
                           'stream with a perforated guard. Package above the screw hole, held by a '
                           'qualified spring clip plus the screw-clamped spreader.',
            'fits': 'C4a and C4b pass conditionally; B3 passes.',
            'conditions': ['Not an external wall: measure local air (target <=60 C) and case '
                           'temperature in the closed cabinet.',
                           'Keep laterally clear of the speaker magnet.',
                           'Prove rear withdrawal with the %.1f mm drop.' % drop,
                           'Resolve A5 clamp, A7 high-voltage spacing and guard earthing.'],
        },
        {
            'name': 'ALT-2 Fischer SK 81 50 SA flat-base wall sink',
            'description': 'PA340 soldered to a copper or insulated-metal carrier bolted to the '
                           'INSIDE of an aluminium chassis wall; a flat-base extrusion bolted to the '
                           'OUTSIDE of the same wall with the same two or more screws. Target '
                           '<=3 K/W free-air at about 3 W so that wall joints and guard leave margin '
                           'inside 5 K/W. Protrusion including guard must suit the chosen wall: '
                           '<=%.0f mm on a rear wall of a 130 mm-deep tray only if the rear cover '
                           'position allows; otherwise use the chassis underside.' % (depth_avail - 130.0),
            'fits': 'Depth screen only. See flat_base_candidate. The actual wall face, cover and exposed air are unqualified.',
            'conditions': ['Reserve the stated clear wall face and demonstrate clamping and rear withdrawal on the proposed cassette.',
                           'Boyd YB32-4G (flat back, 60 x 32 x 16 mm, printed page 61) was read and '
                           'rejected: its curve is roughly 10 K/W near 3-4 W.'],
        },
    ],
    'human_check': 'Before any placement: fix the chassis wall and elevation in the register, hold '
                   'the real sink, carrier and guard against the empty cabinet, and measure case '
                   'temperature at full output and in the port-short case.',
}
OUT_JSON.write_text(json.dumps(result, indent=2) + '\n')

section = dict(channel_depth=chan_depth, stack=stack, washer_radius=r_w, land_length=pkg_len,
               lead_span=lead_span, guard_gap=G)
cabinet_view = dict(frame=(frame_w, frame_d), controls=(controls_w, controls_d),
                    end_width=end_w, corner_radius=R, corner_error=corner, origin=(x0,y0),
                    depth=depth_avail, width=width_avail)
draw(OUT_SVG, result, section, cabinet_view)

for c in checks:
    print('%-22s %-13s margin=%s' % (c['id'], c['verdict'], c['margin_mm']))
print('thermal', thermal['graph_53000X_reading_K_per_W_at_power'], thermal['verdict'])
print('failed', len(fails), 'of', len(checks))
