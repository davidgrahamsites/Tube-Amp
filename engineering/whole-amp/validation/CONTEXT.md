# validation contract

Owner: Renegade integration agent. One job: retain validation native checks and visual evidence.

## Inputs
Paths in this contract are project-root-relative unless named as local. Read `Renegade_Codex_Handoff.md`, `PROJECT_STATUS.md` and the parent folder contract. Local edit/evidence surfaces include `Control-drc.json`, `Control-erc.json`, `Control-netlist.xml`, `Control-preview.png`, `Control-preview.svg`.

## Process
Generated review products; check the input revision/hash and scope. A clean report does not release hardware. Keep source inputs, stable scripts and run products identifiable by their registered roles. This contract adds navigation in place; it does not rerun, relocate or approve the existing design. New active runs belong in a revision module with separate tools, evidence and products.

## Outputs
The local files listed above and their children remain the module outputs. `brain/catalog/FILES.json` indexes their roles and hashes; `brain/materials/register.json` identifies the owning material route.

## Human check
Open the local output with its source/reference and confirm revision, unresolved limits and actual part or circuit identity before using it for the build. For native CAD, inspect the render and pin/geometry checks; for runs, inspect assumptions and logs.
