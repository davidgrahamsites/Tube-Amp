# Low-frequency reference check — November12

## Fault found
The earlier transformer model used assumed inductance and coupling. It produced ringing near412kHz. The ringing remained with the active reverb removed. Changing coupling from0.999 to0.995 moved it to172kHz; changing to0.9995 moved it to584kHz. These are unverified transformer parameters. They cannot stand in for the transformer we buy. See ../candidate-hf/coupling-comparison.json.

## Test setup
A separate reference model now uses an ideal centre-tapped transformer with7.6k:8ohm impedance ratio and the existing100ohm winding resistors. It has no leakage inductance, winding capacitance, core saturation or magnetizing current. It is useful for low-frequency circuit checks only. It cannot clear real-transformer stability, bass response, heating or output power.

Three independent checks at50Hz,1kHz and20kHz passed turns ratio, reflected impedance and power balance. See fixture-qualification.json and tools/check_ideal_transformer_fixture.py. This proves the ideal test fixture's arithmetic, not a physical transformer.

The circuit under test retains the proposed passive dry path, attenuated reverb send, clamp protection and4.7k screen resistors. Tube and TI opamp models are unchanged. Supply remains an ideal400V B+,-40V bias and±15V rails. Input is200mV peak at1kHz on the dirty channel. Wet signal is zero/muted. No native schematic or PCB change has been made.

## Results
- A1µs-step trial stopped early. Failed result retained.
- At200ns maximum step, the5ms run completed. Repeating at100ns changed mix peak by0.00550%,screen power by less than0.00047%,and ideal load power by0.00014%. See step-sensitivity.json. This agreement applies to that5ms comparison only.
- The200ns run then completed80ms with400771 points. See200n-80m.json/.cir/.raw/.log.
- Last5ms average screen dissipation:4.173/4.223W. Screen resistor dissipation:4.363/4.378W. Plate dissipation:6.430/6.530W, computed from the unchanged model's conductive plate-current expression.
- Peak reverb input:1.459V. Peak passive-mix signal:13.505V. These are full-run peaks in this reference model.
- Last5ms average B+ current:225.77mA. Ideal8ohm load power:47.29W. Neither number qualifies a real transformer or establishes amplifier output power. They do show why the old173mA PT and25W OT references cannot be accepted without further checks.

## Work still open
Obtain real PT/OT data: loaded/no-load voltages, regulation, current and thermal ratings, winding resistance, turns ratio, phase, primary inductance, leakage inductance and winding capacitance where available. Run high-line/low-bias/tolerance/startup/long-duration checks. Check the actual spring tank and rail behavior. Verify real hardware with appropriate bench procedures. The existing generic tube models also require correlation with the chosen tubes.

The low-frequency reference does not repair or replace the unresolved real-transformer high-frequency model. Keep both sets of evidence. Do not hide the ringing with arbitrary damping parts or report a fabrication release.

Waveform files ideal-transformer-headroom.png/.pdf show the final5ms of the actual saved run. Scripts are under engineering/whole-amp/tools/.
