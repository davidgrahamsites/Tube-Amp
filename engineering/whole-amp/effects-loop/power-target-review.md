# Approximately 25 W reference — 24 November 2026

Owner: electrical integration. T04 remains active. This is a reproducible nominal model result, not a physical amplifier rating or a selected RETURN circuit.

## Task and evidence

Input: FB-109 approximately 25 W target, existing source-derived full-amplifier fixture, unchanged circuit contract and generic tube models. Output: ten drive points plus a near-target pair at different time steps. Done-condition for this pass: retained full-window results, deck/source consistency, settling and numerical sensitivity checks. Physical magnetics, mains corners and bench correlation remain dependencies for closing T04. No native schematic, board, component selection or geometry changed.

Run `python3 engineering/whole-amp/effects-loop/tools/power_target.py` for the base sweep, `--refine` once for its four added drive points, and `--target-check` for the separate near-target comparison. Run `tools/audit_power_target.py` from this module's path to check the retained evidence. Each solver case has a 60-second limit and retains an explicit failure status. Products are overwritten in place; no growing copies.

All twelve runs completed the full 0.5 seconds. The [audit](results/power-target-audit.json) passes 66 checks covering current circuit/model hashes, regenerated decks, saved summary consistency, finite values, settling, numerical refinement and retained fabrication holds. Spectrum uses the final ten cycles and harmonics 2–10. Fundamental load power is fundamental peak voltage squared divided by twice the 8-ohm load; it is not total distorted-waveform RMS power.

## Results

Common conditions: clean channel, volume fraction 1, tone/gain fractions 0.5, 1 kHz sine, nominal stiff 400 V main / 380 V screen / −40 V bias / 278 V early / 313 V preamp rails. Pot fractions describe electrical division, not physical knob rotation. Transformer reference is ideal 7.6k:8 with assumed 100-ohm resistance per primary half.

| Input peak | Fundamental output | Speaker THD, harmonics 2–10 | Internal FX_SEND peak, approximately |
|---|---:|---:|---:|
| 5 mV | 14.46 W | 0.473% | 2.29 V |
| 6 mV | 20.53 W | 0.739% | 2.74 V |
| 6.72 mV, refined | 25.002 W | 1.767% | 3.07 V |
| 7 mV | 26.71 W | 2.318% | 3.20 V |
| 8 mV | 32.22 W | 4.768% | 3.66 V |
| 10 mV | 39.60 W | 10.057% | 4.57 V |

The near-target coarse run was 25.019 W / 1.770% THD. Halving the maximum time step changed the checked fundamental amplitudes by at most 0.0452% and THD by at most 0.00349 percentage points. This supports numerical repeatability only. The sampled high-drive 1% crossing is bracketed by 20.53 and 25.002 W; the 5% crossing by 32.22 and 39.60 W. Neither is an exact threshold. THD is non-monotonic at low drive, so no single global 1% crossing is claimed. The target is not yet demonstrated at 1% THD.

## Consequences for the loop

The approximately 3.07 V peak at nominal 25 W is an internal node, not a released jack level. Earlier roughly 135 V peaks arose in deep overload. Those peaks remain protection/recovery cases; they must not silently set the normal clean requirement. Equally, one clean-channel point cannot justify adopting a low-voltage RETURN. Dirty-channel operation, all relevant control positions, spring-send/mix loading, startup and recovery remain to check. Existing low-impedance buffer experiments change wet level, so headroom alone is insufficient. Do not adopt the costly three-OPA462 bootstrap or silently relocate the loop.

## Model defect and next action

The present controlled-source transformer transfers DC mathematically: this sweep reports about 0.123 V secondary DC near target and up to 2.66 V in overload. That is not a credible steady-state secondary-DC prediction for a real transformer. The abstraction also lacks magnetizing inductance, leakage, capacitance, core saturation and physical losses. Its finite output power and stable solver are not proof of adequate magnetics or stability. Preserve these results as a reference while replacing/qualifying that abstraction.

Next T04 step: separate actual transformer data from assumed parameters, implement and check a coupled-winding model with winding polarity/DC behavior verified, and quantify sensitivity before using it to select circuitry. Missing inductance/leakage/core data must remain explicit; arbitrary parameter choices cannot qualify a component. Then repeat relevant frequency, channel/control, supply/load and overload cases, including physical-parameter uncertainty. Final 120/220 V corners depend on the selected supply's regulation and load budget.

The original [Hammond 1650F](https://www.hammfg.com/part/1650F) is rated 25 W, 7.6k centre-tapped, with 4/8/16-ohm secondary options. That product rating does not rate this amp. The [372FX](https://www.hammfg.com/part/372FX) documents 120/220 V taps and 50/60 Hz operation, but is only a reference: its 150 VA and winding ratings must be assessed against the full load budget, actual fit and China availability before selection. These pages were checked November 24; they do not supply a complete nonlinear transformer model or domestic quote.

## Human check

Before declaring output power, measure the actual amplifier into a known load at stated frequency, supply and distortion, and record tube/screen/transformer stress. Continue all existing cabinet, independent-back-removal, drill-access, grounding and fabrication gates.
