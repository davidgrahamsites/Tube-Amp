---
id: VAL-039
type: validation
domain: components
status: documented
updated: 2026-11-24
---
# P057 sourcing fallback and full-pitch insertion check

[Package comparison](../../engineering/component-selection/power-film/review.md) adds exact Panasonic EZPV60506MTC as a researched fallback, with RS China quantity-one stock/price observation and domestic delivery-policy basis. Four parts are displayed at RMB415.40 including tax. Exact Shanghai address/date remains unqueried; no order, contact or substitution is made.

Manufacturer revisionR9 establishes lead diameter and both pitch tolerances. All four native footprints match nominal pitch but fail a permitted rigid-lead insertion witness at nominal1.8 mm holes. Centered maximum bodies do not overlap, but four neighbor gaps are9.05 mm against a10 mm manufacturer recommendation. CRC's two existing body overlaps and missing exact lead/grouping information remain unresolved. Do not force leads or adopt a large hole solely from the geometry calculation.

Read-only native checks and controls pass; no circuit, board, functional-block or mounting geometry changed. This is an evidence checkpoint, not a selected-part, completed-routing or chassis release. Continue package/assembly qualification and populated three-board placement; full drill access still needs measurements beyond the received46 mm chuck.
