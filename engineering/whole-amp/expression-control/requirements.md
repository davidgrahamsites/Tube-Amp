# Reverb expression pedal — agreed operation

User confirmed November12,2026. Owner: current Codex chat. Status: requirements recorded; circuit, exact parts and PCB work not yet implemented.

## Latest selector request — 25 November 2026

FB-124/125 now require a PANEL / EXPRESSION toggle. See [selector review](selector-review.md) and DEC-016. The newer replacement wording suggests independent pedal control; the older knob-as-maximum law below is historical pending resolution of that interpretation. Protected low-voltage cable, constant dry, fault handling and separate on/off remain required. No native implementation yet.

## Current selector design targets

- A passive rocker pedal with a potentiometer controls wet/reverb level only.
- Heel down: dry only.
- PANEL selects the faceplate knob. EXPRESSION selects the pedal; toe reaches calibrated maximum wet. Independent pedal range is the stated interpretation of the latest replacement wording, superseding the older knob-as-maximum proposal.
- Pedal unplugged: faceplate REVERB knob works normally.
- Dry gain stays constant throughout pedal movement.
- Keep audio inside the amplifier. The pedal cable carries only a protected low-voltage control signal and its return.
- Preserve the existing channel/reverb on-off footswitch. Use a separate expression connection, clearly marked REVERB EXP. Do not silently repurpose the existing footswitch jack.
- Existing reverb-off command still overrides wet level. Existing immediate wet-mute behavior remains unless separately changed.

Current design relationship: wet output = recovered wet signal × selected control factor × reverb-enable state. The factor comes from the knob in PANEL mode and from the pedal in EXPRESSION mode. Unplugged selects the panel factor with a smooth transition. This is a functional target, not a selected electrical control law. The older multiplicative knob-times-pedal behavior is retained in DEC-007 as history.

## Work order

Inputs: v0.5 routed draft boards; current reverb headroom/transformer-model findings; selected-part register; confirmed user behavior above.
Outputs: wet-only gain-control circuit; protected pedal port; exact pedal pot/jack/cable/control parts; power/load budget; schematic and BOM changes; native PCB/harness/panel updates; repeatable tests.
Dependencies: choose the control method before fixing pedal resistance, taper, TRS wiring or voltage. Pedals are not universally interchangeable. Received tank is seller-confirmed600/2250ohm. Actual drive limit/coil behavior and physical dimensions still need characterization; do not make another datasheet request the sole dependency.

Proceed with a passive linear-pot pedal as the design direction. Pot resistance, contact arrangement and connector pinout are not yet selected. Do not issue a pedal purchase recommendation from this requirement alone. Wet gain may use a suitable analog control element driven by the pedal voltage; choose against noise, distortion, signal range, control feedthrough, cost and China availability. No added tube stage.

## Checks before release

1. Verify both endpoints and smooth, monotonic travel. Faceplate zero must give dry only in PANEL mode; heel must give dry only in EXPRESSION mode.
2. Measure dry gain with heel/toe/intermediate positions, reverb mute and pedal unplugged. Retain the proposed0.1dB dry-level acceptance band; it is not a measured result.
3. Test insertion/removal at every pedal position. Restore faceplate operation without a sharp level step or pop. Define and test the control ramp/filter.
4. Test open wiper, broken cable and each jack-contact short. Current-limit/protect the reference output. A plugged-in faulty control cable should not command an uncontrolled wet-level jump. Distinguish a real unplug from a broken wiper.
5. Test mains/control-supply startup, reset and power dips. Existing clean/reverb-off startup remains required.
6. Check actual pedal resistance/taper/pin map, end resistance, cable capacitance and connector switching sequence. Use a real pedal for final travel and hot-plug checks.
7. Check control-element headroom/noise/distortion and rail loading. Repeat wet/dry simulations and native netlist/ERC/DRC after integrating changes.
8. Add the dedicated jack and its clearance to the chassis layout and harness schedule. Cabinet and tank are delivered; actual clearances and populated assembly fit remain to check.

Done condition: exact sourced parts, checked circuitry and native files, and a written bench test with remaining physical checks stated. This file alone does not make the current PCB support an expression pedal.
