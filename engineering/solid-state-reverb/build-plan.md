# One-combo build plan — original Renegade plus solid-state spring reverb

Revision 0.4, 2026-11-11. Build one working prototype in the preferred Mable 5E3 shell before any repeat units. This is the assembly and test sequence for the engineering package; the unresolved parts below prevent treating it as an instruction to energize the current draft.

## 1. Close the concrete design gaps before ordering or drilling

Use `bom.csv`, `source-delta.md`, the integrated schematic, and `pcb/design-rules.md` together. Source amplifier uses four 12AX7 and two EL34; there are no added reverb tubes or transformer. Keep the original cabinet appearance, 12-inch combo format, Shanghai sourcing and front/top operating controls.

Resolve these specific items:

1. Confirm Mable's exact stocked shell matches its recovered dimension drawings, including 312mm opening, supports and materials. Obtain a domestic Shanghai quote; no order or supplier message has been sent.
2. Select the speaker and custom chassis against the real internal envelope. Verify speaker depth, transformer/choke bodies, six tube envelopes/retainers, ventilation and service access. Proof a full-size layout in the cabinet. The 160 x 100mm board outline alone is not fit approval.
3. Select exact T1/T2/L1/T3 suppliers and lead maps. T1 reference is 372FX, not the old 115V/60Hz 272FX. All mains branches are 220V/50Hz. Match secondary requirements and actual regulation/current/insulation behavior; do not equate a secondary AC current rating to available filtered DC current without analysis.
4. Close F1/F2 and S2 ratings: fuse time-current/inrush and breaking capacity; exact HVDC standby switch interruption rating. These three entries are explicitly blocked in the BOM. A 250VAC switch is not a 600VDC switch.
5. Qualify the source 220k EL34 grid returns for the exact selected tubes; verify bias range across line/temperature and the actual operating point. Complete nonlinear tube/transformer and integrated supply simulations under the earlier selected-component requirement.
6. Confirm the real 8EB2C1B tank and its connector grounding/mounting, China stock and permissible drive. Tank selection remains conditional; never substitute an 8-ohm input tank.
7. Match every capacitor body/lead drawing and connector to the board footprints. Select actual panel-pot shaft/bushing and knob parts. Inspect datasheet pin numbering from the correct view. Export new checked files if any footprint changes.

## 2. Mechanical arrangement

Use a custom chassis that fits the existing shell, not a stock 5E3 three-knob chassis by assumption. The original nine operating knobs are clean treble/bass/volume, dirty gain/treble/bass/mid/master, and presence. Add REVERB for ten total. Bias and SEND stay internal. Consider two control rows within the 312mm opening; prove hand access, pot bodies and shields on a full-size print before committing hole centers.

Keep power entry, primary wiring and the HV supply together and physically separate from input/recovery wiring. Mount transformers/choke to adequate chassis structure and test magnetic orientation before final holes. Mount tube sockets to the chassis; fit grid and screen resistors at the appropriate socket pins. Twist heater pairs and keep them away from input grids and tank recovery. Reserve safe service clearance around hot valves/resistors and discharge points.

Mount the tank in its specified horizontal/open-side-down orientation in a bag with resilient hardware. Position it away from power magnetics. Its case connection through the output shell must not introduce an unintended second signal/chassis bond. Secure shielded send/return cables and identify both ends.

## 3. Build and verify the low-voltage module first

The finished layout is **the reverb daughterboard**. The main tube stages remain chassis/turret wired; the controller and isolated secondary supply have native schematics but no routed PCB in this package.

Fabricate only after the part-envelope and fit gates above close. Board specification: 160 x 100mm, 2 layers, 1.6mm FR-4, 1oz copper, solder mask both sides, four 3.2mm nonplated holes. Use the matching Gerber/drill revision and compare the manufacturing viewer against the native board. Do not merge NPTH/PTH files casually.

Populate low parts first, then capacitors, trimmer, headers, relay and optional DIP sockets. Verify every resistor before installation, semiconductor orientation, IC notch/pin 1, electrolytic polarity and solder bridges. C603/C606/C607 are nonpolar film parts. C617 positive goes to ground and negative to -15V. Clean flux around the high-impedance input/recovery nodes. Use insulated standoffs and retained harnesses.

Before connecting to the amplifier, use a current-limited isolated bench supply at +/-15V. Keep +12V relay supply separately current limited. Start with op-amps removed if sockets are fitted, verify rails at pins 8/4, then power down and fit ICs. Investigate unexpected current rather than raising the limit. Expected op-amp quiescent current is approximately 24mA per rail for six sections using the 4mA/channel typical figure; allow for the actual datasheet maximum, output loads and tolerances. K3 high-sensitivity coil is approximately 12.5mA at 12V.

Apply 1kHz, 100mVrms through a representative 100k source. With tank disconnected and REVERB zero, measure output approximately 0.98 times the source in the modeled fixture; a low-impedance generator gives approximately 0.99. Sweep 82Hz–5kHz and confirm no unexpected gain rise/oscillation. Vary the REVERB knob and relay state; dry amplitude should remain within a proposed 0.1dB band. This is a prototype acceptance target, not a claimed measurement.

Inject 1mVrms electrically at the tank-return interface to check recovery/mix. Maximum wet nominal midband gain is about 90, including the wet series/mix resistors; actual tank output is not specified by this injection test. Check zero-knob residual, clipping, DC offsets and switch pops. Raise signal levels cautiously to establish the actual headroom; the +/-15V op-amps cannot reproduce arbitrary tube-preamp peaks. The design target is <=10V peak internal/output signal, with margin verified against actual loading.

Connect the tank, start SEND at minimum, and increase it while observing input current, driver waveform and clean decay. Establish maximum drive from the actual tank specification and measured behavior; do not use an invented universal coil-current limit. Test open/shorted cables under a current-limited setup, tank orientation, hum and acoustic feedback. The electrical surrogate simulation does not predict these effects.

## 4. Supply, controller and chassis wiring

Construct the isolated 18-0-18V secondary supply and regulator assembly with rated mounting/insulation; do not use a solderless breadboard in the final amplifier. Verify 7815/7915 pinouts and isolate the 7915 negative-input tab from any grounded/shared heatsink. Keep rectifier/reservoir charging currents separate from audio returns. Test +/-15V, +12V and +5V regulation and temperatures at the actual loads and required line cases before attaching the audio board.

Assemble and test the existing Schmitt/debounced toggle controller at low voltage. Verify reset to clean/reverb-off, one transition per press, long holds, simultaneous presses and power dips. Verify actual relay contact mapping with a meter. Connect the TRS pedal only with power off until a hot-plug inhibit design is qualified. Footswitch reverb off is an immediate wet mute; tails are not retained.

Harness schedule, component-side connector numbering:

| Connector | Pins in numeric order | Destination |
|---|---|---|
| JR1 | 1 FX_RETURN, 2 GND | Normalled effects-return output |
| JR2 | 1 TANK_IN, 2 GND | Tank insulated input RCA |
| JR3 | 1 TANK_OUT, 2 GND | Tank output RCA/shield |
| JR4 | 1 WET_TOP, 2 WET_W, 3 GND | Panel REVERB pot: CW end, wiper, CCW end; verify physical lug convention |
| JR5 | 1 MIX_OUT, 2 GND | Original C19/R24 phase-inverter input |
| JR6 | 1 +15V, 2 GND, 3 -15V, 4 +12V, 5 COIL_REV | Isolated supply and controller Q2 drain |

Do not fit R100. Keep C19/R24 and the source phase-inverter network. Follow the source-delta table for supply/bias changes. Heater load is 4.2A plus pilot, versus the 5A reference winding; verify voltage at every socket under load. Do not ground a real heater center tap while also using the elevated artificial center tap.

Bond protective earth directly to a dedicated locked chassis stud and all required exposed metal. Keep PE independent of PCB ground, removable signal connectors and signal-return routing. Maintain one deliberate audio-common/chassis connection. Verify the actual assembly's protective measures, insulation and conductor routing with a competent mains/HV reviewer before power is applied.

## 5. Main amplifier commissioning — after review gates close

Use appropriately rated probes, meters, an isolated signal source and a correctly rated dummy load. A variac is not an isolation transformer. Discharge and measure every reservoir/filter node before touching wiring; never rely only on elapsed time or fitted bleeders. No live adjustments by an unqualified builder.

Have the reviewed test procedure establish: unpowered wiring/earth checks; current-limited staged supply tests; verified negative bias present before output-tube conduction; maximum-negative starting setting; heater and cathode-follower heater/cathode voltages; rail ripple, plate/screen voltages and individual cathode current. Derive target idle current from actual plate/screen voltages, tube limits and operating point, rather than a universal mA number. Investigate red plating, unexpected current, oscillation or bias drift immediately.

Verify output-transformer winding phasing and negative-feedback stability at low level into a dummy load before increasing drive. Confirm the selector matches the load and is changed only with power off. Measure clean output power, distortion onset, frequency response, noise, current and temperatures. The 25W transformer rating is not proof of 25W amplifier output.

Required line cases remain 198/220/235.4V at 50Hz; treat 242V as extra stress, not the normal upper bound. Run these only under a qualified procedure with rated equipment. Verify bias/screen/filter/switch/fuse and thermal margins against selected-part limits. Preserve failed results and corrections.

## 6. In-cabinet acceptance

Install the tested assemblies and repeat hum, microphonics, reverb feedback, mechanical rattle, switching-pop, cable retention and thermal tests at intended use levels. Check that controls remain accessible and hot parts cannot damage wiring/cabinet/tank. Record unit identity, BOM/board revisions, exact parts, setup, measurements and photographs. Only after one complete combo passes should the five-unit plan be revisited.
