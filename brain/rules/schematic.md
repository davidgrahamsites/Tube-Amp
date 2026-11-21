---
id: RULE-SCH
type: rule-set
domain: schematic
status: documented
updated: 2026-10-04
---
# Schematic capture

Scope: reusable workflow guidance, not evidence of verified circuitry.

## SCH-001
Recreate the original source as a traceable baseline before modifying it. Link source images/sheets; mark illegible values instead of guessing.

## SCH-002
Organize sheets by circuit responsibility and explicitly name audio, power and control interfaces. Review connectivity as well as drawing appearance.

## SCH-003
Keep custom libraries project-local; verify identifiers, pin numbering and pin types against device documentation.

## SCH-004
Record native parse/export, rendered-sheet review and ERC results with tool versions. Retain justified exceptions; file validity is separate from electrical correctness.

## SCH-005
When schematic text is embedded in raster images, preserve original bytes and slide/image mappings, inspect visually and reconcile extracted/transcribed references before capture. No editable text does not mean no circuit. See [original-source intake](../records/VAL-003-original-ppt-intake.md) for this workflow's scoped evidence.

## SCH-006
Link every simulation to exact circuit/BOM/model revisions, solver version, conditions and results. Qualify part-model pin mapping and operating region, distinguish generic/reference models from selected components, and retain bounded approximations and bench-only checks. Solver qualification is not amplifier validation. Basis: [simulation requirement](../records/DEC-005-220v-selected-component-simulation.md) and [solver qualification](../records/VAL-004-ngspice-qualification.md).

## SCH-007
Draw local signal paths with continuous wires and familiar functional placement; reserve labels for sheet interfaces and shared supplies where they improve clarity. Use explicit junction dots and distinguish wire crossings. For a presentation-only redraw, compare fresh native-exported component values and pin partitions to the prior revision, alongside ERC and rendered review. Basis: the user’s wired-schematic request and [VAL-010](../records/VAL-010-wired-schematic-redraw.md).

## Basis and exceptions
Seeded from [the handoff and discussion](../sources.md) and this requested engineering workflow. Record supporting evidence and exceptions as work proceeds. Project-specific values and results belong in [records](../records/CONTEXT.md).
