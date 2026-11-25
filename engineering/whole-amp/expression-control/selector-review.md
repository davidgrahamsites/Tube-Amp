# PANEL / EXPRESSION selector review — 25 November 2026

Owner: expression-control. Inputs: FB-124/125, requirements.md and current reverb-600/circuit.json. Output: interface proposal, not a released circuit or purchasing recommendation.

## Verified existing interface

RV602 is `100k LOG REVERB`, with ends WET_TOP/GND and wiper WET_W. It carries recovered wet audio. Replacing it remotely with another 100k pot requires matching taper, travel and wiring as well as resistance, and sends audio through the pedal cable. Cable capacitance and interference would become part of the wet audio path. The standing low-voltage-only pedal requirement rules out adopting that direct extension without an explicit change.

## Proposed implementation

Keep wet audio and its gain-control element on the reverb board. Use the panel knob and passive pedal to produce protected low-voltage control signals; a maintained two-position ON–ON toggle selects PANEL or EXPRESSION. Exact poles and low-current contact specification depend on the circuit; the photograph cannot establish these. Route panel wiring through connectors.

Matching panel and pedal resistance is possible but is not necessary for a buffered voltage-divider control interface. Choose resistance, linear/logarithmic response and gain mapping together. A common linear-pot pedal with a suitable internal response law may be easier to source than a 100k logarithmic pedal. No pedal value or part is selected here.

PANEL uses the knob. Proposed EXPRESSION behavior uses the pedal independently over the calibrated wet range, replacing the older knob-as-maximum relationship. Dry gain remains constant; heel is dry and toe is calibrated maximum wet. Unplugged operation returns smoothly to panel control. Reverb-off overrides either control. Open wiper/cable faults must not command uncontrolled maximum wet.

Debounce addresses repeated contact transitions. A separate smoothing/ramp strategy addresses differing knob/pedal positions and control feedthrough; debounce alone does not establish click-free audio. Validate switch and jack hot-plug behavior, shorts, startup, travel response, wet noise/distortion/headroom and dry invariance before claiming success.

## Primary references and limits

- [BOSS EV-30](https://www.boss.info/global/products/ev-30/) documents TRS outputs, polarity switching and range adjustment: expression compatibility includes wiring and range, not just resistance. Reference example only; no sourcing or selection claim.
- [Analog Devices, Selecting the Right CMOS Analog Switch](https://www.analog.com/en/resources/design-notes/selecting-the-right-cmos-analog-switch.html) explains switching charge injection and click/pop issues. Supports separating transition artifacts from contact debounce; does not qualify a selected control circuit.

Human check: confirm the desired control behavior; after implementation, compare panel and pedal sweeps and operate the toggle with deliberately different settings while listening/measuring for transients. Exact China-stocked parts, Shanghai delivery, dimensions and native integration remain pending.

Implementation follow-up: [protected pedal-port proposal](pedal-port-design.md) defines states, board ownership, preliminary current/range budget, unavoidable tip/ring fault ambiguity and exact-jack candidates. This remains outside native CAD; domestic Shanghai sourcing and device-level protection are unqualified.
