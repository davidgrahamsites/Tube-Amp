# RETURN port envelope — 25 November 2026

Owner: electric integration. Status: interface comparison completed; behavior choice open, no native adoption.

Task card: use the current source circuit, generic tube models and reciprocal loaded-transformer fixture to identify the source and load impedances at the existing FX_SEND/FX_RETURN interface. Compare a unilateral buffer with fixed output resistance against native dry, spring-drive and wet transfers before selecting a lower-cost recovery device. Inputs are source-derived; no circuit values or blocks are changed. Outputs are generated port measurements and comparisons under results/return-port-*. The fixture remains an unselected transformer, stiff-supply, nominal-temperature model.

The first done-condition is an independently cross-checked complex port calculation, explicit control/frequency coverage and preserved native hashes. Estimated scope: one interface investigation. Full clean/overload voltage, startup, real transistor, supply, thermal, socket, cable and purchasing qualification remain separate work. Human check: compare the modeled dry/reverb changes with the actual amplifier before choosing the insertion/mixing behavior. No new tube, insertion-point relocation or active mixer is silently adopted.

## What was tested

The current source circuit is loaded through the existing reciprocal transformer fixture:40H primary magnetizing inductance,20mH leakage,250pF lumped primary capacitance,0.2Ω secondary copper,8Ω resistive speaker load and Presence0.5. These are engineering assumptions, not measured magnetics. Supplies remain ideal; generic tube models and the documented fractional-power numerical domain guard are retained. No selected transistor model, tank acoustics or reverb-driver limiter is added.

Thirty-six control combinations: clean/dirty, volume/master fractions0.01/0.25/1, simultaneous tone fractions0/0.5/1 and gain fractions0.1/1. These are electrical fractions, not knob rotation or an audio-taper model. All eight exact frequencies20/40/82.4/200/1000/5000/10000/20000Hz are solved. Controls are not independently exhaustive; no mute/null or nonlinear acceptance claim follows.

Each combination has nine circuit configurations: separated source/load current probes, open-return wet response, native dry/wet responses, and direct buffered dry/wet responses at1kΩ and100kΩ output resistance.324 circuit configurations /2592 single-frequency AC solves complete. All buffered inputs are1MΩ and nominal gain1. Port calculations additionally compare10k/22k/47k/68k/150k/220kΩ output resistances. Each emitted deck is retained and hashed.

The port calculation uses the complex source/load impedance and the transfer from injected return current to the mixer/output nodes. It predicts loaded wet response by superposition, rather than replacing the original preamp with an arbitrary resistor. The direct full-circuit comparisons agree within1.675e−9 relative error across all tested nodes/cases. An independent resistive-network control and a deliberately reversed-sign negative control check the measurement convention. The382-check evidence audit passes and confirms unchanged native board hashes.

## Design consequence

At1kHz the clean source impedance magnitude is36.95–38.32kΩ; the dirty channel is9.90–196.52kΩ across the sampled controls. The following ranges compare each candidate against its matched native baseline. “Dry” is20Hz–20kHz; “wet” uses sampled82.4Hz–5kHz points.

|Fixed return output resistance|Dry-gain change|Wet-gain change|
|---|---|---|
|1kΩ|+0.070 to+2.117dB|−7.501 to−0.636dB|
|47kΩ|−0.876 to+1.290dB|−4.775 to+2.085dB|
|100kΩ|−1.924 to+0.456dB|−2.777 to+4.083dB|
|220kΩ|−3.980 to−1.181dB|−0.157 to+6.703dB|

All eight resistor candidates fail the proposed±0.5dB preservation screen somewhere. This is not a resistor-selection problem alone. At1kHz, native wet-to-PI gain spans6.272dB, while each directly simulated unilateral buffer makes that transfer independent of these upstream controls. Any single control-independent wet transfer, even with an optimally chosen fixed wet-level trim, has at least3.136dB worst-case error against those two native extremes. This bound concerns the stated model/settings; it is not a universal theorem about every compensated loop circuit.

The1kΩ result also changes dry gain by up to2.117dB. Therefore simply telling the user to turn up the REVERB knob would not address the entire difference. Full dry gain, spring excitation and wet mix need calibration if a consistently buffered architecture is chosen. A transistor with sufficient voltage swing cannot by itself fix these loading differences.

## Behavior choice and next work

The user was presented with three behavior directions and asked to see the functional diagrams before choosing (FB-121). [All three diagrams](signal-path-options.md) preserve the insertion region and functional blocks:

1. Recommended investigation: same buffered route in loop and bypass, recalibrated reverb mix. Intentionally changes former passive loading; not an approved circuit.
2. Original passive bypass plus buffered effects route. Retains original bypass as a target, but requires loop-level calibration and can need reverb readjustment when effects are used.
3. Original-behavior preservation through additional compensation. A control/frequency-dependent source characteristic must be addressed; one fixed output resistor/wet trim cannot do it. Feasibility/cost remain unproven.

No option was selected by the diagram request. Continue independent exact-device/source research while awaiting that decision; do not route an assumed option into PCB files. In particular, the commercial LND150 loop precedent has not been shown to preserve this mixer or the required clean/overload envelope. China stock/MOQ/Shanghai delivery, socketing where applicable, thermal and protection qualification are still required before part adoption.

Reproduce with KiCad's NumPy-equipped Python: `tools/return_port_envelope.py`, then `tools/audit_return_ports.py`. Public products are `results/return-port-summary.json`, `return-port-audit.json`, and the two compact CSV comparisons. No procurement or fabrication release.


November 25 follow-up: FB-123 / DEC-016 selects option 1, consistent buffering in effects and bypass modes with reverb recalibration. Earlier choice-pending language above describes the experiment checkpoint; component and circuit qualification remain open.
