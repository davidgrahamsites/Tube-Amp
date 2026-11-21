---
id: VAL-014
type: validation
domain: cross-domain
status: verified
updated: 2026-11-20
---
# Measured tank resistance and PCB integration checks

## Claim and revision
The 600R-1 interface simulation incorporates the user-reported coil DC resistance. Four separate native PCB drafts preserve the historical originals and reconcile selected footprints/current pad nets. Verification is limited to the checks below; the amplifier is not build-ready.

## Method
Follow the [task card](../../engineering/whole-amp/reverb-600/review/task-2026-11-20.md). Run the existing ngspice/TI-model fixture with resistance read from the received-hardware register. Use native KiCad 10.0.6 pad loading, CLI DRC and SVG inspection. Retain source/output hashes and historical assumed-resistance results.

## Actual result
All eight scoped simulation criteria pass. The reverb PCB has zero DRC violations and zero unconnected items; three other boards still have routing gaps. A 444-pad contract check reports no mismatches. Thirteen more fitted positions now have exact selected parts and documented film-capacitor footprints.

## Evidence
- [Review and limits](../../engineering/whole-amp/reverb-600/review/measured-resistance-results-2026-11-20.md)
- [Simulation output](../../engineering/whole-amp/reverb-600/simulation/results.json)
- [Native board audit and hashes](../../engineering/whole-amp/pcb-measured-r/review/final-checks.json)
- [Selected film capacitor evidence](../../engineering/component-selection/evidence/lv-film-selection-2026-11-20.md)

## Scope and follow-up
Impedance frequency/level, inductance and safe tank-current rating remain unverified. Simulation is not acoustic/thermal validation. Close remaining component selection, expression control, integrated routing, actual populated cabinet fit and bench qualification before release.
