# Reverb headroom / solver investigation — November 12

**Development candidate, not a native-circuit or fabrication release.** The source files are preserved. Scripts: tools/check_reverb_headroom.py, probe_reverb_solver.py and run_reverb_solver_probes.py. Runtime: KiCad10.0.6 / libngspice45.2, unmodified generic tube and TI OPAx134 models. Native-bridge initialization must reload XSPICE code models after replacing logging callbacks; early missing-model attempts were harness errors, not circuit failures.

## Candidate change

Keep the dry path passive:100k from FX_RETURN to MIX_OUT,1M wet injection. Attenuate only the solid-state send by changing R601100k→1M and R60210M→100k. Move the1u output coupling and1M return resistor to WET_AC, with a1M injection resistor to MIX_OUT. The original three dual-opamp parts remain in this candidate. Both screen resistors change1k→4.7k for the combined run. These are explicit candidate changes, not a claim of preserving identical source loading or frequency response.

## Completed checks and retained failures

- Original candidate with1µs/gear fails near36.9µs while opamp input is only0.482V. A22pF input cap does not fix it.
- Trap trial failed to finish in practical time and was terminated; no result/pass claimed.
- Isolated reverb driven by ideal50Vpeak/1kHz completes5ms: input4.552V and buffer4.551V. It excludes tube-source and nonlinear PI interaction.
- Removing the clamp diodes only moves failure to2.957ms: **rejected as a fix**, protection retained.
- A1pF global numerical shunt stalls and is terminated after90s. Removing the original10fF global numerical shunt alone fails at1.461ms.
- With global cshunt=0,100ns maximum step,gear and500 iterations, the protected candidate completes1ms,5ms and20ms. The20ms run has205158 points. No physical model coefficients were changed.
- **Combined4.7k-screen candidate completes80ms/838226 points** in531s. Deck, binary raw waveforms, JSON, live solver log and execution record are saved as combined_80ms.*.

## Combined nominal result

200mV peak1kHz dirty input;400V stiff B+,-40V bias,ideal±15V rails,wet zero/muted. Peak over entire80ms: FX_RETURN20.135V,MIX_OUT19.853V,reverb input1.65135V,buffer1.65119V. Last10ms screen-A/B average4.13777/4.15928W; screen-resistor-A/B3.93927/3.79398W. These are below8W tube-screen and the candidate10W resistor's nominal hot-derated allowances, within this fixture only.

The ideal load result44.946W is **not amplifier output specification** and remains incompatible with treating the original25W transformer reference as qualified. Actual transformer, high-line/low-bias corners, convergence/time-step sensitivity of the combined candidate, steady-state duration, plate/cathode stress, real tank drive/recovery and switching/startup still require validation. This80ms pass is not a worst-case or physical safety conclusion.

An [18-case AC check](../candidate-mix/results.json) spans both channels,wet fractions0/.5/1 and dry mute on/off. At82Hz/1kHz/5kHz, six dry-gain-independence checks pass; maximum relative spread2.44e-15. Wet test injects1mV electrically at tank output, not an acoustic spring model. Passive insertion loss remains documented in ../passive-mix/README.md.

candidate-headroom.png/.pdf plots actual raw samples from75–80ms. The waveform plot does not replace longer settling or tolerance tests.

## Later waveform review supersedes any interpretation as a qualified transient

The saved waveform visibly rings at transitions. Resampled derivative-spectrum diagnosis gives approximately412kHz; this is a diagnostic frequency, not an established physical oscillation. ../candidate-hf/ contains5ms runs with100ns and50ns maximum steps and a global-feedback-zero diagnostic. All complete, but halving the timestep changes MIX_OUT peak19.853→23.327V (**17.50%**). Ringing remains around416kHz with50ns and412kHz without global feedback. Small-signal AC sweeps to10MHz do not show matching input/output gain peaking near412kHz at the quiescent point.

Therefore **the combined transient is not numerically qualified**, despite completing80ms. Screen-power numbers above remain provisional diagnostic values. Do not call the screen issue fixed or migrate this candidate to released CAD on this evidence. Separate the nonlinear valve/transformer behavior from the solid-state interface and check models/timestep sensitivity; real magnetics and bench evidence remain necessary. Protection removal was a diagnostic only and is not adopted.
