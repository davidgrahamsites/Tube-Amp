> November 20 photo update: model and second marking are now photograph-confirmed; socket labels and meter-specific steps are in [received photo intake](received-tank-photo-intake-2026-11-20.md). Earlier requests below for a label photograph are closed. DC coil readings have since been supplied; see tank_received.electrical_measurements in ../fit-register.json. AC and current qualification remain pending.

# Received tank: measurements, equipment and limits

Owner: electrical integration; human bench operator performs measurements. Date2026-11-20. Status: proposed procedure, not executed. Unit: M8EB2C1B / R2610270015, as transcribed by user. Canonical results belong in ../fit-register.json under tank_received.electrical_measurements. No measurements are created by this plan.

## What can be established
DC resistance is directly measurable. AC impedance can be measured under explicit chosen conditions; this does not recover the supplier's undocumented original test conditions. Recommended current and guaranteed maximum current are manufacturer design/qualification ratings, not values a multimeter can discover. Bench testing can establish a conservative operating point for this particular sample, not a production-wide maximum or long-term life rating. Do not test to failure to find a limit.

## Equipment by task
1. DC coils: ordinary digital multimeter with ohms ranges covering tens of ohms through several kilohms; leads or RCA breakout adapters. Do not use an insulation tester/megohmmeter. Tank disconnected from all other equipment.
2. AC impedance: LCR meter/impedance analyzer offering1kHz, a documented low AC test level and impedance magnitude/phase (or valid series-R/L measurements). A basic multimeter's capacitance or resistance mode is insufficient. Open/short compensate the test leads per its manual. This is a capability requirement, not a recommendation to buy an expensive laboratory instrument.
3. Alternative AC setup and drive characterization: clean sine generator, two-channel oscilloscope with waveform subtraction, known1% non-inductive series resistor, leads/RCA adapters; suitable low-voltage audio driver where generator drive is insufficient. For wet-output compression/distortion, add a high-impedance low-noise recovery preamp and FFT/audio analyzer or properly configured audio interface. Check the preamp/interface headroom so its clipping is not blamed on the tank. Disable phantom power; never feed tank output into a powered microphone input without the appropriate interface.

## First measurement: DC resistance
Disconnect both RCA jacks from everything. Put meter leads in COM and V/ohms sockets, select ohms, and check the shorted-lead reading. Measure between the centre contact and outer shell of the INPUT jack; record the stable reading. Repeat on OUTPUT. Use each jack's own shell, not the metal tank case, because input shell is specified as insulated. Record meter model, room temperature if available, displayed units/range and reading. These are DC resistance values and need not equal the nominal600/2250ohm AC impedances.

## Proposed AC conditions (not Mable's published conditions)
Begin at1kHz sine, zero DC bias, with low excitation; propose50mVrms at the winding for an LCR meter after checking its actual level/current monitor. Use the lowest stable suitable level and record actual applied level. Nominal50mV/600ohm is about83microamps, but actual current depends on measured impedance. If using a series-resistor fixture, a100mVrms source through1kohm bounds current to about0.1mArms for a passive coil; this is an intentionally low-level characterization proposal, not a manufacturer-approved test specification. Generator amplitude settings must account for its50ohm/Hi-Z display convention and be verified with the scope.

Measure each coil separately with the opposite jack open. Mount/support the tank in its specified horizontal, open-side-down orientation without contacting or restraining the springs. Note temperature, mounting, other-jack termination, frequency, actual RMS voltage/current, model/range, lead compensation and repeatability. Begin at1kHz; use low-level frequency sweeps/points across the intended audio band to build a better model. Do not leave a constant-voltage setting unexamined at low frequency, where impedance can be much lower.

## Two-channel fixture detail for a qualified operator
Connect generator HOT -> known series resistor -> tested coil centre; tested coil shell -> generator RETURN. CH1 tip goes to generator HOT, CH2 tip to tested coil centre. Both ordinary earth-referenced scope ground clips go to the same generator RETURN. Do not put a ground clip on the resistor's high side, float protective earth or connect to an energized amplifier.

The resistor voltage waveform is CH1 minus CH2. Current waveform is that difference divided by the measured series resistance. Compute impedance as the complex ratio of coil voltage to current; magnitude alone is Vcoil_rms / Icoil_rms. Subtract the waveforms/phasors, not their RMS magnitudes, because the coil introduces phase shift. This fixture is for the isolated low-voltage tank only.

## Working drive level versus maximum rating
Factory engineering data tied to the actual winding/part revision is the route to a manufacturer-rated recommended/maximum current. Another generic8EB2C1B chart is not adequate. Do not make another repeated supplier request the sole critical path.

Once low-level coil data are known, qualify the adjustable driver on the actual sample using small initial signals, measured input current and an independently unclipped recovery chain. Check several frequencies and guitar-like signals for compression, distortion and mechanical behavior. Choose a working level with margin below unacceptable behavior and verify prolonged use/temperature as part of the prototype plan. The exact current limit and acceptance criteria remain to be set from evidence; audible saturation is not a guaranteed safe maximum. The historical3.1mA Accutronics reference is not a certified Mable maximum. No destructive maximum-current search is proposed.

## Evidence
- [Fluke resistance measurement procedure](https://www.fluke.com/en-gb/learn/blog/digital-multimeters/how-to-measure-resistance): isolate/remove power for resistance measurements and account for test leads.
- [Hioki IM3536 instrument specifications](https://www.hioki.com/global/products/lcr-meters/10-mhz/id_6057): frequency and test-level control are distinct impedance-measurement conditions. Reference for capabilities, not a purchase selection.
- [MOD manufacturer tank specification table](https://www.modelectronics.com/reverb-tanks/sound-samples-product-info): its impedance values are specified at1kHz; this supports a conventional reference frequency, not proof of Mable's conditions.
- ../evidence/accutronics-reference.pdf: historical manufacturer reference only. Actual Mable documentation limits are in tank-specifications.md.

## Next human check
Inventory equipment already available and take the two unpowered DC resistance readings first. Borrow/use a competent electronics bench for the AC and drive characterization if appropriate; do not purchase the full list solely for these first checks. Update actual readings and conditions in the fit register, retaining the difference between measured facts and chosen test assumptions.

## Clarifications during the November20 rerun
The user asked which decisions AC impedance affects: driver current/voltage capacity and supply headroom; series resistance and stability isolation; coupling capacitor/send filtering; recovery loading/noise; and the coil model used for simulation. Impedance alone does not give acoustic transfer gain, decay quality or the useful wet-knob range. Audio testing is still required.

Copper heat uses approximately I_RMS squared times measured DC resistance. With76ohm input,3mA gives0.684mW,10mA7.6mW,30mA68.4mW. These illustrative powers are not safe-current ratings: winding thermal resistance, wire/insulation temperature ratings, ambient and losses are unknown. Magnetic/mechanical distortion may occur before thermal damage. The model must not label its maximum simulated current a safe tank limit.
