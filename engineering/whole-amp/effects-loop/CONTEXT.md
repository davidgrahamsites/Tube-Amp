# Effects-loop qualification
Owner: electric integration. One job: qualify the existing J3/J4 effects interface against its surrounding amplifier.
Inputs: ../reverb-600/circuit.json; ../simulation/models/dm12ax7s.inc and 6ca7s.inc; ../../../plans/effects-loop-optical-review/final.md.
Process: tools builds explicit source-derived decks and runs the existing ngspice adapter. Stable factories live in tools; generated evidence lives in results. No native KiCad mutation.
Outputs/public seam: results/summary.json, decks and logs; review.md is the entry point; solver-review.md records the domain correction, resolved timeouts and manufacturer SEND-model limits.
Human check: compare the actual loop voltages and dry/wet balance with the modeled cases before accepting any buffer or releasing boards.
Task card: FB-101 / FB-102 authorizes execution of reviewed plan. Root owns extraction, simulations and interpretation. Dependencies: current circuit and generic tube models, existing simulator. First done-condition: repeatable integrated electrical reference, source hashes, loading comparisons and timestep check; not final real-transformer, mains, noise or cabinet qualification. Estimated effort: one engineering pass; full plan remains staged.

T04 approximately 25 W reference: power-target-review.md owns interpretation; results/power-target-summary.json and power-target-25w-check.json own the bounded sweep/refinement evidence. Model limitations, especially nonphysical secondary DC, prevent hardware-rating or RETURN acceptance.

FB-111 output-protection continuation: protection-review.md owns interpretation and the integration decision. tools/protection_model.py defines explicit candidate deltas; results/protection-acceptance-summary.json and protection-audit.json own finite-matrix evidence. Mechanical handoff retains socket-local mounting, candidate body/lead envelopes and unresolved thermal/service space; no functional-block repartition.

FB-112 transformer/feedback continuation: feedback-review.md owns the83-case AC comparison, five long transients and HF timestep negative control. Model and native circuit remain distinct; no compensation is adopted. Human check: correlate actual transformer/load response and instrument bandwidth before accepting stability. The mechanical diagnostic uses current board geometry, not guessed populated clearance.

Loaded-winding continuation: loaded-feedback-review.md owns interpretation; results/loaded-feedback-summary.json and loaded-burst-summary.json hold the reciprocal-tap evidence. It supersedes the ideal-tap approximation only for this experiment, not the selected circuit. Read both positive and rejected cases; no compensation is adopted.

RETURN supply diagnosis: return-supply-review.md owns the task card, eight causal cases and twelve isolated-rail follow-ups. The public evidence seam is results/return-supply-audit.json. A50Ω rail-isolation experiment completes the previously failing20kHz conditions with100nF bypass retained; no production adoption or integrated-loop qualification is implied. Human check: compare actual startup, HF, thermal and wet-mix behavior before selection.

RETURN behavior choice: return-port-review.md owns the source/load-impedance comparison and signal-path-options.md owns the three functional diagrams requested in FB-121. Public numeric seam: results/return-port-audit.json and CSVs. Fixed output resistance is not transparent across sampled controls; a behavior choice remains open. The diagram request does not authorize topology adoption. Preserve current native circuit while qualifying independent dependencies.
