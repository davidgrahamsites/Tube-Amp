# Schematic generation and checking tools

One job: produce and check native schematic artifacts against an explicit connectivity register.

## Inputs
`build_design.py` contains reviewable circuit pin maps; `kicad_factory.py` resolves installed symbols and writes native files. The installed KiCad 10 CLI and its libraries are the native parser/checker.

## Process
The generator was used for initial capture, with stable UUIDs and portable local symbols. After manual schematic editing, use the native files as authoritative and reconcile `design-connectivity.json`; do not rerun generation over user edits. `check_netlist.py` compares fresh native XML exports with the register, including cross-sheet connections and intended no-connects. `run_explorations.py` runs limited RC/bias analyses with KiCad's bundled ngspice.

## Outputs
Native design files, `design-connectivity.json`, pin-connectivity check results and reference simulation results. Generated-file hashes protect manual edits against accidental regeneration. `wire_layout.py` rearranges preserved v0.2 native instances using `../wire-layout.json`, routes continuous wires, keeps full native component values behind compact visible Display fields, and guards subsequent edits with `../wire-layout-files.json`. `check_layout_equivalence.py` independently compares fresh native component references/values and physical pin partitions to the archived v0.2 native export.

## Human check
Review source fidelity and circuit decisions separately: a generator/register consistency pass does not independently prove the source transcription or the electrical design.
