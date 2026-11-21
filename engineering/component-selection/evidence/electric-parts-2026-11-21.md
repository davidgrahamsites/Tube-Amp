# Electric build: additional exact component selections, 2026-11-21

Owner: remaining-parts worker; integration owner: root electric-build agent.

Task: qualify straightforward remaining electrical components for the existing electric build. Inputs are `coverage.json`, `candidate-register.json`, the current `engineering/whole-amp/reverb-600/circuit.json`, and manufacturer documents cited below. Output is this evidence record only. No shared register, schematic, PCB, order, or supplier message was changed by this worker. Human check: compare each listed reference and net with the latest schematic, then compare the delivered part with the manufacturer outline before PCB release.

## Integration result

Select the following exact parts for **11 additional references**, subject to the stated circuit envelopes and normal integration checks. Selection establishes a specific component and footprint input; it does not release the whole amplifier for construction. Current stock and final cabinet fit have not been verified by this pass.

| Coverage | References | Exact manufacturer part | Decision |
|---|---|---|---|
| P064 | C301, C311 | KNSCHA MEB105J63V82CB0235 | Select 1 uF, 5%, 63 V film for the two 5 V debounce nodes. Reuse the existing exact-part footprint. |
| P076 | C351, C352, C353 | KNSCHA MEB104J63V82CB0236 | Select 100 nF, 5%, 63 V film for 5 V bypass. Reuse the existing exact-part footprint; place at IC supply pins with a short return. |
| P028 | R1 | Tyohm RN 1/2WS 68K F T/B A1 | Select 68 kohm, 1%, 0.5 W metal film for INPUT to INPUT_STOP. This is an input signal resistor, not a B+ dropping resistor. |
| P013 | R43, R24 | Yageo HHV1WSJT-73-10M | Select 10 Mohm, 5%, 1 W metal-glazed thick film for CLEAN_OUT/GND and MIX_OUT/GND. Do not describe it as metal film. |
| P108 | R38 | Vishay PR01000102202JR500 | Select 22 kohm, 5%, 1 W for BIAS_FILTER to BIAS_OUT, with differential voltage bounded at 80 V and ambient at 100 C. Bias adjustment range still needs its tolerance check. |
| P113 | C505 | Aishi EGW2CM470G16OT | Select 47 uF, 20%, 160 V for HREF to GND, positive at HREF. Normal HREF including ripple must remain below 100 V, local ambient below 85 C. |
| P105, partial | D7 only | onsemi 1N4007RLG | Select for the negative-bias rectifier only. Split the shared P105 group: this decision does not qualify D201–D208 or the main supply bridge. |

The five control capacitors extend two already selected MPNs, without adding a new capacitor family. The 1 uF tolerance is 5%; verify debounce timing using actual resistor and logic-threshold corners. Film bypass selection does not replace a board-level check for high-frequency supply ringing.

## Mechanical inputs for PCB integration

All dimensions are millimetres. Proposed pad geometry below is a design input, not an assertion that the present PCB implements it. Use maximum package dimensions for collision checks. Courtyard allowance is additional to electrical clearance requirements.

| Exact part | Manufacturer outline | Proposed board interface |
|---|---|---|
| MEB104J63V82CB0236 | Body 7.2 wide × 2.5 thick × 6.5 high, each ±0.5; pitch 5; nominal lead 0.5 | Existing 5 mm pitch footprint, 0.9 finished holes, 1.8 pads; maximum body plus 0.25 each side courtyard. |
| MEB105J63V82CB0235 | Body 7.2 wide × 5 thick × 10.5 high, each ±0.5; pitch 5; lead 0.6 ±0.05 | Existing 5 mm pitch footprint, 0.9 finished holes, 1.8 pads; maximum body plus 0.25 each side courtyard. |
| RN 1/2WS 68K F T/B A1 | Official RN table: length 6.4 ±1, diameter 2.4 ±0.5, lead 0.6 ±0.1, straight lead length 28 ±3 | Form leads at 10.16 pitch; 0.9 finished holes. Body envelope 7.4 × 2.9 before courtyard. Check lead forming clear of end seals. |
| HHV1WSJT-73-10M | HHV1WS: length 11.5 ±1, diameter 4.5 ±0.5, lead 0.8 ±0.05, lead length 35 ±2 | Form at 17.78 pitch, 1.2 finished holes. Body envelope 12.5 × 5 before courtyard. The large body is intentional; do not substitute a generic small resistor footprint. |
| PR01000102202JR500 | PR01: body diameter max 2.5, body length L1 max 6.5, overall coated length L2 max 8.0; copper lead 0.58 ±0.05 | Form at 12.7 pitch, 0.9 finished holes; envelope 8 × 2.5 before courtyard. Preserve space around the resistor for cooling. |
| EGW2CM470G16OT | Exact table nominal diameter 10, length 16; family drawing permits diameter +0.5, length +2; pitch 5 ±0.5; nominal lead 0.6 | 5 mm pitch, 0.9 finished holes; body envelope diameter 10.5 × height 18 before courtyard and vent clearance. Positive pad HREF, negative GND. |
| 1N4007RLG | onsemi case 59-10: body length 4.10–5.20, diameter 2.00–2.70; lead diameter 0.71–0.86 | Form at 10.16 pitch, 1.2 finished holes; cathode band/pad 1 at BIAS_DIODE_AC, anode/pad 2 at BIAS_RAW. Body envelope 5.2 × 2.7 before courtyard. |

The Aishi maximum height is **18 mm**, not the nominal 16 mm in the supplier title. Leave additional clearance above its pressure vent. No package in this table establishes the available chassis height.

## Rating and stress checks

### R1: actual input role

The official Tyohm RN sheet includes **1/2WS**: 0.5 W at 70 C, maximum working voltage 300 V, linear power derating to zero at 175 C. At 100 C its rated power is 0.357 W. For a deliberately generous 20 Vrms differential across the full minimum resistance, power is `20²/(68000×0.99) = 5.94 mW`. The rating is also limited by `sqrt(P×R)`, not merely the catalogue 300 V maximum.

This calculation does **not** permit 500 V across R1: that would dissipate 3.71 W and exceed its voltage rating. Preserve its input-only role and the amplifier's separate high-voltage isolation. The RN sheet describes a low-noise metal film family; actual amplifier hiss and RF rejection remain bench checks. The supplier's exact suffix has a 50 ppm/C listing; do not infer that suffix from a different resistor family.

Source: local manufacturer `Tyohm-RN-official.pdf`, page 2, visually inspected in this pass; matching [domestic exact-part identity](https://item.szlcsc.com/430513.html). The drawing header uses length ±1; the 6.4 mm body is not a guaranteed maximum.

### R43 and R24: 10 Mohm shunts

The [manufacturer exact-part sheet](https://www.yageogroup.com/component-documentation/download/specsheet/HHV1WSJT-73-10M) identifies thick-film, metal-glazed construction, 1 W at 70 C, 5% tolerance and 200 ppm/C. The [manufacturer HHV family document, April 2024](https://www.mouser.com/datasheet/2/447/YAGEO_HHV_datasheet_2024v3-3450127.pdf) gives HHV1WS a 5000 V maximum working-voltage ceiling, with power derating to zero at 155 C. At 100 C, permitted power is approximately 0.647 W. At a conservative 500 V differential, minimum resistance 9.5 Mohm gives 26.32 mW. The power-limited continuous-voltage ceiling at 100 C is approximately 2479 V, below the family's 5000 V ceiling and well above this calculation.

Normal shunt DC bias is near zero; 500 V is a rating bound, not a claim that these audio nodes operate at 500 V. The resistor's coating is not touch-safe 5 kV insulation. Copper clearance and coupling-capacitor failure containment remain separate design requirements. This family is not a precision low-excess-noise audio part; near-zero normal DC bias reduces that concern, but noise and pops must be checked on the prototype.

### R38: negative-bias resistor

The manufacturer `Vishay-PR.pdf`, revision 08-Jul-2025, document 28729, specifies PR01 as 1 W, 350 V maximum working voltage, and 135 K/W thermal resistance. Its application section limits the PR01 hot spot to **205 C**; do not apply PR03's 250 C limit. At 80 V across the minimum 20.9 kohm, dissipation is 0.306 W. A preliminary `100 + 135×0.306 = 141.3 C` hot-spot estimate is below 205 C. This is a mounting-dependent estimate, not a cabinet temperature measurement. The power-limited working voltage also governs; 350 V is not permissible across a 22 kohm, 1 W part.

The exact `J` code is 5%. Re-run negative-bias adjustment extremes with that tolerance, supply extremes, and RV10/R503 tolerances before release. Selection preserves the specified 22 kohm value; it does not prove safe output-tube bias range. [Manufacturer PR datasheet](https://www.vishay.com/docs/28729/pr010203.pdf).

### C505: heater reference filter

Manufacturer `Aishi-EGW.pdf`, approval CRS-ZG-2008170, version 01, August 2020, contains the exact EGW2CM470G16OT row despite the internal CD11GAS series designation. It gives 47 uF/160 V, diameter 10 × length 16, and 680 mArms at 105 C/100 kHz. The stated 120 Hz coefficient is 0.50, giving 340 mArms at 120 Hz. **Do not call that a 100 Hz guarantee:** a 100 Hz coefficient is not stated. The 10000-hour test is at 105 C with rated DC and ripple; it is a qualification test, not a promised service life in this cabinet.

R506/R507 form a 220 kohm/39 kohm divider. At 550 V B_SCREEN and nominal resistances HREF is 82.82 V; with the selected JR resistors at ±5% and the upper resistor low/lower high it is about 90.11 V. The proposed normal limit of 100 V including ripple is below 160 V. Use the real supply transient result to confirm that limit. The feed resistor limits charging current to approximately 2.63 mA at 550 V and minimum 209 kohm; heater leakage and faults are separate cases. This supports the small filter application, not a main B+ reservoir application.

Primary source is the local manufacturer approval sheet, printed pages 5–6 and 9–10; [supplier page links the original PDF](https://item.szlcsc.com/3521241.html). Sleeve marks are not electrical insulation. Maintain the negative stripe to GND and keep this part away from hot valve sockets.

### D7: negative-bias rectifier only

[onsemi 1N4001/D, June 2024 revision 18](https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf) lists 1N4007RLG as an available ordering code, with 1000 V repetitive reverse rating and 1 A average rectified rating under specified mounting/temperature conditions. The discontinued section is for other listed order codes, not this RLG code.

With a design bound of 55 Vrms on the bias winding, peak is 77.8 V. Half-wave capacitor charging gives an approximate maximum reverse voltage of twice that peak, 155.6 V. R40 at 1 kohm minus 5% bounds initial charge current at about 81.9 mA, before winding resistance and diode drop. This is well below the diode's rating and does not require treating the 30 A one-cycle surge rating as continuous capability. It depends on retaining R40 and confirming the winding maximum. Final supply/startup/fault verification remains open; these bounds do not qualify other rectifier positions with much larger reservoir-current pulses.

## Mainland purchasing evidence

These are **historical observations from the existing candidate register on 2026-11-11**. Public pages checked on 2026-11-21 did not provide a fresh signed-in stock/price quote. MOQ and price below are useful low-unit sourcing evidence, not a claim of availability today. No order was placed. Do not confuse manufacturer reel quantity or JLC assembly stock with SZLCSC's retail minimum.

| MPN | Domestic SKU/link | Historical MOQ | RMB each | Historical stock |
|---|---|---:|---:|---:|
| MEB104J63V82CB0236 | [C3034535](https://item.szlcsc.com/3579063.html) | 10 | 0.263736 | 28K+ |
| MEB105J63V82CB0235 | [C3975271](https://item.szlcsc.com/4544345.html) | 5 | 1.168 | 10K+ |
| RN 1/2WS 68K F T/B A1 | [C433508](https://item.szlcsc.com/430513.html) | 50 | 0.0988 | 1300 |
| HHV1WSJT-73-10M | [C911419](https://item.szlcsc.com/981333.html) | 5 | 0.9964 | 840 |
| PR01000102202JR500 | [C1740495](https://item.szlcsc.com/1831276.html) | 5 | 1.0684 | 2070 |
| EGW2CM470G16OT | [C3013687](https://item.szlcsc.com/3521241.html) | 5 | 0.6259 | 35K+ |
| 1N4007RLG | [C53568](https://so.szlcsc.com/global.html?k=C53568) | 10 | 0.3291 | 173K+ |

KNSCHA primary drawing sources and their previous integration record are in `lv-film-selection-2026-11-20.md`. No new semiconductor or film-capacitor price is inferred from overseas distribution.

## Items intentionally left unresolved

- **Tyohm RN 1WS** candidates for other values: the inspected official RN table lists 1W and 1WL, but not 1WS. Do not transfer the larger 1W body's 500 V or power/thermal data to a smaller supplier-labelled 1WS part. Obtain its exact drawing or choose another traceable family.
- **C202/C205/C209, KEMET R82DC3330AA60J:** exact-part manufacturer export is found [here](https://datasheet.octopart.com/R82DC3330AA60J-KEMET-datasheet-86450220.pdf). It confirms 330 nF, 5%, 63 VDC/40 VAC; maximum body 7.4 × 3.6 × 7.6, 5 ±0.4 pitch and 0.5 ±0.05 lead. Historical C600436 MOQ 5/RMB0.9887/5670 on November 11 remains valid as historical evidence. However, search also found a manufacturer change notice naming this exact part (`Kemet-PCN-NDC_20250219_021.pdf`); its contents could not be fetched. **Do not promote this selection until that notice is read and lifecycle/packing change is understood.** This is additional evidence, not part of the 11 selected references.
- R605 domestic low-quantity sourcing, R616 fault heating, main B+ reservoirs, magnetics, mains parts, and larger rectifier charging pulses remain with their existing holds. This pass does not silently clear them.

## Integration and human verification

1. Root may integrate the 11 reference mappings after checking that the latest circuit still has these nets and the listed operating bounds.
2. Keep D7 as a partial P105 closure; retain all unqualified bridge/rail diode rows as pending.
3. Build footprints from maximum outlines, pin polarity and proposed hole sizes above. Inspect actual samples at 1:1 scale. Check lead forming and the C505 vent/height allowance.
4. Preserve the purchase observation date. Refresh stock and price before an order.
5. Run circuit tolerance/startup checks, PCB clearance checks and the scoped ICM check in the integration work. No simulations or PCB design-rule checks were run by this evidence-only worker.

Integration review correction: R506/R507 selected FMP200JR parts are5%, not1%. Root corrected the HREF worst-case bound to90.11V and feed current to2.63mA before selection. This still requires actual supply/transient checks against the100V normal envelope.
