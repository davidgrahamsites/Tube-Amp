# Reverb coupling capacitor repair
Owner: component and PCB integration. One job: replace C607's insufficient conditional fault-voltage rating with an exact locally sourced film capacitor while retaining capacitance and functional interfaces.
Inputs: ../../whole-amp/reverb-600/interface-voltage, canonical circuit/native board, coverage.json and exact manufacturer/supplier evidence in evidence.
Process: tools/integrate.py updates the declared C607 part and local pad escape only; tools/check.py verifies source/native identity, changed holes and copper, native ERC/DRC and readable schematic preservation. Source of truth is the current native revision, not a historical generator.
Outputs: selected footprint, source/schematic/PCB update, contract.json, review.md and results receipts. Factories and generated evidence are separate.
Human check: compare the purchased capacitor marking/body/lead dimensions and hand-formed pitch against the drawing; verify insertion, thermal clearance and actual fault protection before fabrication/energizing. This change does not qualify all interface insulation or the whole amplifier.
