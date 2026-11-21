# Renegade Tube Amp

KiCad engineering project for an original six-tube amplifier with solid-state spring reverb.

Two separate builds are tracked in Git:

| Branch | Build |
|---|---|
| `electric-guitar-amp` | Original electric-guitar amplifier and spring reverb |
| `acoustic-guitar-amp` | Acoustic-specific input buffer and speaker/crossover development |

Read [BUILD_VARIANT.md](BUILD_VARIANT.md) to identify the checked-out build. Read [PROJECT_STATUS.md](PROJECT_STATUS.md) for actual completed checks and unresolved work. Neither branch is a construction release.

## Project map

- [Workspace contract](CONTEXT.md)
- [Current material catalog](brain/catalog/WORKSPACE.md)
- [Requirements and handoff](Renegade_Codex_Handoff.md)
- [Selected component BOM](engineering/component-selection/selected-engineering-bom.csv)
- [Current 600R-1 schematic](engineering/whole-amp/reverb-600/cad/Renegade_220V_Reverb.kicad_sch)
- [Four-board engineering draft](engineering/whole-amp/pcb-measured-r/CONTEXT.md)
- [Measured-resistance simulation and PCB review](engineering/whole-amp/reverb-600/review/measured-resistance-results-2026-11-20.md)
- [Received-cabinet fit evidence](engineering/whole-amp/mechanical/CONTEXT.md)

Historical designs and failed/limited simulations are retained as evidence. Native KiCad factories marked with overwrite guards must not be rerun over later manual edits. Supplier PDFs, source artwork and third-party models retain their original ownership and licensing.
