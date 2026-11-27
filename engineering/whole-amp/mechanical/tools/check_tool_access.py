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
    'scope': 'Partial tool dimensions and conservative chuck cross-section; not a swept collision test',
    'source_feedback': tool.get('latest_source_feedback', tool['source_feedback']),
    'clearance_chuck_diameter_mm': diameter,
    'latest_reported_chuck_diameter_mm': tool.get('latest_reported_chuck_diameter_mm', diameter),
    'chuck_diameter_conflict': tool.get('latest_reported_chuck_diameter_mm', diameter) != diameter,
    'latest_source_feedback': tool.get('latest_source_feedback', tool['source_feedback']),
    'bit_projection_beyond_chuck_mm': tool['bit_projection_beyond_chuck_mm'],
    'bit_tip_to_tool_back_mm': tool['bit_tip_to_tool_back_mm'],
    'chuck_front_to_tool_back_mm': (tool['bit_tip_to_tool_back_mm'] - tool['bit_projection_beyond_chuck_mm']) if tool['bit_tip_to_tool_back_mm'] is not None and tool['bit_projection_beyond_chuck_mm'] is not None else None,
    'chuck_radius_mm': diameter / 2,
    'motor_body_width_mm': tool['motor_body_width_mm'],
    'proposed_motor_width_with_allowance_mm': tool['motor_body_width_mm'] + 2 * margin if tool['motor_body_width_mm'] is not None else None,
    'motor_width_scope': 'Across housing only; not a centered circular envelope. Height and axis offset remain unknown.',
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
