# Reset and relay factories
Owner: Renegade integration. Inputs: ../contract.json, ../models and the shared ../../tools/spice_runtime.py adapter.
Process: calculate_bounds.py reads manufacturer limits; simulate_reset.py runs the unmodified TI nominal model; simulate_drivers.py uses an explicitly named engineering surrogate. Independent outputs are retained in ../results; no simulation writes native CAD.
Outputs: editable JSON evidence and exact decks with hashes. Human check: compare assumed supply, capacitance, harness and temperature bounds with actual assembled hardware; a nominal model is not a worst-case guarantee.
