---
id: VAL-076
type: validation
domain: components
status: documented
updated: 2026-11-26
---
# Shared heater-reference compatibility

[HD-002 review](../../engineering/component-selection/heater-divider-rating/interface-review.md) records 38 completed generic-model cases, 14 with no shared HREF interval under conservative JJ EL34/ECC83S heater-cathode limits and the assumed 8 V RMS heater ceiling. Two longer/finer repeats reproduce the failure with cathode-peak differences below 1 mV. An independent interval audit checks 114 group windows and preserves all 22 native files.

The existing reference is 33.177 kΩ nominal, exceeding the reference EL34's 20 kΩ DC limit even with a stiff source. A higher-wattage R506 cannot fix the voltage-window conflict. Isolated heater groups and an explicitly bounded preamp rail/reference are the next candidate, not an adopted circuit. The 355 V preamp case also has an empty preamp-only interval, so merely splitting the groups is insufficient. Exact sourced tube limits, supply/startup/fault behavior and actual thermal/physical evidence remain open. No new parts, transformer winding or native layout adopted; no fabrication release.

This diagnostic follows [VAL-075](VAL-075-heater-divider-rating-boundary.md). Its narrative is captured by the [Luna design journal](../../docs/design-journal/CONTEXT.md), which is derived from the engineering evidence and does not replace it.
