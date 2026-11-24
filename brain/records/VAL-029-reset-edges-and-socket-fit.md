---
id: VAL-029
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Reset edges, socket candidates and chassis envelope

Owner: Renegade integration. Advances T06/T08/T10; no build or manufacturing release.

[Reset review](../../engineering/whole-amp/control-switching/edge-review.md):
two unused gates in the existing socketed HC14 now condition reset while
preserving active-low polarity and the control functional block. Six intended
pin changes, 27 new 0.3 mm tracks and one 0.4 mm via pass independent native
graph, preservation, layer-aware connectivity, drill-delta and negative-control
checks. No new ERC/DRC finding; existing ERC1 and Control DRC13 remain. Control
unconnected items drop from 84 to 79. Native schematic PDFs were visually reviewed
at whole-page and detail scale; reset wiring and power labels are readable.

The edge bound is 19 ns at the stated 4.5 V/50 pF/−40…85 °C datasheet conditions,
with 30 pF output trace/socket budget after two HC74 clear inputs. Actual load,
startup/brownout and clock recovery timing remain unqualified. The TPS3890 model
does not discharge CT on manual reset although the datasheet requires it; the
unmodified model discrepancy is documented, not converted into a hardware failure
or an invented pass. G50 release threshold and replacement/carrier remain open.

[TE socket candidates](../../engineering/component-selection/socketing/te-candidate-review.md):
domestic loose stock verified for 1-2199298-2 and -3. Rated contact/tail/body
evidence replaces incomplete candidate assumptions. Full mating tolerances,
current drawing revision, actual sample and retention still require qualification.
All sockets remain the default; no performance-based exception has been adopted.

[Mechanical screen](../../engineering/whole-amp/mechanical/review/socket-fit-checks.json)
consumes the socket module's provisional envelope. All five DIP footprints need
Ø1.0 mm holes and expanded courtyards for these candidates; current holes are
Ø0.8 mm. Candidate body boxes do not overlap supported neighboring courtyards.
That is not a complete collision check. Stack height is conservatively 10.38 mm,
with proposed 12 mm assembly reserve plus 15 mm removal reserve. Populated
three-board placement, actual tool access and extraction remain open. Back wood
stays mechanically independent; drill dimensions remain deferred to November 25.

Scoped ICM checks are clean for control-switching, socketing and mechanical.
The design seams remain separate: electrical net contract, component socket
envelope, read-only mechanical consumer, native CAD and generated evidence.
No purchase, supplier communication or fabrication upload occurred.
