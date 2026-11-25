---
id: VAL-043
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Expression supply diagnostics and practical bias

[Owned review](../../engineering/whole-amp/expression-control/supply-bias-review.md) retains nine causal solver cases: the old ±12V timeout starts from an impossible −497.942V output. External-node solver guesses recover a physical solution with seed/refinement checks; stronger shunts alone do not qualify it.

A new reference-fed PNP current-source/current-mirror candidate has24cases:17complete,7failed operating-point cases retained. Nominal1kHz THD is about0.05901%; a control ramp reaches off, but direct low-current solves, trim margin, temperature offsets and startup remain open.133evidence checks pass with `circuit_qualified:false`; native CAD is unchanged.

Diodes MMBT3906-7-F has a dated Chinese LCSC608stock/MOQ1 observation. BC857B-7-F has9000stock/MOQ3000 at that supplier; DEC-017 requires checking Taobao/Pinduoduo alternatives rather than discarding an exact part solely for that MOQ. No orders, exact Shanghai checkout, native adoption, populated fit or six-scope completion.
