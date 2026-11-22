---
id: VAL-019
type: validation
domain: cross-domain
status: documented
updated: 2026-11-21
---
# Researched layout comparison and bounded repairs

## Claim and limits
FB-080 requested a researched comparison with zhbi98/pcb-layout-design. FB-077 authorizes continued repairs and GitHub push. The comparison is complete; whole-amplifier engineering and fabrication release are not. Retain Main, Power, Control and Reverb ownership. This checkpoint changes three local copper corners and restores five ignored check types on three boards. It changes no circuit, selected part, footprint placement, outline or custom clearance rule. No new simulation or physical acceptance is claimed.

## Evidence and decisions
The [comparison](../../engineering/whole-amp/pcb-measured-r/review/external-guidance-comparison-2026-11-21.md) pins external commit f316a68016443b4a43d8813d4ab1062eeff29243 and links TI, ADI, KiCad and amplifier-author sources. Adopt local stage placement, bypass/feedback loops, local coil suppression, actual assembly envelopes and explicit current constraints. Adapt grounding and insulation to the high-voltage amplifier and its harness. Do not infer a four-layer requirement, mandatory ground split/pour, digital timing rules or certified trace capacity from generic advice. Retain the user's 45-degree/arc requirement; electron collisions at corners are not its physical justification.

New F02 finding: selected C353 KNSCHA MEB104J63V82CB0236 is film. TI TPS3808 §8.4.1 calls for a nearby 0.1 µF ceramic bypass. Exact U3 ordering code remains open. Resolve U3 and the bypass part together. Trial moves of C351/C352/C353 were rejected for remaining courtyard conflicts and the unaddressed part requirement; none were adopted.

The [repair manifest](../../engineering/whole-amp/pcb-measured-r/review/bounded-repair-2026-11-21.json) identifies source/adopted hashes. Main PI_K, Power B_EARLY and Control RESET_CT bends were beveled; native 4 mm detail exports were visually inspected. All five previously ignored check types were restored to warning on Main/Power/Control. Reverb is byte-identical to its pre-checkpoint board. No clearance rule was relaxed. KiCad also serialized default 0.15 mm text thickness on existing footprint text; no footprint placement or pad geometry changed.

## Fresh native verification
KiCad 10.0.6 normal and strict DRC were rerun on all four adopted boards with all severities, all track errors and zone refill. Strict copies preserve native source hashes and contain no ignored check types or stored exclusions.

| Board | Missing wire courtyards | Unconnected items | Simple-bend findings |
|---|---:|---:|---:|
| Main | 43 | 105 | 0 |
| Power | 12 | 39 | 0 |
| Control | 13 | 99 | 0 |
| Reverb | 0 | 0 | 0 |

No other DRC violation types were reported. These warnings represent unmodeled wire/solder/insulation envelopes, not proven collisions. All 444 circuit-pad mappings pass; all 184 on-board circuit references, 68 wire interfaces and 46 off-board circuit references remain accounted. No paired board-schematic parity is available. Junction/transition review remains open; a zero simple-bend count is not blanket copper or EMI approval. The 364-rule matrix remains 21 FAIL, 331 NOT_VERIFIED, 11 NOT_APPLICABLE and one SUPERSEDED because broader group requirements remain open.

The sandboxed macOS KiCad CLI crashed during application-service registration. The same read-only checks completed with approved service access outside that sandbox. This was a tool-environment failure, not a corrected board defect.

## Parts and mechanical evidence
The [reverb component dossier](../../engineering/component-selection/evidence/reverb-repair-picks-2026-11-21.md) records conditional C603/C605/R605/R616 picks and their remaining package, thermal and sourcing limits. These are not silent BOM/native substitutions. The latest rear-view cabinet image is archived; its speaker offset is qualitative evidence consistent with an offset drawing, not a measured axis position. Use the [fit register](../../engineering/whole-amp/mechanical/fit-register.json). Actual drill measurements are deferred by the user. Keep chassis loads on fixed cabinet structure and preserve independent rear-cover removal.

## ICM seams and next work
Candidate creation and read-only verification are separate tools in the PCB integration module; human visual review and guarded adoption remain explicit. Exact components are owned by component selection, electrical interfaces by the circuit module, and populated fit/tool envelopes by mechanical integration. Generated reports do not become circuit authorities. Current status and handoff point here; prior VAL-018 is the initial audit snapshot.

Next: resolve exact supervisor/bypass and coil suppression interfaces, then re-place stages and complete the return/current/insulation plan before routing. Finish expression control, major parts and populated assembly. Rerun affected simulations after electrical substitutions. Close amplifier ringing, startup stress, tank drive, physical fit and powered-test gates before release. No fabrication package or order is authorized by this checkpoint.

Human check: inspect each modified corner at native scale, review actual device layouts/current loops and wire envelopes, then review the populated cabinet and real tool approach/withdrawal paths. Exact parts and fit are still open.

## Record checks
Scoped ICM checks are clean for PCB integration, mechanical integration, component selection and brain. Both catalogs regenerated with no reported errors. New tools parse; active native hashes match the run manifest; normal/strict DRC counts agree; feedback IDs are unique and every canonical path resolves. `git diff --check` passes. Manual seam review retains separate candidate generation, read-only verification, human review and adoption; no circuit or component owner was bypassed. These checks validate the checkpoint, not fabrication readiness.
