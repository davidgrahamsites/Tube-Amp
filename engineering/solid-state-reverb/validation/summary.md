# v0.4 validation summary

Checked with KiCad10.0.6 and bundled ngspice45.2 on2026-11-11.

| Check | Actual result | Scope |
|---|---|---|
| Integrated native export |18-sheet PDF and XML exported | File parse/render, not safety approval |
| Integrated pin partition |229 references,595 mapped connected pins; no missing/split/short/extra pins | Compared native netlist against explicit design register |
| Integrated ERC |0 errors,1 warning | Retained intentional GND/PE alias; not suppressed |
| PCB native pad partition |115 connected pads,29 connected nets match standalone native schematic | Includes exact physical pad numbers; no inferred pad mappings |
| PCB DRC including schematic parity |0 violations,0 unconnected,0 parity issues |Final native report; low-voltage rules only |
| TI OPAx134 AC analysis |Dry gain≈0.9801 with100k source at1kHz; control/mute variation<0.000001 gain |Actual TI model; fixture and limits in simulation/results.json |
| Wet electrical injection |1mV return injection gives≈89.6mV output at full wet/1kHz |Does not establish actual tank wet level/decay |
| Cabinet evidence |Three exact-product manufacturer size drawings downloaded and visually read |Not a stock commitment or in-cabinet fit proof |

## Corrections found during work

Initial capacitor footprint name was missing and corrected. Native wired export and pin comparison passed. The first PCB run exposed four courtyard overlaps and silkscreen interference; corrected component positions. Subsequent parity checks exposed missing metadata, unnamed-net naming differences and isolated relay-pad names; these were reconciled against native XML with connectivity unchanged. Two redundant vias coincident with plated pads were removed. Rendered review also exposed an incorrectly formed ground-zone boundary after an outline API call; replaced it with an explicit notched perimeter and refilled/rechecked it. All final PCB reports are clean.

The sandboxed macOS DRC command aborted in UI-service initialization, not on a reported design violation. Running the same native command with desktop-service access succeeded. Initial TI-model execution needed KiCad's bundled XSPICE code models loaded; the original TI model was not modified. Model logs and hash are retained.

## Still incomplete

- Exact mains/HV fuse and standby switch selection and coordination.
- Full nonlinear selected-component original-amplifier/supply/control/integrated simulations required by the project contract.
- Exact purchased transformer, tube, tank, passive and connector qualification; tank primary documentation/China stock.
- Independent source-to-pin electrical review and maximum preamp/reverb headroom/stability review.
- Chassis/support/speaker/transformer/tank fit, heat, harness routing and front-panel hole design.
- Main amplifier/controller/supply PCB layout (only reverb daughterboard routed).
- Physical bench, protective measures, commissioning, acoustic/thermal and in-cabinet tests.

No fabrication/build release or hardware-performance claim is made. `pcb/fabrication-preview/` is for engineering/CAM review after these checks, not an approved order package.
