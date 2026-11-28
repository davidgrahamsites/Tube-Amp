# Mechanical study factories
Owner: integration. One job: generate dimensional screens and printable studies from the fit register.
## Inputs
`../fit-register.json`; `../../reverb-600/circuit.json` supplies pot terminal nets only.
## Process
`check_fit.py` checks the original dimensional screens. `panel_study.py` generates panel envelopes and a terminal interface. `print_panel.py` exports full-size and tiled paper PDFs. These factories do not mutate native CAD or approve fabrication.
## Outputs
Generated JSON, CSV, SVG and PDF under `../review/`. Only the register is the dimensional edit surface.
## Human check
Check the 100 mm print bar with a ruler, place the paper against the actual opening and compare real knob/pot hardware before machining.

freecad_probe.py tests the installed FreeCAD Python/native/STEP route using a synthetic coupon in temporary storage. It owns no amplifier dimensions. Retain only its receipt in review/freecad-automation-check.json; read review/cad-toolchain.md for tested versus pending formats.

board_fit_cad.py owns the native/STEP current-board fit diagnostic from ../fit-register.json and ../../pcb-measured-r/review/mechanical-inventory.json. It checks drilled volumes, native reopening, STEP positions/rotation/solids and records explicit missing populations. plot_board_fit.py draws those retained poses. Native files are not fabrication chassis. Human check: compare the board-only trial and excluded service/component volumes with the real cabinet.

check_tool_access.py consumes only the partial drill measurement seam and emits conditional cross-section arithmetic; it never grants access. socket_fit_cad.py consumes the current board diagnostic and socket-fit screen, verifies native/STEP roundtrips and reports only modeled-solid collisions.

FIT-012: bench_tool_access.py reads ../tool-access-study.json, the drill fields in ../fit-register.json, optional precision-driver-candidate.json, native boards and component-owned package contracts. It writes ../review/bench-tool-access.json. bench_access_cad.py verifies that receipt, checks independent solid intersections and writes editable FCStd, STEP and a CAD receipt. No board mutation. Human check: compare each screw approach with the actual populated assembly and fitted bit.

CB-008. Run guard_sink_fit.py with Python to screen the external sink against the cabinet register. plot_guard_sink.py draws the four Boyd checks. The review folder holds the JSON and SVG. Check the Fischer flat-base alternative against the rear cover, airflow and actual removable carrier.

CB-009. rear_cover_geometry.py reads the cabinet register and drawing dimensions. rear_cover_sink.py writes rear-cover-sink.json and the flat-wall versus recessed section. Check the direct A–B reading and the whole guard with the cover on. The ImageGen measurement illustration is a guide to the endpoints.

CB-010. Run recess_template.py to generate the five-page paper fit kit from the CB-009 cover stack. recess_guide.py owns the illustrated guide. Run check_recess_template.py to measure the exported vectors. Print at actual size and record the smallest installed guard gap and cover withdrawal.
