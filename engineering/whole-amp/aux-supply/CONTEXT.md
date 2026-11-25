# Auxiliary supply qualification
Owner: Renegade integration. One job: qualify the control and reverb low-voltage supply and its local support parts.
Inputs: ../reverb-600/circuit.json and native sheet08, component selection and manufacturer regulator guidance.
Process: bounded repairs preserve functional interfaces. tools/correct_c212.py owns the guarded C212 value correction; results retains native before/after evidence. Read review.md before using any result.
Outputs/public seam: review.md and results/c212-checks.json for the historical correction; envelope-contract.json, envelope-review.md and results/envelope for the current raw-supply/conditional-thermal screen. Exact socket/heatsink implementation remains in component-selection/socketing and the populated chassis.
Human check: verify actual local capacitor placement, socket/contact fit, regulator heat and startup behavior. A datasheet value correction does not qualify the whole supply.

Current R215 change and acceptance limits: preload-review.md and preload-contract.json. Results/preload contains native before/after reports, exact-family package excerpt, guarded integration receipt and updated raw-load simulations. This supersedes the historical unadopted-preload proposal only.

Current load/model seam: load-review.md, load-contract.json and results/loads. This supersedes the room-temperature relay load in the prior raw screens, retaining R215. calculate_loads.py binds the existing control cold-coil assumptions to actual relay and heater references; screen_cold_loads.py adds current-path RMS/peak evidence; check_loads.py audits the result. It does not qualify complete loads, trace sizes or purchased parts.

Unadopted transformer options: transformer-review.md and transformer-candidates.json own the115/230V candidate comparison in120/220V operating modes. Results/transformer-candidates retains the current comparison. The review links a ready-to-review supplier inquiry; no message or order has been sent.

Advance-mute hold-up seam: hold-up-contract.json and hold-up-review.md own the unadopted adjustable-regulator/raw-reservoir comparison. results/hold-up distinguishes the rejected 25 VA tolerance corner from a targeted 50 VA reference. It does not modify transformer selection, native CAD or the complete current budget. Actual detector/contact timing, China sourcing and populated fit remain open.
