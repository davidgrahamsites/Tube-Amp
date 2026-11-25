# Panel connector integration

Owner: electrical/PCB integration. One job: translate the ten external panel-pot interfaces into removable PCB connector requirements without changing the circuit.

Inputs: `../reverb-600/circuit.json`, current `../pcb-measured-r/boards/`, and manufacturer limits in `connector-contract.json`. The earlier proposal in `../../panel-harness/` supplies candidate identities, not verified wiring geometry. Public interface: `results/pot-connectors.csv` and `results/checks.json`.

Process: run `tools/check_panel_interfaces.py` with KiCad's Python. Read all native boards without saving; derive every terminal net from the circuit, compare existing PCB endpoints and audit the installed candidate footprint against nominal drawing dimensions. Report missing board nodes and hold connector adoption until voltage, full drawing/physical numbering, wire, supplier and populated fit evidence is complete. Never delete all JM wire pads: they also serve tubes, supplies and other interfaces.

Outputs: generated pinout/migration schedule and checks, plus `review.md` explaining constraints. The contract owns connector and crimp requirements; the circuit owns pot nets; mechanical owns final position, cable length and access.

Human check: compare exact purchased parts and crimped samples to manufacturer drawings; continuity-test each numbered cavity against the pot terminals with power disconnected. Confirm CW operation, latch/extraction access and independent rear removal in the populated cabinet. None is passed by this audit.

Task HI-001: prerequisite for T09/T10; medium scope. Done for this bounded audit means ten complete derived interfaces, native endpoint evidence, nominal drill comparison, and negative controls. Manufacturing readiness remains a separate gate.
