# Effects-loop qualification
Owner: electric integration. One job: qualify the existing J3/J4 effects interface against its surrounding amplifier.
Inputs: ../reverb-600/circuit.json; ../simulation/models/dm12ax7s.inc and 6ca7s.inc; ../../../plans/effects-loop-optical-review/final.md.
Process: tools builds explicit source-derived decks and runs the existing ngspice adapter. Stable factories live in tools; generated evidence lives in results. No native KiCad mutation.
Outputs/public seam: results/summary.json, decks and logs; review.md states scope, findings and next action.
Human check: compare the actual loop voltages and dry/wet balance with the modeled cases before accepting any buffer or releasing boards.
Task card: FB-101 authorizes execution of reviewed plan. Root owns extraction, simulations and interpretation. Dependencies: current circuit and generic tube models, existing simulator. First done-condition: repeatable integrated electrical reference, source hashes, loading comparisons and timestep check; not final real-transformer, mains, noise or cabinet qualification. Estimated effort: one engineering pass; full plan remains staged.
