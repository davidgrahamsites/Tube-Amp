# Reset and relay factories
Owner: Renegade integration. Inputs: ../contract.json, ../models and the shared ../../tools/spice_runtime.py adapter.
Process: calculate_bounds.py reads manufacturer limits; simulate_reset.py runs the unmodified TI nominal model; simulate_drivers.py uses an explicitly named engineering surrogate. Independent outputs are retained in ../results; no simulation writes native CAD.
Outputs: editable JSON evidence and exact decks with hashes. Human check: compare assumed supply, capacitance, harness and temperature bounds with actual assembled hardware; a nominal model is not a worst-case guarantee.

Reset edge stage: integrate_reset_edges.py then finalize_reset_edges.py are guarded one-time mutations. edge-routes.json is the human-editable route recipe. check_reset_edges.py independently validates the current delta, including layer-aware routes and temporary Excellon exports. analyze_reset_edges.py produces bounded datasheet/model evidence. Historical driver-specific validators apply only to their recorded revision.
