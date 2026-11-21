---
id: VAL-010
type: validation
domain: schematic
status: verified
updated: 2026-10-04
---
# Schematic v0.3 - continuous-wire redraw

## Claim and revision
Presentation-only redraw of the 15-sheet revised Renegade project, preserving the v0.2 component references, full native values, physical pin partitions and intentional no-connects. All fourteen circuit sheets use continuous orthogonal wires with conventional functional placement. Labels are retained at sheet interfaces; grounds use native power symbols. This is a scoped drawing/connectivity claim, not an amplifier qualification.

## Method
KiCad 10.0.6 native XML export, full ERC with no exclusions and PDF export with wire-crossing hops. Independent native-to-native comparison to the archived v0.2 netlist, plus existing explicit-register pin checks. Manual placements are retained in `wire-layout.json`; original native instances, pin numbers, UUIDs and hidden selection/rating/source fields are preserved. Compact Display fields coexist with unchanged full Value fields. Rendered pages reviewed, with detailed critical audio/power/control sheets.

## Actual result
204 physical references, 137 nets, 536 mapped connected pins and 11 intentional no-connects. Native component reference/value and pin-partition comparisons pass. Full revised ERC: zero errors, one retained GND/PE alias warning; no exclusions. 71 sheet-interface labels replace the previous per-pin global labels. Native parsing/export succeeds.

The first redraw failed parsing because the serializer quoted a library pin-type keyword and omitted page-string quotes. The next native comparison caught rotated-symbol coordinate mismatch and unnecessary wire tails. These were corrected before delivery. Rendered review also moved output-valve, unused-relay and reverb-capacitor fields to remove collisions. Prior label layout and validation are preserved in a ZIP checkpoint.

## Evidence
- [Editable schematic module](../../engineering/updated-schematic/README.md)
- [Task and acceptance scope](../../engineering/updated-schematic/wire-layout-task.md)
- [Exact native equivalence](../../engineering/updated-schematic/validation/layout-equivalence.json)
- [Register connectivity check](../../engineering/updated-schematic/validation/connectivity-check.json)
- [ERC](../../engineering/updated-schematic/validation/revised-erc.json)
- [Wire/layout counts](../../engineering/updated-schematic/validation/wire-layout-report.json)
- [Current CLI run](../../engineering/updated-schematic/validation/wired-native-cli-run.json)
- [Revision hashes and summary](../../engineering/updated-schematic/validation/validation-summary.json)
- [Earlier layout checkpoint](../../engineering/updated-schematic/validation/label-layout-v0.2.zip)

## Scope and follow-up
The source baseline remains unchanged. Existing bias/RC reference exploration is inherited because the circuit pin partitions and component values are unchanged; no additional amplifier-performance simulation is claimed. Exact build magnetics/tank/parts, independent engineering review, full selected-component simulations, protection, transient/thermal/pop behavior and cabinet fit remain pending as in VAL-009. Native files remain the circuit edit surface; re-layout refuses to overwrite subsequent native edits.
