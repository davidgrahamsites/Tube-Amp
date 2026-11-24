# Control reset and relay switching
Owner: Renegade integration. One job: qualify the reset-to-relay electrical interface.

Inputs: ../reverb-600/circuit.json, native latch sheet and Control/Main/Reverb boards; exact manufacturer data and dated supplier observations in review.md. Baseline a9fd3fb5e12f23d84b21dd751f16ec957ed9e62e.
Process: contract.json owns candidate limits. tools calculates corners and simulates bounded cases through ../tools/spice_runtime.py. models retains unmodified manufacturer models separately from generated decks/results. Native adoption requires a separate preservation/netlist/ERC/DRC and visual gate. No factory silently regenerates other modules.
Outputs/public seam: review.md, contract.json and results/*.json. Candidate supervisor and native driver status are explicit. Socket hardware belongs to ../../component-selection/socketing; these checks do not qualify that interface.
Human check: measure reset startup/brownout, HC74 outputs, driver drain transients and relay pickup/release on the assembled harness at actual temperatures. Check every IC/tube is removable and the installed socket carrier pin mapping matches its drawing.
