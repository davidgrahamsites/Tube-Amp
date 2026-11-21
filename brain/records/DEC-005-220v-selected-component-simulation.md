---
id: DEC-005
type: decision
domain: cross-domain
status: documented
updated: 2026-10-04
---
# Complete mains refactor and selected-component simulation

## Question and scope
Which electrical design evidence must precede the prototype's PCB/fabrication release?

## Options and tradeoffs
The original drawings establish a legacy amplifier, not a completed 220 V / 50 Hz revision with reverb. Traceable part selection and matched simulation expose operating/stress assumptions before hardware cost is committed; missing or approximate models retain a physical measurement requirement.

## Evidence
The user stated October 4, 2026: “everything needs to be refactored for chinese 220v and simulated with the components of choice.” Requirements are canonical in the [handoff](../../Renegade_Codex_Handoff.md); detailed analysis packages and model/run evidence are in the [simulation contract](../../simulation/requirements.md).

## Decision and authority
User-directed requirement: all mains-powered supplies support Chinese 220 V / 50 Hz, and simulation uses the selected components with traceable models or justified bounded surrogates. Capture/reconcile the original baseline, complete part/load selection and qualify models, then simulate blocks and integrated behavior before electrical release. Record each model's limits; simulation is not physical electrical approval.

## Open questions and next check
Resolve output-power goal, cabinet dimensions, part evidence and source ambiguities. Select components and establish model adequacy. No complete refactor, part selection or amplifier simulation has been completed by recording this requirement.
