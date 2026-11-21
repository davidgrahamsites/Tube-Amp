---
id: VAL-015
type: validation
domain: cross-domain
status: verified
updated: 2026-11-21
---
# Electric headroom and exact-part checkpoint

## Claim and revision
The isolated original preamp fixture completed 118 cases with stable first-stage results under the recorded assumptions. Seventeen additional component positions now have engineering selections; eleven packages were integrated into the current native draft. These are scoped checks, not a completed amplifier or fabrication release.

## Method
Ngspice fixture derives clean and dirty preamps from current600R-1 circuit contract, uses the unchanged generic Duncan12AX7 model, sweeps three ideal supplies/two frequencies/nine amplitudes, and compares eight finer-step/longer-settling runs. Two clean-volume cases distinguish first-stage clipping from downstream level. Corrected a missing dirty tone sheet and extended settling; failed/short attempts are retained and labeled. KiCad10.0.6 loaded updated packages and checked pad/net contract and DRC. Separate144-case bias resistor screen retained full decks/logs/hashes.

## Actual result
At nominal278V first-stage supply and1kHz, clean first-plateTHD is3.911% at1Vsource peak and15.358% at2V. Source includes assumed20k resistance and470pF cable; jack peaks are0.9788V and1.9515V. Fine-step comparison maximum first-stage gain change0.01536%, THD change0.01092 percentage points. Retain DEC-010: no added buffer. No claim that all humbuckers stay clean at full output.

Selected engineering BOM:44MPNs/134references/60groups of128groups/230refs. Two selectedMPNs lack domestic RMB prices; priced-subset estimate359.32RMB excludes them and other unselected items. Stock observations are dated, not a new quote.

Native pad maps:444 checked, no mismatches, historical sources preserved. Current DRC: Main0violations/105unconnected; Power0/39; Control0/99; Reverb0/0. Six newest selections (R303,R313,R503,R39,C321,C602) still require native package integration; C602 needs10mm rather than provisional5mm pitch and may invalidate local routing. No routing-completion claim.

R39's scoped144-case maximum instantaneous power0.30361W is below its100°C derated0.64706W continuous allowance. R40 reaches7.4193W startup peak and remains held for pulse qualification. Supervisor release/gate-drive corners and exact alternatives are documented; no semiconductor substitutions were silently applied.

## Evidence
- [Headroom report](../../engineering/whole-amp/electric-input-headroom/results/review.md), [structured numerical checks](../../engineering/whole-amp/electric-input-headroom/results/numerical-review.json), [runtime](../../engineering/whole-amp/electric-input-headroom/results/runtime-version.txt)
- [First component wave](../../engineering/component-selection/evidence/electric-parts-2026-11-21.md)
- [Resistor review](../../engineering/component-selection/evidence/electric-bias-resistors-2026-11-21.md), [reproducible bias screen](../../engineering/component-selection/evidence/bias-resistor-screen/CONTEXT.md)
- [Low-voltage controller/capacitor review](../../engineering/component-selection/evidence/electric-lv-parts-2026-11-21.md)
- [PCB check](../../engineering/whole-amp/pcb-measured-r/review/final-checks.json), [package changes](../../engineering/whole-amp/pcb-measured-r/review/electric-package-integration.json)

## Scope and follow-up
Generic preamp model does not qualify selected tube spread, real pickup waveform, power stage/OT, thermal behavior or noise. Existing full-amp HF ringing remains open. All four original board outlines cannot occupy one467×160mm plane; finish physical assembly allocation before routing new outlines. Exact magnetics/speaker/sockets, received tank envelope, control-panel interfaces, expression control, semiconductor corners and procurement remain open. See DEC-011 for panel proposal.
