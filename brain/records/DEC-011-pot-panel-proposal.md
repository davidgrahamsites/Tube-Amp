---
id: DEC-011
type: decision
domain: cross-domain
status: proposed
updated: 2026-11-21
---
# Pot mounting panel and cabinet packaging proposal

## Requirement
User requires a physical panel carrying the pots. Original electric controls and received yellow cabinet stay. Panel bears knob torque; PCB solder joints are not the mechanical support.

## Proposal, not frozen geometry
Ten panel-mounted controls in two rows of five; 42mm horizontal centre spacing,22mm between rows and21mm row offset. This supersedes the earlier aligned34mm row-spacing study after FB-073 reported only53mm clear depth. AlphaRV24AF15R1 smooth6.35mm shaft candidates and MableMAKP0437S6.4mm set-screw pointer knobs. 2mm aluminium is a study thickness. Panel outside profile, fastening, antirotation holes, nut/washer stack, actual knob bore depth and printed scale remain unqualified. No exact panel/knob purchase or machining released.

The register owns geometry and the circuit owns terminal nets. Factories generate face/underside envelopes, full-size and tiled PDFs, and a30-terminal pot interface. The revised215×48mm knob envelope has4.414mm minimum inter-knob gap and2.5mm rectangular-edge clearance against the assumed26mm sweep. The307×53mm screen uses the conservative end of user-reported307–308mm width and approximate53mm depth. Actual curved-edge, elevation, finger access and fitted knob seating remain unverified. The older194×60mm envelope/312×67mm screen is retained as superseded geometry in the register.

## Evidence and next check
[Mechanical assessment](../../engineering/whole-amp/mechanical/review/electric-packaging-panel-2026-11-21.md), [pot/knob evidence](../../engineering/component-selection/evidence/control-panel-parts-2026-11-21.md), [canonical register](../../engineering/whole-amp/mechanical/fit-register.json), [paper tiles](../../engineering/whole-amp/mechanical/review/panel-study-A4-tiles.pdf), [terminal interface](../../engineering/whole-amp/mechanical/review/panel-pot-interface.csv).

User requested clearer measuring instructions and a generated illustration. [Guide](../../engineering/whole-amp/mechanical/review/measurement-guide-2026-11-21.md) defines P1/P2/P3,S1,T1/T2/T3; it is teaching material, not evidence of dimensions. P1/P2-clear and383mm P3 inside height are now recorded (FB-073/074), together with270mm aperture and149.5×60×36.5mm tank. Do not re-request them. Next allocate speaker, socket/tube/service paths, magnetics, pots and boards in one assembly before freezing chassis and PCB outlines.

## Received cabinet interface and tube visibility — November 21
[Six received photographs and review](../../engineering/whole-amp/mechanical/review/received-cabinet-photo-intake-2026-11-21.md) record the user-reported rear-cover edge/top-underside alignment. Develop flange/bracket-supported folded metalwork; exact face elevation, supports and fastening remain unresolved. A flange-mounted face may still be recessed. Preserve independent rear-cover removal.

User requests natural tube glow through the two oval rear slots **only where compatible with the compartmentalized functional blocks**. This conditional appearance preference is accepted; tube positions and visibility are not yet verified. Electrical layout, protection, cooling and service access take priority. Do not split a functional block merely to show a tube in each slot. The canonical dimensional/interface fields are `mounting_interface` and `tube_visibility` in the mechanical register.

## Rear-cover mounting prohibition — FB-070
User explicitly prohibits mounting the chassis or control panel to the removable rear wooden cover. This includes secondary/shared supports; earlier “not sole support” wording was too permissive. Mount only to fixed cabinet structure. Keep rear-cover screws accessible and allow its removal without releasing chassis/control-panel mounts. Exact fixed-structure brackets and assembly path remain unverified.

## PCB support flange and tool access — FB-071
User requires a broad flange beneath the board so an electric drill can be used. Working interpretation: a metal chassis/support flange, with its fixing screws beyond the PCB edge; the PCB sits on standoffs. Do not choose a flange width from bit diameter alone. Include chuck/body clearance, screw engagement and removal travel, and straight approach/withdrawal without striking electronics or cabinet wood. Tool model/envelope, flange width and screw setback remain null in the canonical `pcb_support_tool_access` interface. Check stiffness, fastener edge distance and electrical clearance as part of the same assembly. Drill/deburr metalwork before electronics installation and remove swarf. FB-070 continues to prohibit any attachment to the removable rear cover.
