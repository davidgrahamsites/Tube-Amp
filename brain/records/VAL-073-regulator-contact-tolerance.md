---
id: VAL-073
type: validation
domain: components
status: documented
updated: 2026-11-25
---
# Regulator contact tolerance and cooling boundary

[Review](../../engineering/component-selection/socketing/contact-review.md) applies primary Mill-Max rectangular-lead diagonal and contact-compliancy guidance to ST L78/L79 package extrema. All three screened contact types fail complete initial-fit tolerance; replacement retention is also explicitly checked. No exact socket, supplier route or native footprint is adopted. The editable contract, hashed primary PDF and generated check are local to the socketing owner. Positive and negative controls distinguish a virgin fit from a usable replacement fit.

The review carries forward the current auxiliary owner’s conditional shared-sink requirement without creating a second supply model: maximum baseline heat 4.286827 W, required sink-to-ambient no greater than 7.3961 °C/W at assumed 60 °C ambient, 100 °C junction target and 1 °C/W case-to-sink interface. Final parts, insulation, orientation, actual cabinet temperatures and different supply variants still require qualification.

Scoped ICM and contact arithmetic checks pass. A failed contact-range qualification is an engineering result, not a test harness failure. Functional blocks, native layout, default socket requirement and independently removable wooden back remain intact. No fabrication release. Next: purpose-built flat-lead contact or documented regulator/contact pairing; independent heatsink fastening, isolated U7 tab and service extraction; then populated three-board fit. Full drill body/bit envelope remains pending user measurement.
