---
id: VAL-069
type: validation
domain: pcb
status: verified
updated: 2026-11-25
---
# Conditional reverb current allocation

## Claim and revision
A12-case source-bound passive-load screen supports raising the auxiliary working allocation from50 to70mA per rail, with native R619/R620 separately added. This is verified arithmetic/model evidence only. No complete-current, copper ampacity, physical tank or fabrication claim.

## Method and actual result
[Review and assumptions](../../engineering/whole-amp/pcb-measured-r/current-budget/review.md) bind baseline f51f883 and the current native circuit. Independent resonance arithmetic, KCL, case coverage and four negative controls pass. Conditional10Vpeak envelope needs69.725mA per rail including rail loads;18Vpeak diagnostic needs99.925mA. Neither is a guaranteed hot/fault operating point. Do not use the ideal driver's tank-current bounds as allowed tank settings.

The updated auxiliary72-case sweep and four refinements complete; nine corruption checks pass and42 cases still flag supply limits. Maximum half-winding RMS0.29678A and conditional regulator heat4.2868W. The checker explicitly accounts for the changed working reserve when comparing historical results. No native circuit, board, socket, block or chassis edits.

## Evidence
- [Editable assumptions](../../engineering/whole-amp/pcb-measured-r/current-budget/contract.json)
- [Numerical budget](../../engineering/whole-amp/pcb-measured-r/current-budget/results/budget.json)
- [Independent checks](../../engineering/whole-amp/pcb-measured-r/current-budget/results/checks.json)
- [Supply checks](../../engineering/whole-amp/aux-supply/results/loads/checks.json)
- [Trace-width research including FB-140](../../engineering/whole-amp/pcb-measured-r/review/trace-width-research-2026-11-25.md)

## Scope and follow-up
Complete all-board current/thermal/drop/pulse/fault budgets and finish component/transformer selection before native width acceptance. Tank AC/drive evidence, protected Mac test fixture,120/220V fuse coordination, final three-board assembly and body/bit drill envelope remain open. Functional blocks and removable-back requirements remain intact.
