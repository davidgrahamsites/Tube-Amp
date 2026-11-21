---
id: VAL-005
type: validation
domain: cross-domain
status: verified
updated: 2026-10-04
---
# Tube matcher v0.1 — scoped offline arithmetic checks

## Claim and revision
Tube matcher **system-design revision 0.1**, in [design.md](../../engineering/tube-matcher/design.md) and [profiles.json](../../engineering/tube-matcher/profiles.json): supply budget, ideal RC discharge and example measurement/mismatch arithmetic are reproducible. Verification is solely computational and structural; it does not validate a circuit, tube, profile operating current or safety mechanism.

## Method
Python 3.13.2, October 4, 2026:

```text
python3 engineering/tube-matcher/calculations.py
python3 /Users/appleadmin/.codex/skills/icm-check/scripts/icm_check.py . engineering/tube-matcher
python3 brain/tools/build_index.py
```

The calculation script checks profile anchor envelopes against instrument ranges, retains unreleased flags, and checks analytic gm/rp examples, positive-input rejection, uncertainty gating and bin boundaries. All example tube currents/slopes are synthetic. ICM Check audits module contracts; brain index validates metadata/unique IDs.

## Actual result
- Calculation script passed **13 numerical checks**, plus two profile anchor/range consistency checks.
- Assumed total input budget **89.8 W**, against **120 W** adapter target; efficiency/allowances are unmeasured.
- Ideal single 22 µF rail at 300 V: **0.99 J**, **7.483 s** to 10 V through 100 kΩ, or **0.748 s** through 10 kΩ. Active resistor initially sees **9 W**. Neither result authorizes guard release; all real stored energy and pulse ratings remain to be established.
- Synthetic 40.0/41.2 mA mismatch **2.956%**, conservative bound with ±1% per value **4.955%**.
- Synthetic 12AX7 gm 1.60/1.62 mA/V with ±2% per value has conservative mismatch **5.242%**; script correctly reports uncertain/retest for a 5% gate.
- Module ICM check returned **ICM CHECK: clean**.
- First brain catalog regeneration exposed an existing DEC-005 ID used by another record. Renamed only this task's new matcher decision to DEC-006 and updated its links; pre-existing decision preserved. Final rerun returned **Catalog generated: 17 nodes; metadata and IDs valid.** Calculation and ICM checks also passed on the final rerun.

## Evidence
[Calculation script](../../engineering/tube-matcher/calculations.py), [machine-readable report](../../engineering/tube-matcher/calculation-report.json), [source register](../../engineering/tube-matcher/sources.md), [DEC-006](DEC-006-tube-matcher.md).

## Scope and follow-up

After the user's app-tracking question, the [app/data contract](../../engineering/tube-matcher/app-data-contract.md) and [synthetic result](../../engineering/tube-matcher/example-result.json) were added. Python parsed the example, checked demo/invalid-calibration exclusion flags, and reproduced gm, rp and mu for both sections from its raw samples. Module ICM check and 17-node catalog regeneration passed again. This checks illustrative data consistency only, not a working app or transport.
No actual tube measurements, metrology calibration, circuit simulation, KiCad schematic/PCB/ERC/DRC, CAD fit, working UI/BLE/firmware, fault injection or energized checks were performed. Proposed profiles remain non-executable design data. Schematic review and physical qualification gates are defined in the design.
