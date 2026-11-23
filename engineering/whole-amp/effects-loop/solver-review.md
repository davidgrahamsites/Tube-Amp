# Tube-model correction and real SEND-driver screen — 23 November 2026

Owner: electric integration. Authority: FB-101 / DEC-014. Status: numerical screening, not fabrication release.

## Engineering disposition

The first large-signal failure has been localized to the EL34 model's fractional-power expression. A domain guard fixes that failure without changing the intended nonnegative model equation. Ten of twelve heavy-overdrive cases complete; two remain time-limited. The return circuit still needs substantial voltage swing. A padded solid-state SEND branch is promising, but neither its protection nor the return architecture is released.

No native schematic, PCB, component selection or mechanical geometry is changed by this pass. Existing relay controls remain selected for their existing functions. The quiet signal, reverb and power blocks remain separate.

## Numerical correction

The retained `6ca7s.inc` model defines `gs` with URAMP, then evaluates `V(gs)^1.5`. Negative intermediate Newton trial values can put the fractional power outside its real domain. The fixture's optional `guard_pentode_power=True` emits an inline copy with `URAMP(V(gs))^1.5`. Its coefficients and licensing notice are retained. The source model file is untouched and the default fixture remains unguarded so the historical failure is reproducible. This is a solver-domain correction, not a claim of improved tube fidelity.

The seven bounded diagnostic decks retain the same stimulus: clean, B_EARLY 240 V, 1 kHz, 1 V peak, 50 ms requested duration.

| Diagnostic | Outcome |
|---|---|
| Original model | Fails around 48 microseconds |
| More timepoint iterations | Still fails |
| Trapezoidal integration and more iterations | Still fails |
| Remove numerical node shunts | Still fails |
| Remove EL34 stage only | Completes |
| Remove phase inverter and EL34 stage | Completes |
| Full fixture, fractional-power guard | Completes |

Removed-stage decks are fault-localization tests only. They are not amplifier alternatives. [ngspice documentation](https://ngspice.sourceforge.io/docs.html) is the reference for solver options and `.nodeset`; increasing iteration counts alone did not resolve the observed failure.

Four guarded normal-signal cases were compared with the retained unguarded results at eleven signal nodes each. Maximum relative fundamental-amplitude change: **0.00001814%**. This supports the narrow domain correction at those points, not the accuracy of the physical tube model.

## Heavy-overdrive results and limits

The matrix uses clean/dirty, B_EARLY 240/320 V, 82.4/1000/5000 Hz, and 1 V peak source. Volume fraction is 0.25 and tone/gain fractions are 0.5. B_PRE follows the fixture at B_EARLY +35 V. Ten cases completed. Dirty-channel 5 kHz at both rails exceeded the 120-second wall-clock limit after the original 30-second attempts. Their saved status is **timeout**, not pass. Some completed cases also show residual window-to-window settling; completion alone is not full qualification.

The previously failing clean/240 V/1 kHz case reaches 0.5 seconds. Its coarse-run internal FX_SEND swings approximately **−79.68 to +66.16 V**. This is an internal tube signal, not a pedal-safe level. It demonstrates that a unity buffer on ±15 V cannot transparently reproduce this checked overload waveform.

The first timestep refinement exceeded the 0.02 percentage-point THD comparison limit at the speaker diagnostic node. A further refinement was therefore run. Comparing 192 to 384 samples per cycle with maximum steps reduced from 10 to 5 microseconds:

| Node | Fundamental change | THD change, percentage points |
|---|---:|---:|
| FX_SEND | 0.0001152% | 0.0048077 |
| PI grid | 0.0006272% | 0.0048061 |
| Speaker diagnostic | 0.0005267% | 0.0031556 |

These pass the scoped numerical comparison of 0.1% amplitude and 0.02 percentage-point THD. They do not validate real output power. The fixture uses stiff supplies, generic tubes, fixed bias and an ideal behavioral transformer with no saturation and nonphysical DC transfer. Power supply sag, component spread, actual transformer response and the full control/pickup envelope remain open.

## TI macro-model SEND check

The retained TI OPAx134 model was tested as a unity follower on ±15 V, preceded by a provisional 9.9 MΩ /100 kΩ divider and followed by 100 Ω series resistance. This is a standalone branch; its source is ideal. It does not replace the integrated loading study or qualify a return stage. See the [TI OPA2134 datasheet](https://www.ti.com/lit/ds/symlink/opa2134.pdf) for device limits beyond the macro-model.

Six AC sweeps cover 10 kΩ and 100 kΩ loads, each with approximately zero, 2 nF and 10 nF cable capacitance. Worst change at 20 kHz relative to 1 kHz is −0.0784 dB. Offset is approximately 0.50 mV. No gain peaking was found in these nominal closed-loop sweeps; this alone does not prove stability at all component, supply and cable corners.

Four 1 kHz transients cover 100/200 V peak before the divider, with a normal 10 kΩ/2 nF load or a 0.01 Ω external short. All reach 30 ms. Normal port outputs are approximately 0.99/1.98 V peak. Shorted peak currents are approximately 10/20 mA; the 100 Ω resistor dissipates approximately 5/20 mW averaged over the retained time window. Average power is time-weighted. These are limited stimulus cases, not a guaranteed short-circuit or thermal rating. They do not cover rail faults, pad failure, injected pedal voltage, power sequencing or sustained full-swing faults. The model's extremely low reported distortion is not an audio-quality specification.

Initial shorted runs converged to an invalid operating point: BUF approximately −209.7 V on ±15 V rails and about 2.1 A supply current, then failed near 2.77 ms. Adding `.nodeset v(BUF)=0 v(PORT)=0` guides the initial solution; it does not force those node voltages during analysis. The resulting operating point is approximately 0.50 mV at BUF and 4 mA quiescent supply current. The factory now checks these operating-point bounds and sweep/end-time completion. This numerical sensitivity is retained here rather than presenting the successful rerun as unconditional model robustness.

## Reproduction and next work

Factories: `tools/solver_review.py`, `tools/send_driver.py`. Evidence: `results/solver-review.json`, `results/send-real-summary.json`, exact decks/logs and `results/audit.json`. Run the solver factory, then `--retry-timeouts` to allow 120 seconds for time-limited cases. The standalone SEND factory has a 60-second process bound. Use `RENEGADE_LOOP_INPUT` with the saved component snapshot for replay; source/model hashes and runtime requirements are stated in review.md.

Next: resolve remaining nonlinear cases; assess a physically valid output transformer representation; define a protected high-voltage return candidate and preserve all three transfers (dry, wet and spring excitation). Only then select exact domestically available parts and integrate a readable schematic, connectors, footprint/drill data and routing. Cabinet fit, removable rear wood and actual drill access remain separate release gates. No manufacture-ready claim is supported by this checkpoint.

Human check: compare the voltage scale, incomplete cases and return/mixing consequences before accepting a recovery design. Read the circuit alongside these results, not only the aggregate audit pass.
