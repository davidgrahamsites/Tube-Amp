---
id: DEC-022
type: decision
domain: cross-domain
status: documented
updated: 2026-11-26
---
# Preserve step-by-step engineering mathematics

FB-148 requires all engineering calculations and solutions to be saved alongside choices so the design can be followed mathematically. Record equations, symbols/units, sourced inputs, assumptions/tolerances, substitutions, results, independent checks, failure cases and the linked decision. Preserve superseded approaches and limits; never turn an illustrative value into a design limit.

Canonical calculations and machine-readable receipts stay with the owning engineering task. The [Luna calculation narrative](../../docs/design-journal/calculations/CONTEXT.md) provides readable derivations linked to those artifacts and the choices history. Current [packaging workbook](../../plans/power-packaging-synthesis/calculations/CONTEXT.md) records16 nominal/hypothetical calculations, while [capacitor arithmetic](../../engineering/component-selection/power-film/results/assembly-options.json) owns exact-candidate body/lead/array calculations. [VAL-077](VAL-077-power-packaging-review.md) records their scope.

Apply prospectively at every meaningful checkpoint; audit/backfill previous calculations through the journal queue without claiming all historical derivations are already complete. No physics or circuit change follows from the documentation requirement.

FB-149–151 add the [HTML document standard](../../docs/engineering-reader/document-standard.html): concise maintenance English, local KaTeX equations and a technical vocabulary key. Read the [current engineering status](../../docs/engineering-reader/index.html) before planning the next correction.
