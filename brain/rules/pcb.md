---
id: RULE-PCB
type: rule-set
domain: pcb
status: documented
updated: 2026-10-04
---
# PCB design

Scope: reusable workflow guidance, not evidence of verified circuitry.

## PCB-001
Resolve mounting strategy, off-board connections, package choices and circuit partitioning before layout; keep unresolved hardware assumptions visible.

## PCB-002
Address protective earth, mains, high voltage, heaters, audio and low-voltage controls as physical design concerns. Derive numeric spacing, trace and thermal requirements from the actual design and applicable evidence; no generic safe values are supplied here.

## PCB-003
Review grounding, current paths, mechanical fit and service access against the circuit and enclosure. Retain calculations and review evidence.

## PCB-004
Reconcile PCB connectivity with the reviewed schematic revision; retain DRC results and inspect manufacturing outputs. CAD checks do not establish electrical safety.

## PCB-005
Scope imported guidance to the actual circuit block and topology. Continuous references, deliberate stage/star/bus returns and isolation barriers must be reconciled in one whole-assembly current-path review, including off-board wiring. Record derived numerical limits and evidence separately from reading qualitative rules; generic device examples do not select parts or authorize cross-barrier ground stitching. See the [design-imperative applicability review](<../../Design Imperatives/review/REVIEW.md>) for this project's imported references.

## Basis and exceptions
Seeded from [the handoff and discussion](../sources.md) and this requested engineering workflow. Record supporting evidence and exceptions as work proceeds. Project-specific values and results belong in [records](../records/CONTEXT.md).
