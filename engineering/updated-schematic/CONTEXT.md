# Updated Renegade schematic

One job: retain the editable source baseline and 220 V /50 Hz tube-reverb schematic, with revision-specific review evidence.

## Inputs
[Canonical handoff](../../Renegade_Codex_Handoff.md), [source drawings](../../sources/original-ppt/inspection.md), [active prototype plan](../../plans/renegade-working-prototype/plan.md), [simulation contract](../../simulation/requirements.md), and the user's explicit October 4 request to create the updated schematic.

## Process
Read [README.md](README.md). Edit the native KiCad project for circuit changes; keep the design register aligned. The [tools contract](tools/CONTEXT.md) describes the initial generator and checks. Preserve the imported source and original library starter. Distinguish reference component exploration from selected-build-component validation.

## Outputs
Public design seam: [Renegade_220V_Reverb.kicad_sch](Renegade_220V_Reverb.kicad_sch), with its same-name project and linked sheets. [Baseline](baseline/CONTEXT.md) retains the source capture. [Libraries](libraries/CONTEXT.md) are project-local. [Validation](validation/CONTEXT.md) holds native exports and actual checks; [simulation](simulation/CONTEXT.md) holds limited reference runs. [Review notes](review-notes.md) record decisions and remaining evidence. [Wired redraw task](wire-layout-task.md) records the current presentation scope and [layout data](wire-layout.json) retains the manual placements.

## Human check
Review exact transformer/relay/tank parts, electrode stresses, protection, complete S01-S06 simulation and cabinet fit before prototype fabrication or energization. Revision 0.3 is a wired presentation of the same engineering draft, not a build release.
