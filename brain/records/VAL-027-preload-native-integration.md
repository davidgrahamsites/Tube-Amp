---
id: VAL-027
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# 5 V minimum-load repair integrated and checked

Owner: Renegade integration. Existing FB-114–116 repair, sourcing and socket requirements remain in force. This checkpoint advances T06/T08, not closure of the six scopes.

[Preload review](../../engineering/whole-amp/aux-supply/preload-review.md) owns the exact source/native/PCB change, part/package data, suppliers, load/thermal assumptions, native reports and remaining holds. R215 820 Ω is added across5 V/GND using UNI-ROYAL MFR0W4F8200A50 engineering selection. Source, native sheet, Control board andP129 agree. Maximum-case package, round lead and0.9 mm PTH are checked against the manufacturer drawing; both native Excellon hits verified.

72 updated raw-supply runs and2 limiting half-timestep repeats complete. Minimum-load failure is removed inside the declared envelope;41 cases retain other flags. Worst assumed winding RMS0.2851 A and conditional four-regulator heat4.167 W keep transformer/thermal selection open. Static reset-release review confirms the existing G50/4.75 V incompatibility rather than claiming a new startup pass.

Native preservation checks pass: exactly one new component/two endpoints, every old component/endpoint/geometry unchanged, no new ERC/DRC findings. Existing Control 90 unconnected/13 wire-courtyard violations remain; final three-board conversion is pending. Schematic and PCB renders visually inspected within R215 scope; existing readability/bypass/socket defects remain.

Domestic search redirects to login; current Chinese stock/price/MOQ and exact Shanghai shipment are not verified. No purchase, account change, supplier contact or upload. All ICs/tubes remain socket-required. Actual tool clearance remains pendingNovember 25. Next is the existing supervisor/relay-chain fix and exact auxiliary transformer/socket/heatsink qualification. No fabrication release.
