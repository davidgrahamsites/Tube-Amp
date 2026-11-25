# Supply solver and practical bias checkpoint — 25 November 2026

Owner: expression-control. This is an isolated wet gain-control candidate, not an adopted pedal circuit. Functional audio/power/control/reverb boundaries and all native boards remain unchanged.

## Task card

Inputs: DEC-016, VAL-042, existing TI LM13700/OPAx134 models and the Diodes Incorporated MMBT3906 numerical model card. Outputs: supply_probe.py, bias_screen.py, retained decks/logs/JSON, dated source observations and audit_supply_bias.py. Done condition for this checkpoint: explain the previous ±12V timeout, test a realizable bias circuit, expose remaining failures and preserve CAD. This does not close the through-chassis goal. Human evidence: real noise, control artifacts, stability, parts, temperature spread and assembled fit. Estimated scope: one bounded circuit investigation.

## Previous timeout: incorrect operating point

The nine-case supply diagnostic retains the original 25-second timeout and the invalid starting solution: the op-amp model reports approximately −497.942V on ±12V rails. Solver return code zero is insufficient. A stronger numerical shunt lets the transient finish but leaves that impossible operating point; it is explicitly rejected.

Ordinary 1e12Ω numerical shunts plus external-node `.nodeset` starting guesses find a rail-bounded solution. Output guesses −1/0/+1V converge to the same −0.244196V operating point; gain differs by less than1ppm. A half timestep changes 1kHz gain0.0037801%; 1e13Ω shunts change gain less than1ppm. The corresponding ±15V case also completes. Six corrected transients finish16ms. No manufacturer model or physical component was changed in this diagnostic. `.nodeset` is a solver guess, not a forced initial condition or a model of startup.

This resolves the isolated VAL-042 timeout mechanism. The approximately −0.25V residual at ±12V still belongs to that old circuit and its rail-dependent trim; it is not qualified by fixing the solver.

## Practical bias candidate

The current candidate uses an ideal **5V reference input** in place of the two ideal bias-current sources. Actual reference generation, loading, noise and faults remain outside this experiment.

- A Diodes MMBT3906 PNP and OPAx134 servo set amplifier bias through10kΩ. A1kΩ base resistor and1nF feedback capacitor are trial compensation values. A100kΩ output-to-emitter feedback path keeps DC feedback when the PNP turns off; a1MΩ ABC-to-negative-rail resistor gives the bias pin a defined discharge path. Neither is a numerical shunt.
- Two more MMBT3906 devices form the linearizing-diode current mirror, with4.32kΩ reference resistor. They share a typical model; actual mismatch and thermal gradients are not represented.
- The100kΩ internal offset trim is now across5V/ground and feeds the negative input through330kΩ. This is not the user's panel knob. Nominal calibration is0.988718 of travel, uncomfortably near its limit; production trim margin is unresolved.
- Existing100kΩ/1kΩ input network and215kΩ/10pF transimpedance feedback remain screening values. Calibration and full-range gain must be finalized together before capture.

Twenty-four final cases are retained:17complete and7failed operating-point cases. Full- and mid-gain cases complete on ±12/15/16.5V. Full-gain DC is approximately −54/−27/−14µV in those cases, replacing the old circuit's large supply-dependent offset. Nominal full bias is about489µA and diode bias1.020mA.

At8Vpeak/1kHz input, gain is0.95870 at±12V and0.95886 at±15V; computed second-through-ninth harmonic THD is about0.05901%. The half-step gain change is approximately0.00381%. The10kHz case gives gain0.95053 and THD0.05753%. These are isolated candidate inputs, not the verified spring output or full amplifier envelope.

A5ms internal control ramp from full gain to off completes16ms. Final target5V gives base-emitter reverse voltage only about5.49mV in this run and output DC about0.501mV. The nominal model's tiny residual fundamental is **not** a real noise-floor or mute-attenuation specification. This ramp is a diagnostic of reachable steady state, not a protected pedal hot-plug or cold-start test.

Direct operating-point solves at targets4.9V and5V fail at all three rail values. A resistor-only diode-bias comparison also fails in the final candidate configuration. Earlier exploratory circuits are not equivalent controlled comparisons; do not use their distortion numbers as a final A/B result. No failing case is counted as a circuit pass. Fixed nominal trim gives+25.93mV at0°C and−38.92mV at70°C: AC coupling, smoothing and thermal spread still need work.

## Sourcing and new marketplace instruction

Public Chinese LCSC observations on25November:

| Exact candidate | Listing | Observed stock / MOQ | Consequence |
|---|---|---|---|
| Diodes BC857B-7-F / C516596 | https://item.szlcsc.com/532975.html |9000 /3000| This route is uneconomical for one build; do not reject the part solely on this listing. |
| Diodes MMBT3906-7-F / C82762 | https://item.szlcsc.com/83922.html |608 /1| Small-quantity candidate used with its own manufacturer model; displayedCNY0.2459 tier is not confirmed. |

FB-126 / DEC-017 adds Taobao and Pinduoduo small-quantity searches. Initial public indexed queries did not establish a matching exact seller listing. Seller identity, manufacturer/suffix/package, condition, quantity and Shanghai delivery still require evidence. These observations do not authorize orders. LCSC's domestic delivery policy supports a Shanghai route in principle, not the exact address/fee/order acceptance.

The Diodes model card was transcribed unchanged from the primary web tool response because direct download access was denied. Its manifest states that acquisition method; it is not claimed to be a byte-identical downloaded file. The numerical card and upstream URL are retained. Primary references: [MMBT3906](https://www.diodes.com/part/view/MMBT3906/), [model](https://www.diodes.com/spice/download/2962/MMBT3906.spice.txt), [datasheet](https://www.diodes.com/datasheet/download/MMBT3906.pdf), [delivery](https://www.szlcsc.com/help/202.html).

## Audit and next action

133 evidence checks pass: provenance/deck integrity, explicit invalid-solution controls, duration, seed/refinement sensitivity, nominal current/DC/audio bounds and unchanged native boards. The audit separately reports all7failed cases and `circuit_qualified:false`. The TI OTA bandwidth/stability limitation remains; neither the audit nor a completed transient qualifies real stability, safety or fabrication.

Next: diagnose low-current direct solves using the converged control-ramp state; provide adequate trim range; qualify AC coupling, actual reference/controller and supply sequencing. Then implement the protected jack, switch debounce/transition smoothing, unplug fallback and independent reverb-off override; compare full wet/dry behavior and noise before native integration. Keep sockets, three-board fit, rear removal and full drill clearance open.
