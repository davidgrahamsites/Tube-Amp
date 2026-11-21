# Received-tank reverb revision

One job: adapt the amp interface to the received 600 ohm / 2250 ohm spring tank.
Owner: Renegade integration agent. Inputs: ../integrated native v0.5, ../mechanical/fit-register.json, ../../solid-state-reverb connectivity and TI model, ../../component-selection evidence.
Process: keep the original amp sheets; revise the send and passive dry/wet interface in a new native revision; run bounded electrical cases and native pin/ERC checks. Stable factories live in tools; editable circuit contract is circuit.json; outputs live in cad, simulation and review.
Outputs: full integrated schematic revision, change list, scoped simulations and parts overlay. Historical PCB files are not overwritten. This module does not own a fabrication release or the expression-pedal implementation.
Human check: compare actual tank label, dimensions, coil resistance and low-level drive behavior with the recorded assumptions before commissioning. Check cabinet measurements and the eventual populated 3D assembly before ordering boards.

Done for this pass: editable circuit and full schematic capture; repeatable scoped checks; exact resistor choices where evidence supports them; explicit remaining interface/fit work. No claim of actual-tank or full-amplifier validation.
