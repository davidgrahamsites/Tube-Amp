# Expression controller stationary DC — 25 November 2026

Owner: expression-control. Task: resolve the seven failed operating points of the VAL-044 150k trim-feed candidate without substituting ideal control elements. Inputs are hash-pinned in `results/settled-bias.json`. Output is repeatable stationary DC evidence; done condition is complete duration, low late drift/capacitor current, emitter current balance and agreement under time-grid refinement. Human evidence still required: actual startup, noise and control transitions. No native adoption is included.

## Result and method

All 24 retained cases settle: twelve combinations of ±12/15/16.5V and control targets 0/2.5/4.9/5V, eight time/initialization refinements, two weak-shunt perturbations and two dry-end temperature cases at 0/70°C. The target convention remains inverse: 0V is full wet, 5V is dry. Do not connect a heel-low pedal directly to this candidate.

The original manufacturer models and physical bias/trim circuit are retained. The stimulus is set to DC zero for this test. `optran 0 0 0 1u 2m 0` provides a warm initialization, followed by an explicit two-second transient at maximum 100µs step. The input coupling capacitor needs this longer settling interval. Refinements halve the main timestep, extend to three seconds, and halve/double the initialization step. Final node agreement is within 10µV for these numerical refinements.

The last 0.2s is checked independently: every monitored node drifts less than 10µV peak-to-peak; coupling/compensation capacitor current stays below 1nA; emitter KCL residual stays below 1nA. The evidence audit includes deliberately incomplete, out-of-rail, non-finite, drifting, charging and current-imbalanced counterexamples. All 107 evidence checks pass.

At ±15V, full-wet output DC is approximately −10.8nV, midpoint +2.649mV and dry +0.501mV. At ±12V, the previously failed midpoint settles to +2.622mV. These are typical-model calculations, not offset guarantees.

Changing the numerical shunt resistance from 1TΩ to 10TΩ changes the near-off ABC node by −27.071µV, exceeding the original 10µV all-node sensitivity screen. Audio output changes by only +7.622nV. This failed sensitivity screen remains explicit in the audit; it is not disguised as timestep agreement. All runs still meet stationary-state and KCL bounds.

## Interpretation and limits

The earlier seven failed direct operating points now have settled results using this method; their historical failure records remain unchanged. Finite solver output is insufficient, as the prior isolated-controller counterexample demonstrated. The [ngspice manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf) documents transient operating-point initialization; the installed libngspice45.2 command behavior is evidenced by retained logs. Its warm initialization is not a physical supply ramp.

This closes the sampled steady-DC numerical issue only. It does not establish cold-start behavior, reverse base-emitter protection, reference backfeed, tolerance, pedal fault response, noise, wet/dry integration or manufacturability. The original OTA model also overestimates high-frequency bandwidth/phase margin. Native boards and functional block boundaries are unchanged.

Next: implement the protected pedal selector and its polarity/range mapping, then test startup and hot-plug transitions with the real wet gain cell. Qualify exact socket assembly and China purchasing before native capture. Keep the rear panel independent and include the jack/harness in the three-board chassis model.
