# Transformer option evidence
Owner: auxiliary supply qualification. Inputs: ../../transformer-candidates.json, existing raw-model and cold-coil/preload contracts.
Process: ../../tools/screen_transformer_candidates.py overwrites screen.json and simulator.log; ../../tools/check_transformer_candidates.py audits the comparison. Preserve prior adopted-circuit evidence in its separate owner folders.
Outputs: a conditional 120/220V transformer/reservoir/U4 comparison, with retained decks, numerical refinement and assumptions. No native component or wiring adoption.
Human check: confirm primary operating range, regulation tolerances, current rating, dimensions and Chinese availability with the manufacturer/supplier, then bench-test selected parts before qualification.
