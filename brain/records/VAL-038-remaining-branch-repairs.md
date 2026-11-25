---
id: VAL-038
type: validation
domain: pcb
status: documented
updated: 2026-11-24
---
# Four remaining branch candidates repaired

[Routing review](../../engineering/whole-amp/pcb-measured-r/review/remaining-branches-review.md) records one Power and three Control branch repairs: twelve shortened segments, eight tangent arcs, original widths/nets and every other native atom preserved. Native drill/slot and DRC comparisons pass with no new findings; negative controls reject undeclared defects. Native PDF visual review completed before adoption.

All four boards now have zero exact-endpoint right-angle branch candidates outside pads/vias. This does not close every corner/current-capacity requirement. Power remains 12 violations/39 unconnected and Control 13/79; no rules changed. Socket/native-netlist and panel-interface checks remain passing. Component/block positions and all mounting geometry are unchanged.

Exact parts and China-to-Shanghai procurement, current/insulation qualification, completed routing and populated three-board chassis remain unfinished. Full tool access still needs body/bit dimensions beyond the received 46 mm chuck. No fabrication release.
