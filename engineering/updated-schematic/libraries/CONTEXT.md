# Portable draft symbols

One job: supply project-local symbols with traceable terminal mappings.

## Inputs
Official symbols installed with KiCad 10.0.6 and logical off-board transformer/tank/legacy-indicator interfaces defined by the circuit register.

## Process
Resolve inherited symbols into local copies. Physical tube anode/cathode terminals use passive ERC types rather than digital output types. Correct the official EL34 pin8 name from F1 to K; retain actual numbers and heater pins. Do not infer a footprint or wire color from logical transformer/tank terminal names.

## Outputs
`Renegade_Draft.kicad_sym` and `symbol-provenance.json`; all native sheet symbols are cached in their schematic files.

## Human check
Verify purchased part pinouts, relay suffix, transformer wire colors/phasing, tank case bonding and actual socket footprints before physical design. Source-library copies are subject to KiCad library licensing; retain provenance.
