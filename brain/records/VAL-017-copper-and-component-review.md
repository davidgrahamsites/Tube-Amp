---
id: VAL-017
type: validation
domain: cross-domain
status: verified
updated: 2026-11-21
---
# Copper geometry and component review

## Claim and limits
Verified scope: 90 simple right-angle joins on the Reverb draft were chamfered; its native DRC and the four-board pad contract pass. This does not establish current capacity, EMI/RFI immunity, thermal performance, full routing or assembly fit. No fabrication release.

## Requirement and implementation
FB-075 adds interference control, current-appropriate trace widths and no sharp bends. The [routing contract](../../engineering/whole-amp/pcb-measured-r/routing-requirements.md) assigns return paths, heater pairs, rectifier loops, shields, relay suppression and protective earth without breaking functional blocks. Rear wood remains independently removable; drill access includes the chuck/body and withdrawal path. These are requirements, not completed physical tests.

The read-only copper audit and temporary chamfer generator have separate jobs. Starting from c4a121e, only the Reverb candidate was adopted. Each accepted right-angle join was trimmed by at most0.20mm and one quarter of either leg, then joined by a diagonal. Nets and widths did not change. Main/Power/Control source boards and all paired project/rule files are unchanged. Temporary candidate DRC produced28 missing-library warnings; checking the adopted board in its original project path resolved these. No rules or exclusions were relaxed.

## Checks
- [Adoption manifest](../../engineering/whole-amp/pcb-measured-r/review/chamfer-integration.json):90 changes, adopted Reverb SHA256 d504b26a4a76971c1e9ba0939e9bce23933df0f0b174de679f211cfd2432be03.
- [Fresh Reverb DRC](../../engineering/whole-amp/pcb-measured-r/review/Reverb-drc.json):0 violations,0 unconnected items under original rules, KiCad10.0.6.
- [Pad check](../../engineering/whole-amp/pcb-measured-r/review/final-checks.json):444 connected-pad mappings match,10 explicit no-connect pads. Main/Power/Control retain105/39/99 unconnected items. This is pad-contract verification, not full assembly-schematic parity.
- [Copper audit](../../engineering/whole-amp/pcb-measured-r/review/copper-audit.json):Reverb has no simple endpoint bends above45.1degrees. Main/Power/Control each retain one candidate. Pad/via/branch junctions, zones and interior intersections need separate review. The Main/Power candidates are width transitions; Control is a46.157degree join. None is silently waived.
- [Native copper preview](../../engineering/whole-amp/pcb-measured-r/review/chamfered-reverb.svg) rendered and visually inspected. Chamfers are visible; overall routing/return loops still need review.

Widths currently span0.3–0.6mm across the drafts; Reverb uses0.3mm. Every audited path remains pending RMS/startup/fault-current, copper thickness, temperature-rise, voltage-drop and via/pad-neck qualification. A generic minimum width is not an ampacity calculation. No new electrical simulation or powered test was performed in this checkpoint.

## Parts and fit corrections
[Speaker/socket research](../../engineering/component-selection/evidence/electric-speaker-sockets-2026-11-21.md) identifies a283mm manufacturer cutout for the Celestion Seventy80 reference, versus received270mm. Diameter shortfall13mm does not authorize cutting the cabinet. Rear-mount cone/surround/gasket clearance remains unresolved. Socket drawings supply partial envelopes; nine-pin mounting pitch, electrical/thermal ratings, retainers and low-quantity domestic supply remain open. Canonical dimensions and the refreshed fit screen retain these limits.

[Connector/capacitor research](../../engineering/component-selection/evidence/electric-reverb-connectors-and-capacitors-2026-11-21.md) rejects C605's50V candidate against its63V requirement. YageoCC1206JRNPO0BN331/C527285 is a100V C0G candidate; mainland RMB availability and native1206 conversion remain pending. It is not selected. JST XH mating parts and contact counts are recorded, but2.50mm versus native2.54mm pitch and retention/clamping remain unresolved. No new BOM selection is implied by candidate research.

## Next action and human check
Qualify major component envelopes and current budgets before changing board outlines. Resolve speaker fit, socket/retainer geometry and magnetics, then allocate the intact functional blocks in a common assembly. Check the rear-cover removal and complete driver-tool envelope. Complete routing, remaining bend/junction review, expression control and electrical corner cases. Bench hum/RF/temperature checks remain necessary after prototype assembly.

## ICM checkpoint
Scoped ICM checks report clean for PCB integration, mechanical fit, component selection and brain. The selected BOM rebuild remains44MPNs/134references/60groups; no candidate was promoted. Manual seam review confirms read-only audit, temporary mutation factory, canonical requirements/registers and generated evidence remain separate. Four audit hashes match current native boards; the other three boards and all project/rule files match the pre-change revision. `git diff --check` passes.
