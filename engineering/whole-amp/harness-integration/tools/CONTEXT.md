# Panel interface audit factory
Inputs: parent connector contract, circuit and native boards. Owner: PCB integration.
Process: `check_panel_interfaces.py` derives pot wiring and inspects native pads and the installed Molex footprint using pcbnew. It never saves a board. Negative controls challenge terminal swaps, an improper shield assignment and undersized wire insulation.
Outputs: parent `results/` JSON and CSV; no manufacturing files or modified PCB.
Human check: compare the derived terminal mapping against readable schematic and physical connector views before integration.

`cable_loading.py` owns only the RV1–RV8 parasitic-capacitance experiment. It consumes the existing effects-loop fixture and ngspice adapter rather than copying the tube circuit. It writes current evidence in `results/`; no CAD or selected-component state. Run with KiCad's Python. The zero-capacitance comparison, repeated physical leads, elementary RC control and finer frequency grid check the experiment; they do not certify an actual harness.

`check_mating_geometry.py` reads candidate geometry, source hashes and installed library; it derives the peg-based edge limit and nominal mated bounds, tests datum errors, and writes JSON/SVG without changing boards.

`check_wire_dressing.py` derives axial wire-restraint bounds from the sibling contracts, challenges incorrect restraints, and writes a per-pot mechanical interface plus an explanatory SVG. It does not change a PCB or set cable bend radii.

`check_pot_voltage.py` owns the normalized DC fault screen and its report. It retains true zero-ohm endpoints, current and power balance, analytic controls and source hashes. Run with Python plus NumPy, then decorate the generated HTML with the shared reader tool. It does not change the circuit or boards.

`pot_fault_probe.py` consumes the linear-screen settings and shared generic tube/supply fixture. Each DC solve has a 35 s worker deadline. Run after `check_pot_voltage.py`, then apply the reader decorator; the report only includes paired results whose linear-input hash matches.

place_reverb_connector.py applies only the declared JR4/route/label delta to a hash-guarded source copy. check_reverb_connector.py independently compares source/candidate root items, circuit terminals, drill shapes and native DRC, then exports nominal mating/service coordinates. Both use KiCad Python; only the candidate directory is writable output. No active board, rule exclusion or schematic is changed.

The HI-008 factory also applies declared existing wet-net widths, nominal stackup and an added wet-net minimum rule. The checker verifies width-only changes, retained original rules and all wet segments. Current/thermal qualification stays with the current-budget module.

CU-002: declared existing-net width changes include PCB_ARC items, not just straight segments; source comparison checks both types. The rail rule is appended without weakening existing rules. Supply-current analysis stays in the current-budget module.
