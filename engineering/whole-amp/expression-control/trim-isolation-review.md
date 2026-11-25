# Expression trim and solver isolation — 25 November 2026

Owner: expression-control. Inputs: VAL-043, unchanged TI LM13700/OPAx134 models and Diodes MMBT3906 model. Output: VAL-044 diagnostic evidence and revised nominal trim candidate. Done condition for this checkpoint: repeatable trim calibration, audio/refinement comparison, preserved failures and scoped ICM audit. No native CAD integration belongs to this checkpoint. Hardware startup, tolerance, control-port protection and actual assembly evidence remain required.

## Nominal trim improvement

The previous 330k feed needed 98.872% of its 100k trim-divider travel. `tools/trim_screen.py` compares 220k and 150k feeds without editing the historical factories. Nominal calibrated fractions are 74.262% and 56.980%, respectively. Both leave less than 1µV modeled output residual at the calibration condition. These fractions describe the simulated electrical divider, not guaranteed mechanical travel or real-device tolerance coverage.

The 150k candidate has 33 retained cases: 26 complete and seven failed operating points. At 8V peak, modeled gain is 0.95733 at100Hz, 0.95752 at1kHz and0.94919 at10kHz. Sampled THD is at most0.05997%; the1kHz half-step gain difference is0.00337%. ±12V full-gain transient also completes. These are isolated wet-cell results, not whole-amplifier power or distortion specifications.

**Do not adopt it yet:** ±12V midpoint now fails its direct operating-point solve; the three rails' near-dry/fully-dry solves also fail. Fixed trim leaves output DC of+27.94mV at0°C and−41.85mV at70°C. The improved nominal trim range does not close temperature, offset distribution, noise or switching-pop concerns. 220k has calibration evidence only, not a complete alternative audio/temperature screen.

## Why solver success needs a settling check

`bias_continuation.py` takes267 node voltages from the previous successful full-to-off transient and uses them only as solver hints. The direct off calculation still fails. `bias_isolation.py` retains five causal cases:

| Diagnostic | Observed result | Interpretation |
|---|---|---|
| Complete previous candidate, off | Failed OP | Existing failure reproduced |
| Bias servo alone, collector fixed at−14V | OP reports success via transient fallback; output subsequently moves from7.3936V to5.00604V during1ms | The returned OP was not settled |
| Idealized limited-gain controller | Valid numerical OP, audio output about0.501mV | Diagnostic substitution, not a real part |
| Fixed base-drive voltage | Valid numerical OP, audio output about0.501mV | Audio cell can solve at this off bias |
| Real controller with collector fixture, OTA separately biased | Failed OP | Decoupling the collector does not by itself cure initialization |

The [ngspice manual, operating-point analysis](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf) describes a transient fallback whose default duration is10µs. The installed45.2 runtime's log confirms fallback use; the current online manual is47+. A returned vector within the supply rails is insufficient evidence of DC settling. None of the17 complete VAL-043 cases' retained logs used this fallback, so this discovery does not relabel those results. It does limit how future results may be accepted. No manufacturer model was modified to force convergence.

## Parts and pedal evidence

The [Bourns3296 datasheet](https://www.bourns.com/docs/product-datasheets/3296.pdf) identifies the100k, ±10%,25-turn trim family. [LCSC China C48084](https://item.szlcsc.com/49091.html) public fields observedNovember25 show BOURNS3296W-1-104LF, stock9831, minimum1. Metadata priceRMB2.58 has an unknown quantity tier. This is a candidate, not a frozen footprint or worst-case trim qualification. Manufacturer identity matters: similarly named JIERR products are separate parts. The existing [LCSC domestic delivery policy](https://www.szlcsc.com/help/202.html) supports a mainland delivery route; exact Shanghai checkout, fees and order acceptance are not verified. No order was placed.

The [Hotone Ampero Press manufacturer manual](https://hotoneaudio.oss-cn-shenzhen.aliyuncs.com/prod/support/Ampero%20Press_Manual_EN_V01_210226.1629083094134.pdf), visually checked including its wiring drawing, shows a passive10k expression pot: tip=wiper, ring and sleeve=ends. Its100k pot is the separate volume function. Taper and heel/toe polarity are not established by that drawing. This supports a concrete interface example, not purchase selection; the25k edition differs. A matched panel/pedal proposal must account for protection-resistor loading, response law and cable-fault behavior before changing the existing100k logarithmic audio control. Exact accessory stock and Shanghai delivery remain unverified.

## Acceptance and next action

`tools/audit_trim_isolation.py` passes152 evidence checks while explicitly reporting `circuit_qualified:false` and all seven failed trim-candidate cases. Native schematic/board sources are untouched. The functional blocks, independent rear removal and drill-access requirements remain unchanged.

Next: solve and independently validate the physical controller's near-zero-current behavior, including settled OP and supply startup. The current internal target is inverse:0V means full wet and5V means off. Do not connect a tip-wiper pedal directly to it or assume a pull-down gives a dry fault state. Establish the required control inversion explicitly. Then integrate the selected low-voltage panel/pedal interface, including unplug fallback, open wiper, shorts, transition smoothing and powered-off behavior. Keep exact sourcing, socket/carrier geometry and three-board assembly checks open. Do not replace the controller with the ideal diagnostic source in a build artifact.
