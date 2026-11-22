"""Generate 1:1 paper control study from fit-register; never a drill release."""
from pathlib import Path
import hashlib
import json
from html import escape
import math
import csv

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'fit-register.json'
d=json.loads(path.read_text())['control_panel_study']
controls=d['controls']; W,H=d['screen_frame_mm']; radius=d['knob_swept_diameter_mm']/2
body=d['pot_body_diameter_mm']/2; reach=d['pot_lug_reach_from_shaft_mm']+d['wire_extension_study_mm']
pairs=[]
for i,a in enumerate(controls):
 for b in controls[i+1:]:
  distance=math.dist(a['xy_mm'],b['xy_mm'])
  pairs.append({'a':a['reference'],'b':b['reference'],'knob_edge_gap_mm':distance-2*radius})
margins=[min(x-radius,W-x-radius,y-radius,H-y-radius) for c in controls for x,y in [c['xy_mm']]]
lug_body_gaps=[]
for a in controls:
 ax,ay=a['xy_mm']
 for b in controls:
  if a is b:continue
  bx,by=b['xy_mm']
  # Distance of other circular pot body from this lug/wire bounding rectangle.
  dx=max(ax+body-bx,0,bx-(ax+reach));dy=max(abs(by-ay)-5,0)
  lug_body_gaps.append(math.hypot(dx,dy)-body)
assert min(margins)>=0 and min(p['knob_edge_gap_mm'] for p in pairs)>0
assert min(lug_body_gaps)>0
report={'fit_register_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
 'scope':'Rectangular opening screen and nominal component envelopes only',
 'controls':len(controls),'minimum_knob_pair_gap_mm':min(p['knob_edge_gap_mm'] for p in pairs),
 'minimum_knob_to_rectangular_frame_gap_mm':min(margins),
 'control_sweep_envelope_mm':[max(c['xy_mm'][0] for c in controls)-min(c['xy_mm'][0] for c in controls)+2*radius,max(c['xy_mm'][1] for c in controls)-min(c['xy_mm'][1] for c in controls)+2*radius],
 'shaft_top_above_study_metal_mm_before_washers':15-d['metal_thickness_study_mm'],
 'smooth_shaft_length_mm':15-6.5,
 'exposed_bushing_before_washers_mm':6.5-d['metal_thickness_study_mm'],
 'minimum_lug_wire_box_to_other_body_gap_mm':min(lug_body_gaps),
 'opening_basis':d['opening_basis'],
 'knob_seating_verified':False,'assembled_fit_verified':False,'drill_release':False,
 'unmodeled':'Actual curved opening/supports, panel mounts, antirotation tabs, nut/washer/knob recess, installed jack/switch/indicator, finger access and full cable harness'}
OUT=ROOT/'review'
(OUT/'panel-study-checks.json').write_text(json.dumps(report,indent=2)+'\n')
for underside in [False,True]:
 name='underside' if underside else 'face'
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="332mm" height="111mm" viewBox="0 0 332 111">',
 '<rect width="332" height="111" fill="white"/>',
 f'<text x="10" y="8" font-family="sans-serif" font-size="4">RENEGADE ELECTRIC — {name.upper()} ENVELOPE STUDY / DO NOT DRILL</text>',
 '<text x="10" y="14" font-family="sans-serif" font-size="2.8">Print at 100%. Check 100 mm scale. Rectangular frame is NOT the actual cabinet cut profile.</text>',
 '<g transform="translate(10 20)">',
 f'<rect width="{W}" height="{H}" fill="none" stroke="#444" stroke-width=".4"/>']
 for x in [0,W-31]:svg.append(f'<rect x="{x}" y="0" width="31" height="{H}" fill="#ddd"/><text transform="translate({x+15} {H-3}) rotate(-90)" font-size="3" font-family="sans-serif">RESERVE / UNPLACED</text>')
 for c in controls:
  x,y=c['xy_mm']; label=escape(c['label'])
  svg.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="none" stroke="#296890" stroke-dasharray="1 1" stroke-width=".35"/>')
  if underside:
   svg += [f'<circle cx="{x}" cy="{y}" r="{body}" fill="#e1e7ed" stroke="#333" stroke-width=".25"/>',
           f'<rect x="{x+body}" y="{y-5}" width="{reach-body}" height="10" fill="#f7dba8" stroke="#a66b00" stroke-width=".25"/>']
  else:svg.append(f'<circle cx="{x}" cy="{y}" r="{d["pot_hole_study_mm"]/2}" fill="none" stroke="#b34d33" stroke-dasharray=".7 .7" stroke-width=".3"/>')
  svg += [f'<path d="M{x-2},{y}h4 M{x},{y-2}v4" stroke="#111" stroke-width=".2"/>',
          f'<text x="{x}" y="{y-3}" text-anchor="middle" font-family="sans-serif" font-size="2.4">{c["reference"]}</text>',
          f'<text x="{x}" y="{y+8}" text-anchor="middle" font-family="sans-serif" font-size="2.35">{label}</text>']
 svg += ['</g>',
 '<path d="M10,96h100 M10,93v6 M110,93v6" fill="none" stroke="black" stroke-width=".3"/>',
 '<text x="45" y="103" font-family="sans-serif" font-size="3">100 mm</text>',
 '<text x="125" y="96" font-family="sans-serif" font-size="2.6">26 mm knob sweeps / 24 mm pot bodies. Labels show assignment only.</text>',
 '<text x="125" y="102" font-family="sans-serif" font-size="2.6">Underside shown in shared top-view coordinates, NOT a mirrored drilling view.</text>',
 '</svg>']
 (OUT/f'panel-study-{name}.svg').write_text('\n'.join(svg)+'\n')
print(json.dumps(report,indent=2))

# Electrical interface only: wire lengths, loom placement and pin viewing side remain open.
contract=ROOT.parent/'reverb-600/circuit.json'
parts={c['reference']:c for c in json.loads(contract.read_text())['components'] if c['reference'].startswith('RV')}
with (OUT/'panel-pot-interface.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['reference','function','electrical_value','candidate_mpn','terminal_number','net','status'])
 for c in controls:
  part=parts[c['reference']]
  for pin,net in sorted(part['pins'].items()):
   w.writerow([c['reference'],c['label'],part['value'],c['pot_candidate_mpn'],pin,net,'Interface draft; verify maker terminal view/CW sense; no wire lengths released'])
