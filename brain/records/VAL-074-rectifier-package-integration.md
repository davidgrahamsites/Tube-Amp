---
id: VAL-074
type: validation
domain: pcb
status: documented
updated: 2026-11-26
---
# Selected rectifier identity and package integration

[Review](../../engineering/whole-amp/pcb-measured-r/rectifier-package/review.md) records D3–D6 BY255P-E3/54 adoption across source, connectivity, readable schematic and Power PCB, correcting the stale 1N4007/STTH112/DO-41 mismatch. The selected MPN and two-series-diode topology are preserved. Manufacturer maximum 1.32 mm leads require the new 1.7 mm nominal holes; proposed finished-hole tolerance yields 0.28 mm minimum diametral allowance.

All 145 net groups, 20 other native files and 17 unaffected schematic pages are preserved. ERC1 and Power DRC12/39 opens remain unchanged; no new finding under existing rules. Exact native/drill/route delta, evidence hashes and visual review pass. Four support footprints move; mounts and outline remain fixed. Refreshed mechanical inventory and maximum diode/support-resistor envelopes carry the new geometry to fit work.

Historical sourcing and electrical assumptions are not upgraded by a native pass. BY255 repetitive pulse/heat, actual transformer and transient reverse-voltage limits, conductor current capacity, three-board populated fit and full drill access remain open. No fabrication release; objective6 remains active. Next: source-bound operating/fault ratings and remaining exact packages, then populated chassis packing.
