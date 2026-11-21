# Circuit simulation evidence

One job: establish reproducible simulation evidence for the selected-component 220 V / 50 Hz prototype revision.

## Inputs
[Canonical requirements](../Renegade_Codex_Handoff.md), [source inspection](../sources/original-ppt/inspection.md), reconciled baseline netlists when captured, chosen-component datasheets/model provenance and revisioned engineering limits.

## Process
Use [requirements.md](requirements.md) as the public simulation contract. Qualify the available solver, then qualify device models, simulate individual blocks and integrate them. Keep software qualification separate from amplifier results. Create model/netlist/run folders with their own contracts as those artifacts are produced; do not populate them with unverified circuit placeholders.

## Outputs
Model provenance and pin mapping, exact netlists/inputs/hashes, solver version, logs, waveforms, measured metrics, review of limits and exceptions. Current intake has no selected-component amplifier simulation.

## Human check
Review operating conditions and model adequacy against actual selected parts; require physical measurements for safety, magnetic/mechanical/acoustic behavior and other effects the models cannot establish.
