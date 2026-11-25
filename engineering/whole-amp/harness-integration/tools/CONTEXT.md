# Panel interface audit factory
Inputs: parent connector contract, circuit and native boards. Owner: PCB integration.
Process: `check_panel_interfaces.py` derives pot wiring and inspects native pads and the installed Molex footprint using pcbnew. It never saves a board. Negative controls challenge terminal swaps, an improper shield assignment and undersized wire insulation.
Outputs: parent `results/` JSON and CSV; no manufacturing files or modified PCB.
Human check: compare the derived terminal mapping against readable schematic and physical connector views before integration.

`cable_loading.py` owns only the RV1–RV8 parasitic-capacitance experiment. It consumes the existing effects-loop fixture and ngspice adapter rather than copying the tube circuit. It writes current evidence in `results/`; no CAD or selected-component state. Run with KiCad's Python. The zero-capacitance comparison, repeated physical leads, elementary RC control and finer frequency grid check the experiment; they do not certify an actual harness.
