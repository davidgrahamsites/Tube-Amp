"""Screen the reported tool cross-section; never infer a full screw-access pass."""
import hashlib
import json
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
source = MODULE / 'fit-register.json'
register = json.loads(source.read_text())
tool = register['drill_tool_measurements']
diameter = tool['chuck_diameter_mm']
margin = tool['provisional_radial_allowance_mm']
assert diameter > 0 and margin >= 0
missing = [k for k in (
    'chuck_axial_length_mm', 'bit_projection_beyond_chuck_mm',
    'motor_body_width_mm', 'motor_body_height_mm',
    'motor_body_offset_from_axis_mm', 'bit_tip_to_tool_back_mm'
) if tool[k] is None]
result = {
    'scope': 'Reported chuck cross-section only; not a swept tool collision test',
    'source_feedback': tool['source_feedback'],
    'measured_chuck_diameter_mm': diameter,
    'chuck_radius_mm': diameter / 2,
    'proposed_radial_allowance_mm': margin,
    'proposed_cross_section_diameter_mm': diameter + 2 * margin,
    'conditional_axis_to_obstruction_mm': diameter / 2 + margin,
    'condition': 'Only where an obstruction overlaps the chuck axially. This is not a flange width; fastener edge distance and the larger body must also be allowed for.',
    'missing_tool_measurements': missing,
    'fastener_positions_known': register['chassis_service_study']['fastener_positions_mm'] is not None,
    'full_swept_access_checked': False,
    'screw_access_verified': False,
    'fabrication_ready': False,
    'source_used_fields': ['drill_tool_measurements', 'chassis_service_study.fastener_positions_mm'],
    'source_used_fields_sha256': hashlib.sha256(json.dumps({
        'drill_tool_measurements': tool,
        'fastener_positions_mm': register['chassis_service_study']['fastener_positions_mm']
    }, sort_keys=True).encode()).hexdigest()
}
(MODULE / 'review/tool-access-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
