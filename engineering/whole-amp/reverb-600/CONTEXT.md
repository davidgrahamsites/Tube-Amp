# Received-tank reverb revision

One job: adapt the amp interface to the received 600 ohm / 2250 ohm spring tank.
Owner: Renegade integration agent. Inputs: ../integrated native v0.5, ../mechanical/fit-register.json, ../../solid-state-reverb connectivity and TI model, ../../component-selection evidence.
Process: keep the original amp sheets; revise the send and passive dry/wet interface in a new native revision; run bounded electrical cases and native pin/ERC checks. Stable factories live in tools; editable circuit contract is circuit.json; outputs live in cad, simulation and review.
Outputs: full integrated schematic revision, change list, scoped simulations and parts overlay. Historical PCB files are not overwritten. This module does not own a fabrication release or the expression-pedal implementation.
Human check: compare actual tank label, dimensions, coil resistance and low-level drive behavior with the recorded assumptions before commissioning. Check cabinet measurements and the eventual populated 3D assembly before ordering boards.

Done for this pass: editable circuit and full schematic capture; repeatable scoped checks; exact resistor choices where evidence supports them; explicit remaining interface/fit work. No claim of actual-tank or full-amplifier validation.

November 24 T03: `grounding-contract.json` owns the explicit external GB1 signal/chassis bond and permanent PE constraints. `tools/check_grounding.py` proves native topology with a temporary cut-wire negative control, preserving active CAD. `tools/grounding_contract.py` exposes the hash-checked alias seam to native/PCB audits; no general PE-to-GND equivalence is allowed. `review/grounding-review.md` owns the engineering interpretation and physical qualification limits. Native copper/geometry and panel manufacture are not approved by this check.

November 25 interface-voltage: `interface-voltage/` owns the source-derived dry/wet stress screen and JR1/JR5 voltage-metadata correction. Its independent capacitor-differential checks inform the held ground-plane work; they do not qualify the selected RETURN, physical insulation or fault protection. Start with `interface-voltage/review.md` before accepting copper around the dry interface.

November 25 clamp/rail injection: `input-clamps/` owns bounded input and output clamp injection, a two-rail load correction candidate and its analytic/SPICE evidence. `input-clamps/review.md` distinguishes the proposed 10k loads from native integration and full power-sequencing qualification.

Current rail-load correction: [rail-load-integration/review.md](rail-load-integration/review.md), VAL-064. R619/R620 are now native; exact R601 package/rating synchronized. Earlier VAL-063 source-preservation claims are historical. Voltage-domain spacing/ground pour and whole-system qualification remain open.
