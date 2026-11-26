---
id: VAL-071
type: validation
domain: pcb
status: verified
updated: 2026-11-25
---
# Thirteen FMP200 packages: finished-hole correction

[Review](../../engineering/whole-amp/pcb-measured-r/fmp200-holes/review.md) records manufacturer maximum lead/body dimensions, proposed fabrication tolerance and exact native delta. Main/Power now have 26 corrected resistor holes (0.9 mm) with 1.8 mm pads. Placements, connectivity, tracks, vias, mounts, outlines and source schematics are unchanged. Full parsed-tree comparison, Excellon comparison and disposable baseline replay pass. No new native DRC findings; existing Main43/Power12 findings and Main105/Power39 unconnected items remain.

Package envelopes deliberately leave unqualified assembly heights null. Current socket and board inventories were refreshed. This closes only the hole defect, not thermal/fault qualification or cabinet/drill access. Continue exact part stress/package qualification and populated three-board assembly; objective6 remains incomplete.
