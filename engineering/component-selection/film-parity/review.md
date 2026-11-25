# Film-capacitor source, schematic and board parity

Updated 2026-11-25. This corrects hidden part metadata for 15 already adopted capacitors. No value, connection, functional block, board geometry or mounting hole changes. `contract.json` identifies the exact references and retained manufacturer evidence; `results/checks.json` is the reproducible gate.

| Part | References | Native geometry |
|---|---|---|
| KNSCHA MEB104J63V82CB0236, 100 nF, 5%, 63 V | C203, C206, C210, C213, C604, C610–C615 | two round 0.9 mm nominal holes, 5 mm pitch |
| KNSCHA MEB105J63V82CB0235, 1 µF, 5%, 63 V | C301, C311, C606, C607 | two round 0.9 mm nominal holes, 5 mm pitch |

All 15 have matching selected MPN and footprint in circuit source, native schematic and existing board. Four schematic sheets change hidden fields only. All 144 named pin partitions and 236 component identities are preserved except declared metadata. All 18 rendered pages are pixel-identical before/after; ERC retains its single existing finding. Four boards and 14 other schematic files are byte-identical. No electrical resimulation is needed for this metadata-only change. This does not requalify prior simulations or the complete schematic.

Manufacturer drawings give maximum bodies 7.7×3×7 mm (100 nF) and 7.7×5.5×11 mm (1 µF). The 1 µF drawing specifies 0.6±0.05 mm round leads and 5±0.5 mm pitch. Nominal holes are compatible with the lead shape; finished-hole tolerances and practical lead forming remain fabrication/assembly checks, not proven by nominal dimensions. The 100 nF drawing gives 0.5 mm nominal leads; no unstated tolerance is assumed.

## Chinese procurement evidence

[ICkey 100 nF listing](https://www.ickey.cn/brand/34831/020115/2.html) observed November 25 lists 1,556 units, MOQ10, increment1, RMB0.2607 each at10+, mainland delivery including VAT, one working day. Its through-hole 5 mm description matches the manufacturer part. [ICkey 1 µF listing](https://www.ickey.cn/brand/34831/020115/1.html) lists 45,140, MOQ5, RMB1.1355 at5+, but incorrectly labels the package SOT-23. That alternate is on hold until exact radial-film identity is confirmed. These are displayed listing quantities/prices, not reserved stock or delivered quotes.

Existing LCSC identities are C3034535 and C3975271. Direct stock retrieval returned HTTP405 for both; historical stock figures are not presented as current. See `results/sourcing.json` for URLs and failed retrievals. Mainland delivery is a plausible Shanghai route, but destination-specific checkout is unverified. Nothing was ordered or sent to a supplier.

## Stale bypass record discovered

C351–C353 are not part of this film update. Their native source already selects Yageo CC0805KRX7R9BB104, and their boards already use 0805 SMD footprints. The current working coverage agrees; committed coverage P076 still names the superseded film part. The working registry cites a missing `evidence/local-bypass-relay-2026-11-21.md`. Preserve the ceramic implementation; resolve its documentary source and scoped registry commit next. Do not replace it merely to match stale committed data.

## Remaining boundary

This closes the film metadata mismatch raised by VAL-056. Procurement qualification, complete power sequencing, outstanding native circuit integration and routing, three-board consolidation and populated cabinet/drill fit remain open. All six goal scopes are incomplete; no fabrication release.

Reproduce with `python3 engineering/component-selection/film-parity/tools/check.py`. The one-time synchronizer is baseline-guarded and must not be replayed on a later revision. Human check: inspect manufacturer marking, actual leads, body clearance and finished-hole fit before assembly.
