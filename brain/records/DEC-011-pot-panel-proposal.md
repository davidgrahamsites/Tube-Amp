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
Ten panel-mounted controls in two rows of five; 42mm horizontal and34mm vertical centre spacing. AlphaRV24AF15R1 smooth6.35mm shaft candidates and MableMAKP0437S6.4mm set-screw pointer knobs. 2mm aluminium is a study thickness. Panel outside profile, fastening, antirotation holes, nut/washer stack, actual knob bore depth and printed scale remain unqualified. No exact panel/knob purchase or machining released.

The register owns geometry and the circuit owns terminal nets. Factories generate face/underside envelopes, full-size and tiled PDFs, and a30-terminal pot interface. The194×60mm knob envelope has8mm minimum inter-knob gap against the assumed26mm sweep. The312×67 rectangular screen is not the actual curved cabinet opening. It cannot prove fit.

## Evidence and next check
[Mechanical assessment](../../engineering/whole-amp/mechanical/review/electric-packaging-panel-2026-11-21.md), [pot/knob evidence](../../engineering/component-selection/evidence/control-panel-parts-2026-11-21.md), [canonical register](../../engineering/whole-amp/mechanical/fit-register.json), [paper tiles](../../engineering/whole-amp/mechanical/review/panel-study-A4-tiles.pdf), [terminal interface](../../engineering/whole-amp/mechanical/review/panel-pot-interface.csv).

User requested clearer measuring instructions and a generated illustration. [Guide](../../engineering/whole-amp/mechanical/review/measurement-guide-2026-11-21.md) defines P1/P2/P3,S1,T1/T2/T3; it is teaching material, not evidence of dimensions. Await these missing measurements without re-requesting the467mm width,160mm depth or existing speaker bolt readings. Then allocate speaker, socket/tube/service paths, magnetics, pots and boards in one assembly before freezing chassis and PCB outlines.

## Received cabinet interface and tube visibility — November 21
[Six received photographs and review](../../engineering/whole-amp/mechanical/review/received-cabinet-photo-intake-2026-11-21.md) record the user-reported rear-cover edge/top-underside alignment. Develop flange/bracket-supported folded metalwork; exact face elevation, supports and fastening remain unresolved. A flange-mounted face may still be recessed. Preserve independent rear-cover removal.

User requests natural tube glow through the two oval rear slots **only where compatible with the compartmentalized functional blocks**. This conditional appearance preference is accepted; tube positions and visibility are not yet verified. Electrical layout, protection, cooling and service access take priority. Do not split a functional block merely to show a tube in each slot. The canonical dimensional/interface fields are `mounting_interface` and `tube_visibility` in the mechanical register.
