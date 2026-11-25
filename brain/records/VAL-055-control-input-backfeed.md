---
id: VAL-055
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Shared reference and logic-input backfeed

[Owned review](../../engineering/whole-amp/control-switching/control-interface-review.md) proposes a 10 kΩ/100 kΩ input divider for U1E and a 49.9 kΩ series resistor for U1F. The rejected equal-10k trial permits a 0.986 V new-path phantom supply; the revised bound is 0.579 V. This is not a whole-board power-sequencing guarantee.

Twelve scoped screens pass, including 192 RC corners, four independent passive SPICE solutions and six current-integrated RC witnesses. The minimum hold after a full 2 ms fault is 50.549 ms. Three corruption controls are rejected and 91 native/source CAD identities remain unchanged. The audit identifies native C301/C311 directly on logic inputs with no capacitor-to-input series limit. Those defects remain actionable before native control integration.

Exact Yageo 10 kΩ, 49.9 kΩ and 100 kΩ parts have positive Chinese LCSC stock observations and a domestic Shanghai route; the initial 47 kΩ part was out of stock. Full references, source bytes and purchasing fields are retained. No order or supplier message. Next: fix the native debounce input-current paths, verify timing/supply collapse, then readable native integration and remaining three-board fit. All six scopes remain incomplete.
