"""Render a service-sequence concept from the canonical fit register; not CAD geometry."""
from pathlib import Path
import hashlib
import json
from html import escape

root = Path(__file__).resolve().parents[1]
source = root / 'fit-register.json'
data = json.loads(source.read_text())
study = data['chassis_service_study']
out = root / 'review'
assert study['block_partition_changed'] is False
area = sum(v[0] * v[1] for v in data['boards'].values())
m = data['cabinet']['user_measurements']
plane = m['A_rear_clear_width_mm'] * m['B_rear_edge_depth_mm']
report = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'received_opening_mm': {'width_range': m['P1_clear_opening_width_range_mm'], 'approximate_depth': m['P2_clear_opening_mm']},
          'received_inside_height_mm': m['P3_obstruction_report']['P3_inside_height_mm'],
          'current_board_area_mm2': area, 'reported_rectangle_area_mm2': plane,
          'unchanged_boards_one_plane_possible': area <= plane,
          'compartments_preserved_by_this_edit': not study['block_partition_changed'],
          'assembly_fit_verified': False, 'tool_access_verified': False,
          'unresolved_access_checks': study['access_verification'],
          'scope': 'Area bound and service architecture only; illustration has no scale'}
(out / 'chassis-service-checks.json').write_text(json.dumps(report, indent=2)+'\n')
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="700" viewBox="0 0 1100 700">',
       '<rect width="1100" height="700" fill="#f4f1e9"/>',
       '<style>text{font-family:Arial,sans-serif;fill:#172c38} .label{font-size:18px} .small{font-size:15px}</style>']
def text(x,y,s,cls='label'):
    svg.append(f'<text x="{x}" y="{y}" class="{cls}">{escape(s)}</text>')
def rect(x,y,w,h,color,stroke='#172c38'):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="{stroke}" stroke-width="2"/>')
text(35,40,'RENEGADE — CHASSIS SERVICE ARRANGEMENT')
text(35,68,'CONCEPT ONLY · NOT TO SCALE · NO HOLE POSITIONS OR FIT APPROVAL','small')
text(35,110,'1  Remove wooden cover')
rect(40,135,440,230,'#d8b970');rect(64,159,392,182,'#f4f1e9')
rect(64,180,20,145,'#607b87');rect(436,180,20,145,'#607b87')
rect(95,200,330,110,'#d9e3e6')
text(130,242,'REMOVABLE METAL CHASSIS')
text(127,271,'Functional blocks remain grouped','small')
for x in [105,415]:
    svg.append(f'<circle cx="{x}" cy="295" r="7" fill="#172c38"/>')
text(46,395,'Retaining screws face rear; tool approaches from outside.','small')
text(46,420,'Supports attach to fixed wood only.','small')
text(46,445,'Wooden cover has no chassis attachment.','small')
text(570,110,'2  Withdraw chassis; service on bench')
rect(575,255,480,25,'#8aa1ad');rect(595,180,335,15,'#4f8069')
for x in [615,900]:rect(x,195,10,60,'#b2b2aa')
text(670,166,'PCB + components','small')
text(620,312,'Standoffs on metal carrier','small')
rect(965,130,60,85,'#b8cbd3')
rect(989,215,12,38,'#506b79')
svg.append('<circle cx="995" cy="265" r="6" fill="#172c38"/>')
text(950,118,'Driver','small')
text(570,355,'Flange projects beyond board edge.','small')
text(570,380,'Keep chuck and body clear, not only the bit.','small')
text(570,405,'Check access from the screw-head side.','small')
text(570,430,'Bench support and withdrawal path still need sizing.','small')
rect(35,485,1020,165,'#ffffff')
text(55,516,'RECEIVED DIMENSIONS — ASSEMBLY CHECK STILL OPEN')
text(55,545,f"Opening {m['P1_clear_opening_width_range_mm'][0]}–{m['P1_clear_opening_width_range_mm'][1]} × approx. {m['P2_clear_opening_mm']} mm; inside height {m['P3_obstruction_report']['P3_inside_height_mm']} mm. User measurements.",'small')
text(55,572,'Tool clearance: screw-axis distance to obstruction ≥ local tool radius + handling margin.','small')
text(55,599,f'Current board area {area:,.0f} mm² exceeds reported plane {plane:,.0f} mm². Repacking required.','small')
text(55,626,'Rails, fasteners, speaker, tubes, transformers, wiring, guard and full removal sweep remain unverified.','small')
svg.append('</svg>')
(out / 'chassis-service-concept.svg').write_text('\n'.join(svg)+'\n')
print(json.dumps(report, indent=2))
