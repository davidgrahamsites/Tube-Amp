# Simulation evidence and limits

Run with KiCad 10.0.6 bundled Python and libngspice 45.2 using `tools/spice_runtime.py`, `simulate_amp.py`, `simulate_stress.py` and `simulate_supplies.py`. Generated decks, CSV traces, JSON results and logs are retained here.

The full signal-path fixture includes eight triodes, two EL34/6CA7 pentodes, TI OPAx134 models, source passive values and an idealized output transformer. Generic Duncan/Munro valve models are not measured models of the selected JJ valves. Their source headers restrict use to educational/non-profit purposes; they must not be represented as commercially licensed production models. The ideal transformer and stiff supplies do not predict real output capability, regulation, saturation or thermal performance. No acoustic tank response is modeled.

Clean and dirty operating point and AC runs completed. Four transient cases completed (clean 1mV,20mV,200mV peak; dirty1mV peak). Dirty20mV failed to converge near the clamp diodes; the planned dirty200mV case was not reached. A failed simulation is not a pass. Clean200mV predicts about12.48W average screen dissipation, above the8W JJ reference, and dry-path limiting near12.56V peak. These are unresolved design flags, not measured damage or a qualified output-power result.

The24 supply cases span198/220/235.4/242V input,0/70/150mA extra DC load and1.00/1.12 secondary multipliers. Winding resistance100ohm per half and1.12 regulation multiplier are assumptions. These runs converged; the highest modeled unloaded reservoir peak was about510.31V. They do not establish actual transformer limits or no-load voltage. Separate supply and signal simulations are not a fully integrated chosen-parts validation.

## November12 convergence follow-up

The original failure above is retained as historical evidence. New [reproducible sensitivity runs](../tools/check_convergence.py) retain the circuit values and models and change numerical settings only: maximum timestep1µs,ITL1/ITL4=500. Dirty20mV and200mV both reach40ms. Results and full generated decks/logs are in[convergence](convergence/). Dirty20mV:12.7186W average screen-A dissipation; dirty200mV:12.8913W. These remain excessive relative to the8W reference. Predicted58–60W load power with an ideal transformer/stiff supply is not a real output-power claim and exceeds the original25W transformer reference.

A further20mV run tightens reltol from0.003 to0.0003,abstol from1nA to100pA andvntol from10µV to1µV. It completes326356 points and predicts12.7169W screen-A dissipation,about0.013% lower. Output power changes about0.0047%. Mix-output peak changes about0.87%,so clipping peak sensitivity remains larger. Numerical completion does not validate the generic tube model or real transformer behavior. No component values were changed to hide the overload.

Next: validate load/regulation and transformer parameters, improve large-signal convergence without masking clipping, bound screen dissipation and dry-path headroom, and check actual selected parts over tolerances/temperature/startup before any release.

## November12 longer screen-stress and reverb diagnostics

[80ms full-amp comparison](screen-tradeoffs/README.md) increases the predicted screen stress compared with40ms: last10ms averages at1k are16.668/16.782W, at2.2k8.622/8.656W, and at4.7k4.163/4.179W. The4.7k resistor itself averages up to4.350W, motivating a10W candidate with actual hot derating. The result is still drifting between last20ms and last10ms windows; it is not a settled worst-case claim. No native values changed. [Isolated output tests](output-stage/README.md) underestimate full-amp stress and cannot substitute for it.

[Passive dry AC experiment](passive-mix/README.md) explores keeping the high-level tube dry path outside the±15V opamps while attenuating the reverb send. It changes loading:1kHz dry insertion loss is1.584dB clean/3.480dB dirty relative to a direct dry path. This is not yet the selected topology or proof of unchanged tone. See reverb-headroom for bounded nonlinear diagnostics; native model files remain unmodified. Do not remove clamp protection merely to force convergence.

The protected combined candidate now completes80ms with100ns maximum timestep and no global artificial shunt capacitors. Nominal screen power4.14–4.16W and reverb input1.65Vpeak are reported with retained failed trials in [headroom results](reverb-headroom/README.md).18 AC cases confirm dry-control independence. High-line/long-duration/actual-part qualification remains open; no native topology changed.

Follow-up isolation ties the ringing to the unverified inductive-transformer assumptions. The separate [low-frequency ideal-transformer reference](ideal-transformer-candidate/README.md) passes independent fixture checks, short timestep sensitivity and80ms completion. This gives usable scoped low-frequency evidence while leaving actual magnetics/HF qualification open. It is not a substitute for the chosen transformer's data.
