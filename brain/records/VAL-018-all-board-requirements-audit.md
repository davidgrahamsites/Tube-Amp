---
id: VAL-018
type: validation
domain: cross-domain
status: documented
updated: 2026-11-21
---
# All-board requirements audit

## Claim and limits
FB-076 requested all PCBs and routing checked against all requirements. All four active electric-build boards were audited. **All four fail fabrication release.** This is a completed evidence/gap review, not completed engineering verification or a repaired design. No native CAD, project rule, schematic, part choice or circuit was changed. No new simulation or powered test was performed.

## Evidence
[Full report and repair order](../../engineering/whole-amp/pcb-measured-r/review/requirements-audit.md) is the canonical assessment. The adjacent requirements matrix individually indexes all 364 imported rules with source hashes, dispositions, evidence and closure work. Counts: 21 FAIL, 331 NOT_VERIFIED, 11 NOT_APPLICABLE and one SUPERSEDED. Partial checks do not pass an entire rule. Topology exceptions reopen when topology changes.

Fresh KiCad 10.0.6 native DRC: zero configured violations on all four; Main/Power/Control/Reverb have 105/39/99/0 unconnected items. Strict-copy runs enable all ignored checks and reveal 43/12/13/0 missing wire-pad courtyards. These 68 findings are missing assembly envelopes, not proven collisions. No active rules were relaxed. The [run manifest](../../engineering/whole-amp/pcb-measured-r/review/requirements-run.json) identifies unchanged native inputs.

Exhaustive native contract audit covers 184 circuit references, 68 wire interfaces and 16 mounting footprints. Pad/net and interface checks pass. All 46 remaining circuit references are accounted off-board. This is not native paired-board-schematic parity; current paired assembly schematics are absent. All four copper/fabrication exports were rendered and visually inspected.

Confirmed findings include incomplete routing, remote bypass/feedback placement, relay suppression on another board, missing wire-terminal envelopes and three simple bends exceeding 45 degrees. Per-net current/voltage/drop/thermal/creepage qualification is incomplete. Explicit HV clearance rules exist; they do not constitute complete insulation qualification. Zero copper zones alone is not a defect. Fifty-two on-board references still lack selected MPNs. Exact mechanical envelopes, rear-cover independence, complete drill/driver access and assembled cabinet fit are not verified.

## ICM ownership and next work
Read-only native extraction, strict-run orchestration and rule-matrix generation are separate factories. Editable engineering assessment is separate from generated evidence. Existing source/circuit, component selection and mechanical modules retain ownership; the audit does not duplicate or silently change their contracts. Older routed-board status was marked historical and active edit routes corrected.

Next: resolve exact parts and common populated assembly; repair placement and protection; derive current/insulation and return-path rules; complete routing and remaining bends; rerun contract/native/visual/CAM and assembly checks. Expression pedal, amplifier ringing, supervisor corners and tank drive qualification remain open. Human check: inspect each finding in native CAD and full source rule, then inspect physical assembly/service paths and perform the staged prototype tests before any qualification claim.

## Record verification
Scoped ICM checks are clean for PCB integration, brain and the active prototype plan. Script syntax parses; all manifest native hashes and original imperative-file hashes match disk; 364 matrix IDs are unique; feedback IDs are unique and all canonical paths resolve. `git diff --check` passes. Manual seam review confirms the new factories separate native extraction, external CLI checking and requirement indexing, with human engineering dispositions kept editable. These checks validate audit records and module boundaries; the engineering failures above remain open.
