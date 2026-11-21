# Control contract

Owner: Renegade integration agent. One job: retain Control native board draft or export evidence.

## Inputs
Paths in this contract are project-root-relative unless named as local. Read `engineering/whole-amp/board-plan.json`, selected component evidence and native board files. Local edit/evidence surfaces include `Renegade_Control.dsn`, `Renegade_Control.import.ses`, `Renegade_Control.kicad_dru`, `Renegade_Control.kicad_pcb`, `Renegade_Control.kicad_prl`.

## Process
Historical/draft board products. Previous DRC results do not prove600R-1 circuit parity or delivered-cabinet fit. Preserve native edits. Keep source inputs, stable scripts and run products identifiable by their registered roles. This contract adds navigation in place; it does not rerun, relocate or approve the existing design. New active runs belong in a revision module with separate tools, evidence and products.

## Outputs
The local files listed above and their children remain the module outputs. `brain/catalog/FILES.json` indexes their roles and hashes; `brain/materials/register.json` identifies the owning material route.

## Human check
Open the local output with its source/reference and confirm revision, unresolved limits and actual part or circuit identity before using it for the build. For native CAD, inspect the render and pin/geometry checks; for runs, inspect assumptions and logs.
