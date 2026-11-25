# Current supply-load evidence
Owner: auxiliary supply qualification. One job: retain the current load inventory and cold-coil raw-supply screen.
Inputs: ../../load-contract.json, ../../envelope-contract.json, ../../preload-contract.json, control-switching contract and reverb-600 circuit.
Process: ../../tools/calculate_loads.py produces budget.json; ../../tools/screen_cold_loads.py produces raw-screen.json and simulator.log; ../../tools/check_loads.py verifies input freshness, arithmetic and adversarial checks. These factories replace this current result set without archiving full copies.
Outputs: conditional load and rectifier/thermal evidence only. Historical envelope/preload results remain frozen comparisons.
Human check: verify actual coil, tube, pilot and transformer parts; measure winding current, startup and regulator temperatures. No copper, socket, sourcing or manufacturing approval follows from this screen.
