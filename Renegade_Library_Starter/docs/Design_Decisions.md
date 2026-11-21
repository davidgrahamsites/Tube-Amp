# Renegade modification — design decisions and open checks

## Agreed direction

Use the uploaded Renegade schematic as the starting design. Revise the whole amplifier's mains-related supplies for **220 V / 50 Hz**, including the separate relay supply. Do not carry forward the original mains fuse values without recalculation. Internal tube heaters, B+, bias and control rails retain their individually required voltages; they do not become 220 V.

Add real spring reverb, provisionally using an additional 12AT7 driver, a correctly specified reverb transformer, the previously discussed long tank, and an additional 12AX7 for recovery/mixing. The proposed shared insertion point is after the effects return and before the phase inverter. Preserve a dry path and mix the recovered wet signal into it. This is an architecture, not a validated circuit.

The exact main transformer is not frozen. Recalculate heater current and B+ requirements after the actual tube use and operating points are established. Also verify rectification, filter-capacitor surge voltage, bias supply and the 50 Hz transformer rating.

## Proposed footswitch interface

The user's “TLR” is provisionally interpreted as **6.35 mm TRS**, not XLR. This assumption needs confirmation before selecting a connector or pedal.

Use two normally-open momentary contacts in a passive pedal:

- Tip-to-sleeve press requests a clean/dirty channel toggle.
- Ring-to-sleeve press requests a reverb on/off toggle.
- Sleeve is the low-voltage control return, not a B+ or mains connection.

The target is a battery-free pedal with state held inside the amplifier. Pedal LEDs, a powered/multiplexed cable protocol, and compatibility with arbitrary existing latching pedals are not part of this baseline. Chassis indicators and local momentary buttons can be included in the circuit design.

## Proposed control circuit

Each switch receives input protection, filtering and a Schmitt-trigger debounce stage. A 74HC14 plus a dual 74HC74 is the provisional hardware approach. Feed each flip-flop's complementary output back to its D input to obtain a toggle on each valid clock edge. Exact RC values, edge polarity, switch loading and supply tolerances are not yet calculated.

A reset/power-good arrangement must establish **clean channel / reverb off** before accepting button events. Reset release must occur after the input debounce states have settled; brownout and power-cycling behavior require testing. Nominal debounce interval target: approximately 20–30 ms, subject to the chosen switch and component tolerances.

Relays and their transistor drivers remain inside the chassis on an isolated low-voltage supply. Include appropriate coil transient suppression and supply decoupling. The footswitch does not directly carry relay-coil current in this proposal.

Reverb on/off should control the low-level wet path without interrupting the tube heater, B+ or driver-transformer primary. The initial target is immediate wet muting; reverb-tail spillover is not specified. Exact mute location and relay contact arrangement remain to be designed.

## Debounce is not pop suppression

Preventing repeated logic toggles does not establish silent audio switching. The analog circuit must separately address DC at switching nodes, charge/discharge paths, relay timing, grounding and any short mute interval needed during a channel change. No pop-free performance is claimed before bench testing.

## Required tests before approving the control design

Check clean power-up, repeated presses, held buttons, both buttons together, switch bounce, power interruption, cable insertion/removal, shorts between jack contacts and operation with no pedal. TRS insertion can momentarily contact other terminals; debounce alone must not be assumed to make hot plugging state-safe. Choose a suitable detect/inhibit approach or explicitly restrict hot plugging after the connector is selected.

Check that reverb muting leaves dry gain stable and that both channels receive reverb at usable levels. Measure/control switching transients on a safe low-voltage prototype before integration into the high-voltage amplifier.

## Scope of this archive

Only library registration and generic component symbols are implemented. None of the control circuit, amplifier wiring or mains design described above is implemented in the preview schematic.
