# Rating coverage and missed BOM references

The current source contains 240 physical references (multi-unit symbols count once; power flags are not parts). R304/R314 had already been selected and integrated by VAL-056, but were absent from the central coverage and purchasing register. P133 now records the existing Yageo RT0603BRD0710KL selection and dated C95204 sourcing evidence. This is reconciliation, not a new circuit or package change.

`../check_coverage.py` is now a mandatory step in the selected-BOM factory. Missing references, duplicate coverage and disagreement with explicit source MPNs fail generation before output files are written. Negative controls recreate the R304/R314 omission, duplicate an entry and change its MPN; all are rejected. Existing unselected parts remain explicit; accounting for a part is not electrical qualification.

[The worksheet](results/parts.csv) lists every physical reference, its source rating statement, selection requirement, available selection/package evidence and applicable rating checks. Watts are appropriate for resistors and dissipative devices; capacitors also need voltage/ripple/temperature, contacts need current/voltage, and magnetics need winding/core/VA limits. Old rating text is shown as declared source information, not silently promoted to a proven limit. Final worst-case evidence must be supplied by each owning electrical module. This240-reference inventory covers the current circuit source, including optional/DNP positions; it does not count additional PCB interface headers, mating contacts, wire or mounting hardware maintained outside that source. Their harness/assembly BOM gates remain separate.

## C605 selection reconciliation

The first check against the staged canonical registers also rejected C605: the source and native schematic already specify CC1206JRNPO0BN331, but committed P093 still called it a candidate. A pre-existing working correction pointed to a nonexistent evidence file. P093 and the candidate record now point to this reconciliation and the existing [manufacturer-backed component dossier](../evidence/reverb-repair-picks-2026-11-21.md). The current source, native schematic and Reverb footprint agree on the exact330pF/5%/100V C0G part and1206 geometry, REC_OUT to REC_FB. The [local-loop adoption review](../../whole-amp/pcb-measured-r/review/local-loop-review.md) records the prior placement repair; no new capacitor substitution occurred here.

The same identity check verifies R304/R314 source, native resistor identity, pads and nets. All native schematic and board hashes match baseline c006f05; no re-routing or DRC rerun is needed for a register-only change. The dated global C605 listing does not prove current domestic availability or full circuit/assembly qualification.

## Bounded R304/R314 check

[Manufacturer RT V17](../../whole-amp/control-switching/evidence/Yageo-RT-2026.pdf), pages2/4/5/6, establishes 0.1W at70°C, linear derating to zero at155°C, 75V maximum working voltage additionally limited by power, and maximum body1.7×0.9×0.55mm. The existing VAL-056 screen bounds each resistor by5.25V across at least9.8kohm, giving2.8125mW. The rating allows64.706mW at100°C (4.35% utilization) and35.294mW at125°C (7.97%). This leaves adequate resistor power margin within that declared screen; no larger package is justified by this bounded load alone.

No new ESD, abnormal supply, thermal measurement or controller sequencing pass is implied. The resistance range is an engineering allocation; actual hot/aged limits and local ambient remain to verify. The pre-existing whole-controller phantom-power issue is still open. Exact footprint integration remains VAL-056; no native files were changed here.

## Purchasing and remaining work

The retained November25 listing observation had minimum-buy field1 and conversion field20. The BOM therefore leaves purchase quantity and price unknown instead of turning either field into an invented quote. Current availability, actual order increment and delivered Shanghai price still require verification. No purchase was made.

Complete per-part operating/transient/fault and thermal evidence, resolve unselected parts, and carry package/heatsink/harness envelopes into the populated three-board chassis. Objective6 remains incomplete. A complete reference inventory cannot establish build readiness.
