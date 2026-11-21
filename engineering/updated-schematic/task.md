---
id: TASK-P04-SCHEMATIC-DRAFT
type: task
domain: schematic
status: documented
updated: 2026-10-04
---
# Updated schematic v0.2

## Owner and dependencies
Root agent owns capture, integration and documentation. Inputs are available source images, canonical requirements and previous control/reverb proposals. Packaging measurements and actual supplier choices remain dependencies of release, not of this draft.

## Inputs
Current source archive SHA-256 `00c43b64bb87dee26b7982b797921cbb307a56d60e0324fe06e7f86d9d6eecc9`; its image bytes match the preserved intake. KiCad 10.0.6 official symbols; original starter unchanged. Explicit user clarification: create the updated schematic.

## Outputs
Editable source baseline, revised hierarchical schematic/project, portable local symbol library, native netlists/ERC/PDF, draft BOM/register, scoped ngspice runs and engineering review notes. README is the public entry point; native schematic is the editable design seam.

## Method and automation
Circuit Design Skill Ladder L0/L1/L3, controlled native-file generation, installed CLI parsing/export/ERC, independent native-export-to-register pin comparison, PDF rendering and direct visual review. Limited L2 bias/RC explorations use KiCad Python 3.9 and shared ngspice 45.2. No subagents dispatched. Verification Before Completion and ICM Check apply to evidence and module structure.

## Done-condition and evidence
This task completes a reviewable native schematic draft with implemented reverb/control/mains-refactor topology and explicit limitations. See validation summary and VAL-009. It does not complete P04's build-selected component modeling, full S01-S06 simulation, physical fit or fabrication release.

## Effort and stopping conditions
One sustained capture/review session, approximately one hour, with source/rating/model uncertainty explicit. Stop before fabrication/energization; actual components, model qualification and qualified electrical/physical review are still required under the existing handoff.


## Presentation follow-up
The [v0.3 wire-layout task](wire-layout-task.md) redraws this same circuit with continuous wires and verifies exact native component-value /pin-partition equivalence. See VAL-010 for the current view; this original circuit-capture task retains its historical v0.2 scope.
