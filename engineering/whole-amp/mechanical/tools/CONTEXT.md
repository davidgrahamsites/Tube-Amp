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
