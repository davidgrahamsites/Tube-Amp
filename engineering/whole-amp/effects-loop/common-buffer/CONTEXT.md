# Common-buffer headroom decision
Owner: amplifier integration. One job: distinguish normal output-power requirements from overload preservation before selecting the approved common loop buffer.

Inputs: DEC-016, current reverb-600 circuit at f3d258d, effects-loop loaded_feedback_model and generic tube models. Process: compare an unlimited common buffer with explicit 10/12 V output ceilings, using the same preamp, spring-send and output interfaces. Outputs: contract.json, review.md, source-bound decks and measured comparisons under results. No native mutation or device selection. Human check: verify actual transformer/load and listening/bench overload behavior before accepting a reduced voltage envelope.

Done-condition for this pass: completed or explicitly failed bounded comparisons, numerical refinement for the deciding case, reproducible metrics and a justified next architecture action. An ideal clipping model cannot qualify an op amp, pedal protection, noise, rail sequencing or physical safety. Estimated effort: one finite headroom comparison. Existing blocks and all six build requirements remain intact.
