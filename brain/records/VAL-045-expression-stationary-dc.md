---
id: VAL-045
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Expression controller stationary DC

[Owned review](../../engineering/whole-amp/expression-control/settled-bias-review.md) records 24 settled cases and 107 passing evidence checks. Longer explicit settling resolves the sampled direct-OP failures of VAL-044 without replacing the physical controller or manufacturer models. Numerical timestep/duration/initialization refinements agree within 10µV. A separate weak-shunt perturbation exceeds that screen at the off-state ABC node by reaching 27.071µV change, while audio output changes 7.622nV; this sensitivity is retained.

This is powered-circuit steady DC, not cold start or full expression-feature qualification. Pedal protection, reverse-junction stress, actual reference/supplies, integration, socket carrier and Shanghai procurement remain open. No native PCB, block, mounting or drill change; all six through-chassis scopes remain active. Next: protected selector/polarity mapping and startup/hot-plug validation, followed by native integration and populated fit.

[Pedal-port implementation proposal](../../engineering/whole-amp/expression-control/pedal-port-design.md) now records control states, current/range budget, jack variants, passive tip/ring fault ambiguity and unverified domestic purchasing. No new behavior approval or hardware selection is inferred.
