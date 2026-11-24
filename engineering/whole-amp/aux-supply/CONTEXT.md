# Auxiliary supply qualification
Owner: Renegade integration. One job: qualify the control and reverb low-voltage supply and its local support parts.
Inputs: ../reverb-600/circuit.json and native sheet08, component selection and manufacturer regulator guidance.
Process: bounded repairs preserve functional interfaces. tools/correct_c212.py owns the guarded C212 value correction; results retains native before/after evidence. Read review.md before using any result.
Outputs/public seam: review.md and results/c212-checks.json for the historical correction; envelope-contract.json, envelope-review.md and results/envelope for the current raw-supply/conditional-thermal screen. Exact socket/heatsink implementation remains in component-selection/socketing and the populated chassis.
Human check: verify actual local capacitor placement, socket/contact fit, regulator heat and startup behavior. A datasheet value correction does not qualify the whole supply.
