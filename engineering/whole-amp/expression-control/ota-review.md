# Wet gain-cell candidate — 25 November 2026

Owner: expression-control. Status: standalone candidate tested; not selected or integrated.

## Task card

Inputs: DEC-016, selector-review.md, the existing 100k audio reverb control, TI LM13700 SNOM267 and the retained TI OPAx134 model. Outputs: reproducible gain-cell factory, retained decks/results, source observation and evidence audit. This bounded investigation selects the next circuit work; it does not finish the pedal controller. Estimated effort: one circuit-screen checkpoint. Human evidence remains necessary for noise, stability, device spread, pedal behavior and actual fit.

## Candidate and measured model behavior

The candidate would replace the audio potentiometer/buffer function with a wet-only OTA and transimpedance stage, leaving dry outside the control element. A 100k input resistor, 1k input return resistors, 215k feedback and 10p feedback capacitor are screening values. Ideal 1mA diode bias and 0–500µA amplifier bias isolate the gain cell from its yet-unbuilt controller. A physical 100k trimmer across ±15V, feeding the positive input through 470k, compensates nominal control feedthrough. It is an internal setup trim, not the panel knob or pedal.

Twenty-nine cases were retained: 28 complete, while the ±12V/8Vpeak transient hits its 40-second bound. Nine nominal ±15V audio cases cover 0.1/1/10Vpeak at 100/1000/10000Hz. Gain is 0.9939–1.0027; maximum computed second-through-ninth harmonic THD is 0.05628%. These amplitudes are a candidate screening range, not measured spring output or whole-amp headroom. Halving the 10kHz timestep changes gain by 0.003565%; changing numerical shunts from 1e12Ω to 1e11/1e13Ω changes the checked 1kHz gain by less than 0.0001%.

With trim at its midpoint, changing amplifier bias produces 1.22185V of output DC movement in the nominal model. Calibrating once at full gain reduces the sampled bias-dependent spread to 3.181mV. Keeping that trim at 0°C and 70°C gives approximately +5.715mV and −9.105mV output DC. This is still sufficient reason to design AC coupling and smooth control changes; these tests do not prove inaudibility or hot-plug behavior. Lower bias tests yield gains approximately 0.1027 and 0.5080, with nominal full gain near 1.0026.

The initial experiment used an unconstrained secant calibration against an unreliable operating-point fallback, producing an invalid trim and false clipping. Its rejected summary is retained. Adding the declared 1e12Ω numerical shunts, using a realizable resistor trim, constraining travel and checking the final calibration residual fixes that experiment. The ±12V timeout remains explicitly unresolved; it is neither a device-failure conclusion nor a passing supply test.

The 81-check evidence audit passes: input/deck hashes, duration, independent harmonic accounting, nominal screens, refinement, shunt sensitivity, untrimmed negative control and unchanged native boards. This validates the stated evidence, not a finished expression circuit.

## Component and sourcing comparison

| Candidate | Practical consequence | Current sourcing evidence |
|---|---|---|
| TI LM13700M/NOPB | Economical OTA; requires bias/trim/noise/stability work and a qualified socketed SOIC carrier | LCSC Chinese item C1346265 / item1436547: public product payload observed 25 November reports 83 in stock, MOQ1; public displayed price CNY4.20 has no verified quantity tier. No order/reservation. |
| TI LM13700N/NOPB | Convenient DIP socket, but obsolete stock is a poor new-build baseline | LCSC item3073743 public payload reports stock0 and stop_product; current TI order table lists SOIC variants. Do not select the historical DIP merely because it appears in the datasheet body. |
| HGSEMI LM13700N | DIP16 candidate avoids a carrier | LCSC C5160099 establishes manufacturer/package identity. Exact domestic stock/price and manufacturer-specific validation remain open. TI model results cannot qualify this different die. |
| THAT2180/2181 family | Dedicated audio VCA; different gain-control law, trim/package and sourcing burden | A Shenzhen distributor lists the families, but price is shown as zero/quote placeholder. No exact stocked purchasing candidate established in this pass. |

[LCSC part](https://item.szlcsc.com/1436547.html), [obsolete DIP listing](https://item.szlcsc.com/3073743.html), [HGSEMI listing](https://www.lcsc.com/product-detail/C5160099.html), [TI datasheet](https://www.ti.com/lit/ds/symlink/lm13700.pdf), [THAT datasheet](https://www.thatcorp.com/datashts/THAT_2181-Series_Datasheet.pdf), [Shenzhen distributor](https://www.sz-sonicom.com/).

[LCSC delivery policy](https://www.szlcsc.com/help/202.html) names mainland couriers and delivery to domestic customer addresses. This supports a Shanghai purchasing route as an inference; the particular address, shipping charge/date and order acceptance were not checked. No part is purchase-released. The exact socket/carrier, jack, toggle, pedal, trim and protection parts are not yet a complete sourced assembly.

## Next work and limits

Resolve the ±12V simulation failure without silently replacing the real op-amp; compare noise and control-feedthrough burden against a dedicated VCA. Build real bias-current and protected pedal-reference circuits, implement PANEL/EXPRESSION and unplug detection, and test control slew, shorts, open wiper, supply sequencing and fault override. Preserve the separate reverb-off function. Prove loaded wet gain, dry invariance and output polarity in the integrated circuit before editing native CAD.

The TI OTA model explicitly overestimates bandwidth and stability margin by more than twofold. It is one amplifier, not a complete dual-IC current budget. No actual tank acoustic transfer, socket parasitics, tolerances, PCB layout or assembled fit is modeled here. All six build scopes remain open.
