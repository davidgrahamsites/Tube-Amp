---
name: circuit-design-skill-ladder
description: Route electronics design tasks through specification, component evidence, simulation, KiCad capture, mechanical CAD, fabrication and measured validation using reproducible tools and scoped reviews. Use for agent-assisted circuit or PCB development and its enclosure/panel interfaces.
---

# Circuit Design Skill Ladder

Choose the least costly tool and skill combination that can produce a verifiable result for the current task. The ladder is about engineering capability and evidence; it does not prescribe model tiers or imply that software can replace physical measurements.

## Start
Read the project's AGENTS.md and workspace contract. Locate canonical requirements, current revision, unresolved decisions and relevant knowledge-base records. Preserve the user's product, budget, location, software preferences and authorization. If no structured brain exists, retain these in a small task record rather than imposing a new architecture.

Write a task card: inputs and revision, outputs, dependencies, owner, automated operations, required human evidence, done-condition and estimated effort. For delegation, assign disjoint outputs or a single editing owner and a documented integration seam. Delegation is used only when authorized.

## Capability ladder
| Level | Task | Preferred route | Required evidence before advancing |
|---|---|---|---|
| L0 | Recover source and define interfaces | File inspection, source renders, requirements/decision records | Traceable values, explicit unknowns, revisioned interfaces |
| L1 | Select parts and calculate | Manufacturer documentation, dated supplier evidence, reproducible calculations | Operating conditions, ratings, alternatives, gaps and calculations |
| L2 | Explore circuit behavior | Circuit simulator with verified models where useful | Model provenance and limitations; no claim of measured performance |
| L3 | Capture schematic and boards | Native KiCad tools, local libraries, version-supported scripting | Pin/footprint evidence, electrical constraints, native parsing, netlist/ERC/DRC, rendered review |
| L4 | Integrate enclosure and release | Parametric mechanical CAD, vector graphics, revisioned manifests | Actual geometry, interference/fit review, print proof, fabrication/drill/assembly checks |
| L5 | Validate physical hardware | Written bench procedures and human-run measurements | Unit identity, setup, limits, actual measurements, defects and retest results |

Levels are capabilities, not compulsory steps for every task. Mechanical concepts and sourcing research can run early; irreversible release depends on resolved interfaces and relevant review evidence.

## Tool and skill selection
Read [tool-routing.md](references/tool-routing.md) when choosing CAD, graphics, simulation or automation. Prefer existing official software and native APIs/CLIs; verify the installed version and its help before issuing commands. Select only skills relevant to the deliverable. Keep unsupported capabilities marked unknown.

Use parameter-driven geometry and one canonical dimensions/interface file so CAD, artwork and drill drawings share units, origin, hole sizes and revision. Keep visual concepts separate from fabrication artwork. A rendered mockup is not a dimensioned panel design.

For a generated connection list, apply the [netlist intake checks](references/review-gates.md#generated-netlist-intake) before native capture or placement.

## Required schematic and PCB review routes
For schematic capture or readability work, apply the bundled [Schematic Humanizer](references/schematic-humanizer/SKILL.md). Read its [adapter](references/schematic-humanizer/references/adapters.md), [visual checklist](references/schematic-humanizer/references/visual-audit-checklist.md), [audit record](references/schematic-humanizer/references/visual-audit-record.md), [layout annotations](references/schematic-humanizer/references/layout-handoff-annotations.md) and [prompt template](references/schematic-humanizer/references/prompt-template.md). A netlist-like drawing is not an acceptable human-readable schematic. Follow the additional [preservation and acceptance rules](references/review-gates.md); upstream's basic comparator is only one check.
For board placement, routing, component footprints, drill/slot selection or release, read [PCB engineering checks](references/pcb-engineering-checks.md). This is context-sensitive original synthesis; it does not impose generic layer counts, trace widths or high-voltage clearances.
Source provenance and license boundaries are in [integrated sources](references/integrated-sources.md). Do not apply electronics changes solely to improve a picture.

## Automation boundaries
Automate file inventory, source extraction, calculations, document generation, supported CAD operations, BOM consistency checks, exports and release manifests where the available tool actually supports them. Check native parsing and inspect output rather than trusting file-generation code.

Log tool version, command/procedure, input revision or hash, outputs, results and remaining issues. Distinguish planned, attempted and completed checks. Do not mark a part verified on a listing title or treat selection as verification. Do not hide rule-check exceptions to obtain a clean report.

For mains/high-voltage work, derive constraints from actual circuit conditions and applicable evidence. ERC, DRC and simulation are not electrical safety approval. Physical inspection, fit, print durability, solder quality and energized measurements require real evidence; delegate bench work to someone competent for the task.

Preserve user authorization. A planning/design request is not a budget for supplier orders, nor permission to contact suppliers or upload source files. Prepare a concrete quote/release package before requesting a spending or disclosure decision when needed.

## Finish
Deliver editable artifacts and a concise evidence report. Update canonical component, decision and validation records; capture reusable rules only when their scope and support are clear. Record blocked dependencies and progress independently on unaffected tasks.
