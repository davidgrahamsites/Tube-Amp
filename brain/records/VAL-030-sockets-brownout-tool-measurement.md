---
id: VAL-030
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Socket holes, brownout evidence and partial tool measurement

Owner: Renegade integration. Advances scopes3/4/6; does not close the six-scope goal.

[Socket correction](../../engineering/component-selection/socketing/footprint-review.md): five candidate footprints now use52 Ø1.0mm holes and enlarged socket/IC courtyards. C352 moves0.3mm with four declared trace endpoint changes. Netlist, other drills/slots and unrelated native geometry preserved. No new ERC/DRC findings. Control13 existing/79 unconnected; Reverb0/0. Current drawing/sample/retention and other socket assemblies remain open.

[Brownout review](../../engineering/whole-amp/control-switching/brownout-review.md):36 bounded runs complete. Coarse timestep check failed; subsequent refinement passes unchanged25µs tolerance. Endurance/noise margin, guaranteed assertion, actual rail collapse, clock recovery and carrier remain unqualified. Existing G50 release issue remains; replacement not adopted.

[CAD receipt](../../engineering/whole-amp/mechanical/review/socket-fit-cad-checks.json): five conservative socket/IC bounds and provisional27mm service volumes are added to the existing board-placement diagnostic. Native reopen and nine-solid STEP positions pass; no intersections among the specifically modeled service/board/socket solids. Other components are omitted. Existing support planes still exceed width by41mm and depth by20mm. This is not an approved chassis or populated fit.

[Tool measurement](../../engineering/whole-amp/mechanical/review/tool-access-review.md): FB-120 supplies46mm chuck diameter. Proposed2mm radial margin gives50mm cross-section. Bit reach and body/length remain unknown, so screw access stays open. The rear wooden cover remains structurally independent.

FB-118 reaffirms all-path current sizing; FB-119 exposes a genuine U12 square T despite zero simple-bend candidates. Both remain explicit routing work. Next: repair and independently check that geometry, then current budgets and populated three-board layout. No fabrication release, purchase or supplier message.
