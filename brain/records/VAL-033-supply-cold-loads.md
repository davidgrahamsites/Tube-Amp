---
id: VAL-033
type: validation
domain: schematic
status: documented
updated: 2026-11-24
---
# Supply cold-load correction and current-path evidence

[Load review](../../engineering/whole-amp/aux-supply/load-review.md) reconciles the auxiliary raw-supply model with the existing −25°C relay-driver screen. All three coils now total 53.922 mA at the screen voltage, 23.25% more than the previous room-temperature assumption. R215 remains included. No native schematic/PCB or functional interfaces were changed.

Seventy-two transient cases and four timestep refinements completed; current accounting, freshness and eight negative controls pass. Forty-four cases still flag regulation/winding limits. Maximum conditional winding RMS is 0.2941 A and regulator heat 4.258 W. Rectifier/capacitor RMS and startup-model peaks are retained as conditional trace/ripple inputs, not current-capacity approval.

Source-bound tube heaters total 4.20 A nominal; balance resistors and the existing pilot allowance bring the inventory to 4.3815 A. Heater surge and exact transformer remain open. Chinese catalog/search leads were rechecked without declaring live stock, Shanghai delivery or complete procurement verified.

Next: actual logic/audio/fault budgets, exact auxiliary magnetics and thermal/protection implementation, then copper/contact qualification and populated three-board/chassis fit. All six scopes remain incomplete. Chuck diameter is recorded at 46 mm; full tool access awaits the rest of its envelope.
