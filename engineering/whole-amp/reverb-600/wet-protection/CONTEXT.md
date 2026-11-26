# Wet-contact fault protection
Owner: amplifier integration. One job: qualify a local bidirectional clamp candidate across WET_AC/GND against normal audio and tube-derived faults, before changing K3 or board interfaces.

Inputs: current reverb-600/circuit.json at 297850b, VAL-061/065/066 and exact manufacturer data. Process: source-bound resistor/capacitor reduction, DC tolerance corners, AC loading sensitivity and contact-closing transients. Outputs: editable contract.json and review.md; tools own calculations; results own generated evidence; sources own immutable manufacturer documents/provenance. No fabrication release.

Human check: verify hot/cold clamp voltage, leakage/capacitance and actual contact transients on the assembled circuit before commissioning. Done-condition: a justified local correction and exact remaining implementation/part gates, without replacing functional blocks. Scope estimated one protection investigation; no native edits in this stage.
