# Solver qualification results

One job: retain reproducible evidence that the local shared ngspice runtime solves simple analytic checks.

## Inputs
`../tools/qualify_ngspice.py`, installed KiCad native Python and bundled ngspice library.

## Process
The tool writes the tested netlists, engine output and measured metrics here. Treat failures as failures; separate this software evidence from later selected-component amplifier simulations.

## Outputs
`dc-divider.cir`, `rc-step.cir`, `ngspice.log` and `result.json` with runtime/version, checks and input hashes.

## Human check
Review the actual result JSON and log; no result here approves amplifier parts, performance or construction.
