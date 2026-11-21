# Native schematic evidence

One job: retain checks and renders for the exact schematic revision.

## Inputs
The baseline and revised native projects, `design-connectivity.json`, and installed KiCad CLI 10.0.6.

## Process
Export each root to native XML netlist, run full ERC without exclusions, compare connected pins against the register, and inspect rendered PDF pages. Preserve intended net-alias warnings rather than suppressing them. Regenerate hashes after any affected edit.

## Outputs
`baseline-netlist.xml`, `revised-netlist.xml`, corresponding ERC JSON, `connectivity-check.json`, revised PDF, page renders, contact sheet and `validation-summary.json`. The current wired v0.3 presentation is checked against the exact prior export in `layout-equivalence.json`; `wire-layout-report.json` counts wires/interfaces. `label-layout-v0.2.zip` preserves the previous layout and its native validation/PDF. Current CLI evidence is in `wired-native-cli-run.json`. Generated images are review evidence rather than panel/fabrication artwork.

## Human check
Source fidelity, ratings, physical wiring and model suitability need separate engineering review. Native parsing and ERC do not establish circuit performance or electrical safety.
