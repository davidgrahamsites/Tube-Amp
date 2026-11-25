---
id: VAL-050
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Audio-headroom correction and precision monitor

[Owned review](../../engineering/whole-amp/control-switching/rail-monitor-precision-review.md) rejects the previous monitor against the retained10Vpeak signal target. Its five evidence checks pass, while the old circuit acceptance fails. The new REF5050AIDR/LM393BIDR candidate passes14 conditional static screens across16,640 endpoints and2,000 independent nodal comparisons. An8.2k bleeder replaces a failed10k passive off-state trial. All candidates remain outside native CAD.

Exact domestic Chinese stock records support small-quantity comparator/reference routes; complete resistor/socket sourcing and Shanghai checkout remain open. Minimum warning margin is about0.27V, only0.123ms in the isolated100mA capacitor screen. Complete reference/logic sequencing and actual fast-mute timing remain unqualified. No block, board, mount or cabinet change; all six scopes remain active. Next: complete startup/power-down mute interface and exact socketed parts before native adoption.
