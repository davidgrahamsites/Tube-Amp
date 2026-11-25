# K3 coil decay and native gate-resistor boundary

Owner: control-switching integration. Input revision1fe6f48. This checkpoint determines whether the proposed driver inhibit can be treated as immediate contact muting. It cannot. The output is a diagnostic model and an explicit native-change requirement, not a new relay or released circuit. Runtime is seconds with a30s limit per SPICE subprocess; actual contact/temperature measurements remain human evidence.

## Native interface correction

R341 remains **1kΩ** in circuit.json,09b_latches_drivers.kicad_sch and Renegade_Control.kicad_pcb. The rail-inhibit candidate requires a proposed **4.7kΩ** value. Earlier buffered-review wording incorrectly implied that4.7k was already present; it is corrected. The delay factory now reads all three native representations and records their hashes. It stops if their declared current values disagree.

With the proposed base-current allocations, retaining native1k gives a forced collector/base current ratio41.41, exceeding the candidate limit10. The4.7k proposal gives8.81. This is a design condition, not a transistor guarantee. No native resistor, net, footprint or route changed. Sourceable parts and native preservation/ERC/DRC remain prerequisites to adoption.

## Coil energy diagnostic

The [Omron G5V-2 datasheet](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v2.pdf), page2, identifies the H1 DC12 coil as960Ω with2.90/3.99H reference inductances. Those inductances are not guaranteed bounds or a moving-armature model. The sheet's3ms release specification cannot be used as a guaranteed delay for this externally diode-clamped circuit. The5%-of-initial-current metric below is also not its release-voltage test or a contact-position estimate.

The48-case calculation uses the existing coil resistance tolerance and copper temperature approximation over−25/23/70°C,11.4–12.6V, the two reference inductances, and an engineering0.5–1.1V diode clamp range. It assumes the analog fault occurs while the12V relay supply remains healthy. With the driver off:

`L di/dt = -R i - Vclamp`, until current reaches zero.

| Time after driver-off | Remaining coil current, fraction of initial |
|---|---:|
|0.1ms|95.37–98.19%|
|0.5ms|78.73–91.26%|
|1ms|61.58–83.25%|
|2ms|36.62–69.20%|
|5ms|3.03–39.22%|

Conditional decay to5% is4.666–13.947ms. This supports one conclusion: stored coil energy cannot be ignored when evaluating rapid faults. It does **not** prove when the contacts open or close.

Two corresponding SPICE coil/driver cases and two finer-step runs retain the local and remote flyback diodes and100µH/0.2Ω harness surrogate. The model uses a Level1 MOSFET, generic27°C diodes, typical capacitances and an immediate100ns command through100Ω. It is not an exact AO3400A, NPN or HC14 model. Changing the coil resistance temperature does not change the generic semiconductor temperature. Both cases hold the command OFF throughout the observation; they do not simulate successful re-enable.

The completed1ms samples retain62.80% and82.94% current. Fine-step sampled fractions differ by at most0.00000524, and drain peaks by less than7µV. These are numerical agreement metrics, not hardware accuracy. Small negative currents after decay arise from the parasitic network and are retained without clipping in SPICE evidence.

## Retained solver limitation

An earlier ideal-gate-source diagnostic fails at15.0001ms when the gate command is restored after a5ms off interval. Its exact deck, incomplete duration and simulator log are retained in results/relay-latency.json. Adding gate impedance/capacitance allows all eight coarse restore cases to finish, but the selected cold-coil0.1ms case exceeds the30s subprocess limit at the finer step. Its timeout, parameters and factory provenance remain recorded; no missing waveform is fabricated. The primary decay screen therefore asks only the turn-off question; this change in scope is explicit. No failed re-enable run is presented as a passing whole-circuit result.

The separate results/rail-delay-budget.json still retains failed brief-fault hold behavior. Combining two conditional screens cannot qualify the complete comparator/reset/driver/audio circuit.

## Decision and next work

Do not count K3 as an instantaneous rail-fault mute. Keep its final wet-node grounding function and evaluate the audio disturbance during the interval before its contacts move. Before adding a hold latch or fast audio clamp, establish the amplitude/duration requirement with the actual supply paths and protected expression output. A timer alone cannot remove the initial mechanical response interval. Re-enable, simultaneous supply loss, exact part temperature limits and real contact behavior remain unresolved.

Reproduce: `python3 engineering/whole-amp/control-switching/tools/rail_delay_budget.py`, then run tools/relay_latency.py with the KiCad Python runtime. Contracts own candidate parameters; factories write only results. Native CAD and functional blocks are unchanged, and sourcing/three-board populated fit/drill-access gates remain open. No fabrication or purchasing release.

Human check: measure coil current and both K3 contact states with the actual flyback diodes and harness during rail-loss/recovery; compare the resulting wet-output transient with a stated audio limit.
