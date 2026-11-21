---
id: VAL-009
type: validation
domain: schematic
status: verified
updated: 2026-10-04
---
# Updated schematic v0.2 — native draft checks

## Claim and revision
The user's clarified request to create the updated schematic is implemented as an editable KiCad v0.2 engineering draft, alongside a separate native source baseline. Verification here covers native parsing/export, registered pin connectivity, scoped ERC and limited reference simulations; it does not approve the amplifier for construction.

## Method
Circuit Design Skill Ladder L0/L1/L3; controlled native-file generation from explicit pin maps and installed KiCad 10.0.6 symbols. Preserve imported files. Resolve inherited symbols into a local portable library; map valve halves by actual pin numbers, correct physical electrode ERC types and EL34 pin8's name to K. Export both roots with the installed CLI to XML netlists and PDF; run full JSON ERC without exclusions; compare each exported connected pin with the register. Render revised pages and inspect overview plus critical details, correcting label/body, note and title overlap. Run scoped bias and RC/ideal-Schmitt reference analyses using KiCad Python 3.9 / shared ngspice 45.2. Run ICM structural check.

## Actual result
- Revised hierarchy: 15 sheets including cover; 204 native component references, 137 exported nets, 536 registered connected pins and 11 explicit no-connect pins. Source baseline: 11 sheets, 119 references, 85 nets, 317 connected pins and 3 explicit no-connects.
- Both native exports and connectivity comparisons pass. No annotation warnings remain. Revised ERC: zero errors and one retained warning for the intentional GND/PE bond. Baseline ERC: zero errors and two retained net-alias warnings, for GND/PE and B_RAW/B_MAIN. No exclusions were applied.
- Revised circuit retains clean/dirty audio and 4/8/16-ohm output selection, adds a parallel 12AT7 spring driver and 12AX7 recovery/mixer, and captures an isolated 220V/50Hz control supply, debounce/toggle/reset logic and relay drivers. Main supply uses a 372HX electrical reference with a separate bias tap, revised reservoir/bleeders and heater elevation. Exact Chinese magnetics/tank and protection ratings remain unresolved.
- First reference bias attempt gave too little negative voltage; the superseded findings and lost-first-waveform limitation are retained. Corrected nominal simulated range is -33.57 to -48.14V, with twelve line/trim cases stored. This is not a measured or qualified safe EL34 operating envelope.
- The RC/ideal-Schmitt bounce case generates two rising edges for two intended presses, at approximately 0.52559s and 1.02339s. Actual TI device models, reset behavior, hot-plug, ESD and relay/audio transients are not validated by that surrogate.
- Arithmetic gives 4.8A valve heater load, or 4.95A including a proposed 0.15A pilot allowance, against the reference winding's 6A rating. Complete measured and modeled supply/load budgets still need qualification.
- ICM Check reports clean. KiCad emits an existing font-cache-version warning; native export succeeds and rendered pages were reviewed.

## Evidence
[Design entry](../../engineering/updated-schematic/README.md), [native root](../../engineering/updated-schematic/Renegade_220V_Reverb.kicad_sch), [source baseline](../../engineering/updated-schematic/baseline/Renegade_Source_Baseline.kicad_sch), [register](../../engineering/updated-schematic/design-connectivity.json), [validation summary](../../engineering/updated-schematic/validation/validation-summary.json), [simulation results](../../engineering/updated-schematic/simulation/explorations.json), [review notes](../../engineering/updated-schematic/review-notes.md) and [task card](../../engineering/updated-schematic/task.md). Exact native/source hashes are retained with the evidence.

## Scope and follow-up
Complete independent source reconciliation, chosen-build-component/model qualification and S01-S06 simulations, actual tube operating points and stresses, reverb gain/headroom/noise/drive, bias failures/sequence, fuse and HV standby ratings, relay pops, pedal connector/inhibit, tank grounding/mounting, grounding/spacing and cabinet fit. The pin comparison proves the generated drawing matches its register, not independent source fidelity. No PCB, procurement release, physical acceptance or energized measurements are completed.


## Presentation follow-up
The user subsequently requested continuous wires instead of per-pin labels. [VAL-010](VAL-010-wired-schematic-redraw.md) documents the v0.3 redraw with identical native component values and pin partitions. Current module validation paths show that presentation; the exact v0.2 schematic, netlist/ERC/PDF/summary are preserved in `engineering/updated-schematic/validation/label-layout-v0.2.zip`. The circuit qualification scope above is unchanged.
