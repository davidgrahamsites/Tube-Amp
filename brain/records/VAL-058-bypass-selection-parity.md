---
id: VAL-058
type: validation
domain: components
status: documented
updated: 2026-11-25
---
# Existing ceramic bypass selection reconciled

[Owned evidence](../../engineering/component-selection/evidence/local-bypass-selection-2026-11-25.md) resolves VAL-057's stale P076 registry and missing evidence pointer. C351/C352/C353 already use Yageo CC0805KRX7R9BB104 in source, native schematic and 0805 board. All23 native files remain byte-identical; only scoped selection records and evidence change. Exact manufacturer PDF retained and Chinese LCSC C49678 identity verified; current stock, MOQ, price and Shanghai checkout remain unverified.

This is documentary parity, not new electrical/layout qualification. Preserve C351's proper ground return when U1F is repurposed by the pending power-sequencing circuit. Next: complete power-sequencing integration with unresolved phantom powering handled, then remaining native routing and populated three-board chassis fit. All six scopes remain incomplete; no fabrication release.
