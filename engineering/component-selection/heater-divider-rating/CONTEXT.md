# Heater-elevation divider rating
Owner: component selection. One job: qualify bounded resistor voltage/power and compare correction candidates at the existing HREF interface.
Inputs: contract.json, current R506/R507/C505 source and selection identities, manufacturer FMP/PR documents. Current source hash and native baseline are guarded.
Process: tools/screen.py enumerates normal and declared single-fault DC corners and independently compares RC startup with ngspice. Candidate screening does not mutate source or PCB.
Outputs: results/screen.json, simulator log, review.md and supplier observations. Selection, CAD adoption and actual transformer/thermal qualification are separate gates.
Human check: inspect source pin map, correct resistor wire variant, hot placement, film/lead temperatures and physical lead forming. R507-open and R506-short hazards are not fixed by a higher-rated R506.
Task HD-001: baseline78919a2; estimated one scoped engineering wave; done when bounds, alternatives and preserved native inputs are recorded. Exact domestic supply and populated thermal evidence remain required for adoption/release.

Task HD-002: baseline d5566cd; one diagnostic wave. interface-contract.json binds current cathode/heater topology, existing fixture/models and primary tube-reference limits. tools/interface_screen.py samples cathode extremes; tools/check_interface.py independently audits interval intersections and receipts. Results and interface-review.md establish whether resistor selection alone can qualify the existing shared reference. Done means source-bound findings and a correction boundary, not a redesigned heater supply or a qualified tube. Exact tube identity, actual supply, startup and physical verification remain required.
