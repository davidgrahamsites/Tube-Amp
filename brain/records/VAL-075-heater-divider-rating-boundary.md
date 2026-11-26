---
id: VAL-075
type: validation
domain: components
status: documented
updated: 2026-11-26
---
# Heater-elevation rating and fault boundary

[Review](../../engineering/component-selection/heater-divider-rating/review.md) records4,032 DC corners and eight independently checked RC startups. Calculation checks pass; all22 native files are preserved. Under the550V engineering ceiling and tolerance/drift allocation, current R506 reaches550V/1.52355W with C505 short, exceeding the selected500V and100°C derated1.29412W limits. P111 now carries an explicit hold; no part or native circuit is substituted.

PR03/FMP300750V alternatives and two-series-FMP200 pass that bounded resistor case. Exact domestic availability, package/lead forming and actual thermal installation remain unqualified. R507-open and upper-feed-short hazards remain separate: a wattage upgrade cannot protect the heater-reference capacitor/tube interface by itself. Next verify exact heater-cathode limits and the least intrusive complete fault correction, then select and integrate packages. Objective6 remains active; no fabrication release.
