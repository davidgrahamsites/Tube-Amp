# Renegade benchtop tube matcher

One job: design a standalone instrument for matching EL34 power tubes and characterizing both sections of 12AX7 preamp tubes before amplifier installation.

## Inputs
User request and EL34 correction, October 4, 2026; [canonical amp handoff](../../Renegade_Codex_Handoff.md); [original source inspection](../../sources/original-ppt/inspection.md); [sources](sources.md).

## Process
Use the Circuit Design Skill Ladder and Physical Design Agent Ladder. Keep proposed instrument profiles separate from manufacturer ratings and measured results. Preserve versioned profile/calibration identities. One editing owner; no agents dispatched.

## Outputs
[Design v0.1](design.md), [task card](task.md), [proposed profiles](profiles.json), [reproducible calculations](calculations.py), [calculation report](calculation-report.json), and [Mac app/data contract](app-data-contract.md) with a [synthetic record](example-result.json). These are system-design artifacts, not a fabrication or energized-test release or working app.

## Human check
The schematic, component stress/insulation review, calibration and physical fault tests must precede energizing hardware. Geometry remains unknown until exact sockets, display, supply and enclosure parts are selected.
