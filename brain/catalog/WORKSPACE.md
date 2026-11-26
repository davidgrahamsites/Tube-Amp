# Renegade project map

Generated as of 2026-11-26. Edit brain/materials/register.json and brain/feedback/events.json, then rebuild.

## Start here

- Current state: [PROJECT_STATUS.md](<../../PROJECT_STATUS.md>)
- Current circuit: [engineering/whole-amp/reverb-600/review/review.md](<../../engineering/whole-amp/reverb-600/review/review.md>)
- Selected parts: [engineering/component-selection/selected-engineering-bom.csv](<../../engineering/component-selection/selected-engineering-bom.csv>)
- Cabinet measurements: [engineering/whole-amp/mechanical/review/measurement-guide-2026-11-21.md](<../../engineering/whole-amp/mechanical/review/measurement-guide-2026-11-21.md>)
- Feedback workflow: [brain/rules/feedback.md](<../../brain/rules/feedback.md>)
- Decisions and evidence: [brain/INDEX.md](<../../brain/INDEX.md>)

## Materials and ownership

### MAT-001 — Original source and imported starter
Role: source. Status: preserved. Owner: Source intake.

Original files remain evidence; startup/library checks are scoped.

- [Renegade Tube Amp.pptx](<../../Renegade Tube Amp.pptx>)
- [Renegade_KiCad_Library_Starter.zip](<../../Renegade_KiCad_Library_Starter.zip>)
- [Renegade_Library_Starter](<../../Renegade_Library_Starter>)
- [sources/original-ppt](<../../sources/original-ppt>)
- [sources](<../../sources>)

### MAT-002 — Current requirements and build sequence
Role: catalog. Status: current. Owner: Integration.

One functioning prototype first. Apply current explicit corrections over older narrative.

- [Renegade_Codex_Handoff.md](<../../Renegade_Codex_Handoff.md>)
- [PROJECT_STATUS.md](<../../PROJECT_STATUS.md>)
- [plans/renegade-working-prototype](<../../plans/renegade-working-prototype>)
- [Design Imperatives/review](<../../Design Imperatives/review>)
- [plans](<../../plans>)
- [Design Imperatives](<../../Design Imperatives>)

### MAT-003 — Current received-tank schematic
Role: product. Status: engineering draft. Owner: Reverb600 owner.

600R-1 current schematic and measured-DC-resistance simulations; pcb-measured-r contains a separate incomplete four-board integration draft.

- [engineering/whole-amp/reverb-600](<../../engineering/whole-amp/reverb-600>)

### MAT-004 — Exact selected components and purchase candidates
Role: product. Status: partial selection. Owner: Component selection.

Coverage is canonical by reference; selected BOM is generated. Candidate/selected/ordered/received are distinct.

- [engineering/component-selection/coverage.json](<../../engineering/component-selection/coverage.json>)
- [engineering/component-selection/candidate-register.json](<../../engineering/component-selection/candidate-register.json>)
- [engineering/component-selection/selected-engineering-bom.csv](<../../engineering/component-selection/selected-engineering-bom.csv>)
- [engineering/component-selection/selected-engineering-summary.json](<../../engineering/component-selection/selected-engineering-summary.json>)
- [engineering/component-selection/footprints](<../../engineering/component-selection/footprints>)
- [engineering/component-selection](<../../engineering/component-selection>)

### MAT-005 — Received cabinet and spring tank
Role: evidence. Status: received; fit unqualified. Owner: Mechanical owner.

Yellow cabinet and tank received. Tank envelope user-reported 149.5×60×36.5 mm; speaker aperture approximately 270 mm. Mounting photos and conditional rear-slot tube-visibility requirement recorded. Control-opening geometry, installed clearances, assembled fit and coil AC/current qualification remain open.

- [engineering/whole-amp/mechanical/fit-register.json](<../../engineering/whole-amp/mechanical/fit-register.json>)
- [engineering/whole-amp/mechanical/review/tank-specifications.md](<../../engineering/whole-amp/mechanical/review/tank-specifications.md>)
- [engineering/whole-amp/mechanical/review/measurement-guide.md](<../../engineering/whole-amp/mechanical/review/measurement-guide.md>)
- [engineering/whole-amp/mechanical/review/received-vs-drawing.md](<../../engineering/whole-amp/mechanical/review/received-vs-drawing.md>)
- [engineering/whole-amp/mechanical/review/received-tank-photo-intake-2026-11-20.md](<../../engineering/whole-amp/mechanical/review/received-tank-photo-intake-2026-11-20.md>)
- [engineering/whole-amp/mechanical/evidence/received-tank-2026-11-20](<../../engineering/whole-amp/mechanical/evidence/received-tank-2026-11-20>)
- [engineering/whole-amp/mechanical/review/measurement-guide-2026-11-21.md](<../../engineering/whole-amp/mechanical/review/measurement-guide-2026-11-21.md>)
- [engineering/whole-amp/mechanical/evidence/received-cabinet-2026-11-21](<../../engineering/whole-amp/mechanical/evidence/received-cabinet-2026-11-21>)
- [engineering/whole-amp/mechanical/review/received-cabinet-photo-intake-2026-11-21.md](<../../engineering/whole-amp/mechanical/review/received-cabinet-photo-intake-2026-11-21.md>)

### MAT-006 — Speaker, tubes, sockets, magnetics and mounting hardware
Role: product. Status: selection/fit incomplete. Owner: Integration + mechanical.

Original part identity is not a current exact-build selection. Full populated fit remains unresolved.

- [engineering/component-selection/task-card.md](<../../engineering/component-selection/task-card.md>)
- [engineering/component-selection/harness-hardware-candidates.json](<../../engineering/component-selection/harness-hardware-candidates.json>)
- [engineering/whole-amp/mechanical/review/repack-work-order.md](<../../engineering/whole-amp/mechanical/review/repack-work-order.md>)
- [sources/original-ppt/bom-as-printed.csv](<../../sources/original-ppt/bom-as-printed.csv>)

### MAT-007 — Knobs, pots and expression controls
Role: product. Status: partial selection; expression circuit pending. Owner: Controls.

Accepted styling differs from final shaft fit; pedal feature remains required but unimplemented.

- [brain/records/CMP-013-pointer-knobs.md](<../../brain/records/CMP-013-pointer-knobs.md>)
- [engineering/whole-amp/expression-control/requirements.md](<../../engineering/whole-amp/expression-control/requirements.md>)

### MAT-008 — Whole-amp historical boards and integrated draft
Role: product. Status: historical v0.5; preserve native edits. Owner: Whole-amp owner.

Earlier DRC/ERC results do not establish600R-1 board parity or cabinet fit.

- [engineering/whole-amp/pcb](<../../engineering/whole-amp/pcb>)
- [engineering/whole-amp/integrated](<../../engineering/whole-amp/integrated>)
- [engineering/whole-amp/board-plan.json](<../../engineering/whole-amp/board-plan.json>)
- [engineering/whole-amp/NATIVE_EDIT_GUARD](<../../engineering/whole-amp/NATIVE_EDIT_GUARD>)

### MAT-009 — Whole-amp simulation evidence
Role: evidence. Status: scoped results and unresolved numerical issues. Owner: Simulation owner.

Real-transformer HF behavior not qualified; ideal-transformer reference is not hardware proof.

- [engineering/whole-amp/simulation](<../../engineering/whole-amp/simulation>)
- [engineering/whole-amp/tools](<../../engineering/whole-amp/tools>)
- [simulation](<../../simulation>)

### MAT-010 — Earlier schematic/reverb revisions
Role: product. Status: historical preserved snapshots. Owner: Electrical owner.

Tube reverb is superseded. Historical scripts and outputs retain original paths; do not rerun guarded generators over native edits.

- [engineering/updated-schematic](<../../engineering/updated-schematic>)
- [engineering/solid-state-reverb](<../../engineering/solid-state-reverb>)

### MAT-011 — Supplier/source correspondence and evidence
Role: evidence. Status: dated observations. Owner: Sourcing owner.

Preserve quote/login/message dates. Sent inquiries, drafts and received messages have different status.

- [engineering/cabinet-search](<../../engineering/cabinet-search>)
- [engineering/component-selection/evidence](<../../engineering/component-selection/evidence>)
- [engineering/whole-amp/evidence](<../../engineering/whole-amp/evidence>)
- [engineering/whole-amp/mechanical/evidence](<../../engineering/whole-amp/mechanical/evidence>)

### MAT-012 — Decisions, rules and feedback
Role: catalog. Status: current with retained history. Owner: Active Renegade agent.

Ledger links to authoritative records; it does not replace them.

- [brain/records](<../../brain/records>)
- [brain/rules](<../../brain/rules>)
- [brain/feedback/events.json](<../../brain/feedback/events.json>)
- [brain/sources.md](<../../brain/sources.md>)
- [CHATGPT_CONVERSATION.md](<../../CHATGPT_CONVERSATION.md>)
- [brain](<../../brain>)

### MAT-013 — Later production/sales plan
Role: product. Status: deferred reference. Owner: Planning owner.

Five-unit production is not the first working-prototype milestone.

- [plans/renegade-five-unit-build](<../../plans/renegade-five-unit-build>)

### MAT-014 — Supporting tube matcher
Role: product. Status: separate proposed instrument. Owner: Tube matcher owner.

EL34/12AX7 instrument proposal; not part of the amp fabrication package.

- [engineering/tube-matcher](<../../engineering/tube-matcher>)
- [brain/records/DEC-006-tube-matcher.md](<../../brain/records/DEC-006-tube-matcher.md>)

### MAT-015 — Project ICM factories and catalogs
Role: factory. Status: active. Owner: Memory owner.

Stable scripts/templates are separated from editable registers and generated catalogs.

- [brain/tools](<../../brain/tools>)
- [brain/_templates](<../../brain/_templates>)
- [brain/materials/register.json](<../../brain/materials/register.json>)
- [brain/catalog/CONTEXT.md](<../../brain/catalog/CONTEXT.md>)

### MAT-016 — Whole-amp integration and mechanical interfaces
Role: product. Status: engineering work in progress. Owner: Whole-amp integration.

Parent owner for integration files; more-specific routes own circuit revisions, simulations, boards, received hardware and evidence.

- [engineering/whole-amp](<../../engineering/whole-amp>)

### MAT-017 — Current selected-part PCB reconciliation
Role: product. Status: engineering draft; no fabrication release. Owner: PCB integration.

Four boards preserve historical originals. Reverb routed with zero DRC violations/unconnected items; Main, Power and Control need routing. Cabinet fit and expression control remain open.

- [engineering/whole-amp/pcb-measured-r](<../../engineering/whole-amp/pcb-measured-r>)

### MAT-018 — Electric first-stage headroom screen
Role: product. Status: scoped simulated evidence; hardware qualification pending. Owner: Electric integration.

118 completed isolated preamp cases; generic tube/source model, not full-amp or real-pickup validation. Failed and short-settling attempts retained.

- [engineering/whole-amp/electric-input-headroom](<../../engineering/whole-amp/electric-input-headroom>)

### MAT-020 — Luna amplifier design journal
Role: product. Status: initial source-linked narrative; historical backfill and physical build pending. Owner: Luna journal worker; integration technical review.

DEC-021/FB-142: retain problems, options, decisions and verification for a future design guide/post series. Derived narrative; canonical engineering records remain authoritative. Current entries VAL-070–076; no physical-build claim.

- [docs/design-journal](<../../docs/design-journal>)
- [docs/CONTEXT.md](<../../docs/CONTEXT.md>)

### MAT-021 — Capacitor and bottom-power packaging reviews
Role: product. Status: research and conditional plans; no native adoption or populated fit approval. Owner: Electrical/mechanical integration.

FB-144–147: exact capacitor body/lead evidence, independent five-pass reviews, source-backed Alien Method candidates and combined synthesis. Preserve power-block ownership and distinguish verified local arithmetic from whole-amplifier fit. FB-148–151: source-linked mathematical history, offline HTML/KaTeX reports, vocabulary keys and explicit build holds.

- [plans/capacitor-bank-fit](<../../plans/capacitor-bank-fit>)
- [plans/bottom-power-enclosure](<../../plans/bottom-power-enclosure>)
- [plans/power-packaging-alien](<../../plans/power-packaging-alien>)
- [plans/power-packaging-synthesis](<../../plans/power-packaging-synthesis>)
- [engineering/component-selection/power-film](<../../engineering/component-selection/power-film>)
- [docs/engineering-reader](<../../docs/engineering-reader>)

## Complete file inventory

5336 files cataloged with path, role, owner and SHA256 in [FILES.json](FILES.json). No existence/hash check establishes circuit safety or fit.

Historical native snapshots keep their existing paths and original internal layout. Their legacy scripts are not new-work templates. New active work separates tools/templates, editable registers and generated products.

Known missing evidence remains explicit in the mechanical register and engineering review. This backfill does not fabricate unavailable conversations, measurements, supplier answers or orders.
