# Reset and relay factories

rail_delay_budget.py reads ../rail-delay-contract.json, calculates conditional RC/base-drive bounds and independently integrates branch currents. It writes ../results/rail-delay-budget.json with brief-fault failures separate from arithmetic checks; no native mutation or automatic part selection.

relay_latency.py reads ../relay-latency-contract.json and existing coil data. It calculates current decay and runs bounded SPICE subprocesses; logs/decks and a failed restore diagnostic remain in ../results/relay-latency.json. It has no contact-motion or whole-circuit acceptance model. rail_delay_budget.py also reads native source/schematic/board values to guard the declared R341 candidate boundary.
Owner: Renegade integration. Inputs: ../contract.json, ../models and the shared ../../tools/spice_runtime.py adapter.
Process: calculate_bounds.py reads manufacturer limits; simulate_reset.py runs the unmodified TI nominal model; simulate_drivers.py uses an explicitly named engineering surrogate. Independent outputs are retained in ../results; no simulation writes native CAD.
Outputs: editable JSON evidence and exact decks with hashes. Human check: compare assumed supply, capacitance, harness and temperature bounds with actual assembled hardware; a nominal model is not a worst-case guarantee.

Reset edge stage: integrate_reset_edges.py then finalize_reset_edges.py are guarded one-time mutations. edge-routes.json is the human-editable route recipe. check_reset_edges.py independently validates the current delta, including layer-aware routes and temporary Excellon exports. analyze_reset_edges.py produces bounded datasheet/model evidence. Historical driver-specific validators apply only to their recorded revision.

Brownout factories consume ../brownout-contract.json and unmodified TI model. check_brownout_limits.py compares guaranteed limits and proposed noise allocation. simulate_brownout_matrix.py writes the dip matrix, including failed coarse refinement; refine_brownout_matrix.py writes the next refinement without relaxing tolerance.

check_divider_options.py reads ../divider-contract.json, verifies retained manufacturer/baseline hashes, and compares independent resistor, threshold, leakage, temperature and solder/endurance limits. It preserves the historical contract and native CAD. A passing arithmetic receipt includes explicit failed engineering profiles; inspect ../divider-review.md.

rail_monitor_budget.py owns static endpoint analysis of rail-monitor-contract.json. It writes rail-monitor-budget.json with failed constraints and qualification=false. It is not a transient comparator model or CAD writer.

buffered_rail_budget.py consumes the buffered contract, calls the shared endpoint calculator and checks the equations with an independent nodal solver. Outputs are static evidence only; no native mutation or vendor-model substitution.

audio_headroom_budget.py guards native signal/capacitor inventory and rejects the previous rail-warning boundary. precision_rail_budget.py consumes that hashed evidence plus the precision contract, enumerates settled corners and independently checks KCL. Its passive reference-off check is explicitly conditional; it never writes native CAD.
