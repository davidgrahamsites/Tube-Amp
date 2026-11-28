# Tool routing

This reference provides candidate routes; verify current official documentation and installed capabilities for the selected platform before use.

## Version-specific findings (October 3, 2026)
KiCad 10 CLI performs exports and ERC/DRC; it is not a general schematic editor. Its IPC API is PCB-only and requires a running GUI in versions 9/10; headless IPC starts in 11. Controlled native-file generation therefore requires native parsing, rendering, net/connectivity checks and review. See the [official CLI manual](https://docs.kicad.org/10.0/en/cli/cli.html) and [IPC limitations](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/).

FreeCAD Python/console workflows can automate geometry, but GUI-dependent drawing APIs and headless PDF exports require an installed-version trial. Inkscape CLI can export SVG-based artwork, but printer color and text/scale proofs remain separate checks. OpenSCAD's documented export formats do not include STEP; use a suitable FreeCAD solid model when a manufacturer needs STEP. See [FreeCAD headless documentation](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Headless_FreeCAD.md), [Inkscape CLI](https://wiki.inkscape.org/wiki/Using_the_Command_Line), and [OpenSCAD CLI](https://files.openscad.org/documentation/manual/Using_OpenSCAD_in_a_command_line_environment.html).

For drilled boards, retain an internal hole schedule and reviewed PTH/NPTH outputs, then create exactly the selected manufacturer's agreed drill package. Separate versus merged files and oval-slot encoding are vendor-specific; don't send competing drill sets. Inspect export origins, finished diameters, slots/plating and CAM alignment. See [KiCad PCB documentation](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) and the [JLCPCB export guide](https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9).

| Deliverable | Candidate software | Automation target | Human or evidence-dependent check |
|---|---|---|---|
| Schematic, PCB, BOM, fabrication | KiCad | Supported CLI, BOM/export scripts, supported version-specific PCB API | Native load, source fidelity, constraints, pin mapping, rendered review |
| Operating-point/signal exploration | ngspice through KiCad or standalone | Revisioned netlists and model sources | Tube/transformer model suitability and correlation with measurements |
| Chassis, cabinet, baffle, panel holes | FreeCAD | Parametric models, supported Python interfaces, STEP/DXF exports | Supplier dimensions, interference, heat/service access, manufacturability |
| Simple geometric alternatives | OpenSCAD when appropriate | Text-based parameter-driven geometry | DXF/solid export suitability and mechanical review |
| Panel labels and cabinet print art | Inkscape | Editable SVG, documented CLI exports | Scale proof, readable labels, printer bleed/color/material requirements |
| Manifests, calculations, data checking | Python / spreadsheets where useful | Deterministic data transforms and checks | Inputs, units, assumptions and results |

## Available specialized skills
Use the session's current skill catalog rather than assuming tools or skills are installed:
- Presentation/PDF skills when source drawings are embedded in those formats.
- Spreadsheet skills when the primary artifact is a costed BOM/workbook.
- Image generation for visual concept art; rebuild fabrication labels/geometry as vectors.
- Computer-use tools for CAD steps unsupported by a suitable native API/CLI.
- Verification and structural audit skills for evidence and knowledge-base integrity where applicable.

## Interface record
Record millimetre units; coordinate origin and viewing side; board outline; mounting and control centres; drill/cut diameters and tolerances; fastener stack; supplier part drawing revision; clearances and mounting envelope; print/cut layer meanings; and the electrical/mechanical revision that owns these values. Generate downstream artifacts from this record where feasible, then inspect them.

## Research handoff
Ask for exact official sources supporting version/API availability, tool licensing and export formats. Request delivered-cost quotes only against a defined specification, quantity, destination and date. Keep historical prices, planning allowances and actual quotes distinctly labeled.
