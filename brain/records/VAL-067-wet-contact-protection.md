---
id: VAL-067
type: validation
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Local wet-contact clamp correction set

[Owned review](../../engineering/whole-amp/reverb-600/wet-protection/review.md) investigates opposing-series Vishay BZX55C27-TAP diodes across WET_AC/GND. No native change. 1,024 DC tolerance combinations, 96 AC loading comparisons and 85 SPICE cases establish a conditional envelope near 40.056 V with at most 0.01033 dB capacitance-induced gain change. Independent DC/AC checks and half-timestep contact repeat pass.

Clamping exposes a companion defect: R618 exceeds its existing 250 V requirement at the expanded 344.3 V supply corner and reaches 306.773 V at 400 V. Preserve 1 MΩ but carry the known 350 V MF0207 package into the same correction set. R616's capacitor-discharge pulse is about 0.882 mJ; a PR01 100 Ω/5% candidate passes a conservative isolated-event pulse screen. Actual capacitive contact life, nonlinear loading, repeated-fault behavior and native integration remain open.

Exact DigiKey China Zener and PR01 listings are indexed purchase leads with quantity-one prices, not live stock or Shanghai checkout verification. Different-brand LCSC parts are not treated as interchangeable. The next action is to qualify the complete local correction set and integrate it with fresh native and voltage-domain checks; retain all functional blocks. All six scopes and fabrication release remain open.
