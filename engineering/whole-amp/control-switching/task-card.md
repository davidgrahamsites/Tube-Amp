# Reset / relay qualification task
Driver baseline: a9fd3fb. Current reset-edge baseline: 91b0a9c; current four-board draft, 5 V preload and relay-driver correction already integrated.
Owner: integration agent; no delegation.
Outputs: reproducible threshold budget, manufacturer reset-model tests, explicit relay-driver surrogate tests, exact domestic part observations and bounded native correction if gates pass.
Dependencies: final 5 V regulated envelope, exact removable U3 carrier, driver suppression at the controller as well as remote coils, final connector/harness geometry. Functional blocks and named signals stay intact.
Automated work: datasheet bounds, reset startup/brownout/manual-reset simulations, gate/coil switching screen, native pin/geometry/ERC/DRC checks where adopted.
Human evidence: measured cold/hot supply, actual rail fall rates, socket fit, wiring inductance/transients, relay operation and audible switching behavior. Actual drill dimensions remain deferred to November 25.
Done condition for this task: clear candidate/adopted status, repeatable checks with negative controls, documented unresolved limits, ICM record and Git checkpoint. This is not completion of the six-scope amplifier goal.
Effort: bounded component/interface engineering pass; hardware qualification is a separate dependency.
