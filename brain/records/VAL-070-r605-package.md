---
id: VAL-070
type: validation
domain: pcb
status: verified
updated: 2026-11-25
---
# Conditional R605 package integration

The small R605 footprint is replaced with the documented FMP200 candidate envelope, 15.24 mm pitch and 0.9 mm holes. This verifies package integration only; hot/fault and Chinese purchasing qualification remain open.

[Review and remaining limits](../../engineering/whole-amp/pcb-measured-r/r605-package/review.md) records baseline 306efaa, exact local routing, manufacturer dimensions and thermal screens. [Independent checks](../../engineering/whole-amp/pcb-measured-r/r605-package/results/checks.json) confirm unchanged 240-component/145-net topology, all 18 schematic rasters and all 54 other Reverb footprints. Fresh Reverb DRC0/opens0; ERC unchanged. Two component holes move/grow and one via is added; other drills and chassis mounts remain unchanged.

The generated [component envelope](../../engineering/whole-amp/pcb-measured-r/r605-package/results/package-envelope.json) reserves 7.2 mm above PCB top, including an unqualified 3 mm standoff. This is not assembled-fit evidence. At 100°C the direct 18 V RMS resistor stress screen fails; typical op-amp protection is not credited. No fabrication readiness claim.

VAL-069 current calculation and the 72-case auxiliary supply sweep/four refinements were rerun against the metadata-updated source; numerical results are unchanged and42 supply cases remain flagged. FB-141 makes applicable stress ratings and packages mandatory for every part. Next: remaining power-part and legacy-hole checks, exact driver thermal/fault design and populated three-board assembly. Objective6 remains incomplete.
