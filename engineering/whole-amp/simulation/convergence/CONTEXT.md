# convergence contract

Owner: Renegade integration agent. One job: retain scoped convergence electrical simulation fixtures and results.

## Inputs
Paths in this contract are project-root-relative unless named as local. Read `simulation/requirements.md`, the owning module circuit and the saved local decks/results. Local edit/evidence surfaces include `iterations-0.02.cir`, `iterations-0.02.json`, `iterations-0.02.log`, `iterations-0.2.cir`, `iterations-0.2.json`.

## Process
Run evidence, not full hardware qualification. Read model assumptions, logs and convergence limits before using a result. Keep source inputs, stable scripts and run products identifiable by their registered roles. This contract adds navigation in place; it does not rerun, relocate or approve the existing design. New active runs belong in a revision module with separate tools, evidence and products.

## Outputs
The local files listed above and their children remain the module outputs. `brain/catalog/FILES.json` indexes their roles and hashes; `brain/materials/register.json` identifies the owning material route.

## Human check
Open the local output with its source/reference and confirm revision, unresolved limits and actual part or circuit identity before using it for the build. For native CAD, inspect the render and pin/geometry checks; for runs, inspect assumptions and logs.
