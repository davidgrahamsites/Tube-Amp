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

November25 VAL-064: current load contract and results/loads include native R619/R620. [Integration review](../reverb-600/rail-load-integration/review.md) owns the updated72-case current/heat table and32-case candidate brownout regression. The hold-up factory consumes this extra load for future runs; existing results/hold-up and transformer comparisons remain historical snapshots.

November25 VAL-069: envelope-contract.json working audio allocation is70mA per rail, with native rail loads still added separately. Current results/loads are refreshed; load-review.md links the source-bound passive budget in ../pcb-measured-r/current-budget/. Earlier envelope/transformer/hold-up products remain historical until explicitly regenerated and reviewed.

CB-008. Supply qualification owns guard_transformer.py and guard_regulators.py under tools. Run them in this order with KiCad Python. Both read existing load and transformer contracts and produce results/guard-*.json. Check winding RMS, raw extrema, available regulator heat paths and charging surge against actual hot hardware.

CB-009. Supply qualification owns the dedicated regulator sink trial. Run tools/regulator_cooling.py against the CB-008 load profiles. Compare results/regulator-cooling.json with temperatures at the regulator tabs, sink and inlet in the closed cabinet.

CB-010/011 compares U4 cooling and accounts for the added cutoff control load. Read the [return supply and heat report](../effects-loop/common-buffer/gain-cutoff-template.html).
