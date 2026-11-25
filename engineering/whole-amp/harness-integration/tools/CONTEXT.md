# Panel interface audit factory
Inputs: parent connector contract, circuit and native boards. Owner: PCB integration.
Process: `check_panel_interfaces.py` derives pot wiring and inspects native pads and the installed Molex footprint using pcbnew. It never saves a board. Negative controls challenge terminal swaps, an improper shield assignment and undersized wire insulation.
Outputs: parent `results/` JSON and CSV; no manufacturing files or modified PCB.
Human check: compare the derived terminal mapping against readable schematic and physical connector views before integration.
