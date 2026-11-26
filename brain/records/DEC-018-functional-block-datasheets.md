---
id: DEC-018
type: decision
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Reusable circuit blocks with their own datasheets

User request, FB-128: save the completed amplifier as orthogonal functional
blocks with operating, current and loading characteristics, explicit interface
requirements, and characteristics of compatible companion blocks, so later
amplifiers can reuse this work.

Each block must have one clear job and a small explicit interface. A functional
block is not automatically a separate PCB. Shared supplies, grounds, feedback,
control, heat and mechanical dependencies must be documented rather than
hidden behind a claim of complete independence.

[The datasheet contract](../../engineering/functional-blocks/CONTEXT.md) and
[common template](../../engineering/functional-blocks/datasheet-template.md)
define the deliverable. Include minimum/typical/maximum values, conditions,
units, tolerances, current/thermal budgets, source/load impedance, signal and
DC levels, clipping/recovery, bandwidth/treble, stability, power sequencing,
fault behavior, grounds/shielding, pinout/connectors and physical envelopes.
State both acceptable limits and preferred companion-block characteristics.

Every characteristic identifies its evidence and revision, separating targets,
manufacturer limits, calculations, simulations, measurements and unknowns.
Deliver a compatibility matrix for every connected block pair. A newly paired
or modified block reopens affected loading, stability, protection, power and
fit checks. Final sheets reference editable source, exact China-sourced BOM,
implementation/footprint constraints and validation, not copied unsourced
values. Freeze versions so future projects can deliberately reuse or revise a
known design.

This is a required final handoff deliverable, not a declaration that the
existing amplifier or blocks are qualified. All six active engineering scopes
and physical validation requirements remain intact.

Interface adapters are reusable functional blocks too (FB-129). Each describes
the mismatch it resolves, allowed input and delivered output envelopes, power
and ground requirements, and the added noise, bandwidth, latency where relevant,
headroom and stability constraints. Check both connected interfaces. This is
a documentation/reuse requirement, not an instruction to add adapters where
the present amplifier already connects correctly.
