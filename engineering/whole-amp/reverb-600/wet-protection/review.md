# K3 wet-contact protection candidate

Owner: amplifier integration. Baseline: `297850b`, current `reverb-600/circuit.json`. This is a focused correction to the existing reverb output block, not a new audio architecture. **No native circuit or PCB change yet.**

VAL-065 found 138.422 V at K3's open wet contact in the retained 313 V C6-short fixture. That exceeds the relay's 125 V maximum DC switching voltage. The proposed correction is two opposing-series Zeners across WET_AC/GND, with R618's voltage rating increased and R616's pulse capability established. It retains the relay, its OFF-priority function, the dry/wet interface and DEC-016's common buffered loop.

## Proposed exact changes

| Reference | Proposed part or change | Interface |
|---|---|---|
| D603 | Vishay BZX55C27-TAP, DO-35 | Cathode to WET_AC; anode to new WET_Z_JOIN |
| D604 | Same part | Cathode to GND; anode to WET_Z_JOIN |
| R618 | Keep 1 MΩ; use already-investigated MF0207FTE52-1M, 350 V / 0.6 W package | WET_AC ↔ MIX_OUT unchanged |
| R616 | Investigate Vishay PR01000101000JA500, 100 Ω / 1 W / 5% | OUT_BUF ↔ OUT_AC unchanged; tolerance and footprint review required |

D603/D604 are available reference identifiers. Their anodes connect together; they are **not** two opposing parallel ordinary diodes, which would clip the audio near a forward-diode drop. The published [Vishay Zener datasheet](https://www.vishay.com/docs/85604/bzx55.pdf) is retained under `sources/`. The 27 V candidate's leakage test is at 20 V; the initial 24 V candidate was tested at only 18 V. This matters because the expanded normal-signal fixture reaches 19.186 V when summing arbitrary dry/wet phase contributions. It does not establish low distortion at all temperatures or under rectification-induced offset.

## Completed calculations and simulations

The DC screen evaluates 1,024 combinations: six native resistors at both 1% endpoints, four available-rail levels (278, 313, 344.3 and 400 V), and no clamp or three clamp envelopes. The 400 V case is an extended engineering screen, **not** a newly specified early-stage rail. C6 is shorted and tube plate current omitted. Capacitors are open at DC. The clamp is symmetric, with 23/35.6/40 V threshold comparisons and a 220 Ω conducting slope; it is not a Vishay nonlinear model or guaranteed hot/cold bound.

The AC sensitivity screen uses the native passive dry/wet and SEND-attenuation branches, source resistances 1/40/200 kΩ, 20/82.4/1,000/20,000 Hz, C607 at ±10%, and added pair capacitance from zero through 1 nF. Dry and wet sources are bounded at 150 V and 18 V peak. These are deliberately expanded test amplitudes; normal rail, loading and overload behavior still require the integrated amplifier model. Added capacitance is an engineering allowance, not a guaranteed maximum for the selected Zeners.

| Result | Finding |
|---|---:|
| Maximum wet-node voltage with declared clamp envelopes | 40.0561 V |
| Largest AC gain change from added capacitance | 0.01033 dB |
| Maximum normal wet-node sum in the AC screen | 19.1863 V |
| Maximum pair dissipation in sustained C6-short screen | 10.208 mW |
| Maximum R618 stress at 313 V supply | 235.853 V |
| Maximum R618 stress at 344.3 V supply | 261.368 V |
| Maximum R618 stress at 400 V supply | 306.773 V / 94.446 mW |

**The clamp must not be added while leaving R618 specified for only 250 V.** The proposed 350 V part clears this voltage screen. Its thermal derating, footprint and sourcing remain subject to the usual integration checks.

SPICE independently reproduces 24 bipolar DC and 48 AC cases, with maximum analytic discrepancies of 3.09e−11 V and 4.72e−14 V. Thirteen contact-closing transients include one half-timestep repeat. The 1% native R616 / +10% C607 case peaks at 0.40452 A and about 0.882 mJ in R616. The independent RC energy comparison agrees within 1%; halving the timestep changes the measured energy by less than 2.2e−8 relative. This resolves the numerical screen, not actual contact life.

The 0.405 A analytic bound includes the C607 discharge and a conservative dry-feed current. It **excludes the very short direct discharge of diode and PCB capacitance** through contact/wiring impedance. At the 1 nF allowance, stored energy is about 0.802 µJ; peak current still needs a physical parasitic model or measurement. Contact bounce, arcing and inductive ringing are not modeled.

## R616 pulse-rated candidate

The [Vishay PR01 datasheet](https://www.vishay.com/docs/28729/pr010203.pdf), revision 08-Jul-2025, page 9, provides pulse-loading curves. The page was visually inspected. `results/pulse-budget.json` evaluates the 5% part with its 250 ppm/K coefficient over −25 to 70°C: minimum resistance 93.8125 Ω, initial C607-branch current 0.427 A, peak power 17.104 W. These values differ from the 1% native-resistor simulations above.

A conservative 20 W, 50 V, 1 ms rectangle plus a 1 µW tail covers this calculated isolated discharge. At one event per second, it is below a deliberately rounded-down 50 W point from the manufacturer's 1 ms, period/pulse-width=1,000 curve. This is an **isolated-event screen**, not permission to infer arbitrary repetition, relay-bounce endurance, actual assembly temperature or full output-buffer stability. The current generic 0.25 W resistor specification provides no corresponding pulse proof.

## China procurement evidence

Exact [DigiKey China BZX55C27-TAP listing](https://www.digikey.cn/zh/products/detail/vishay-general-semiconductor-diodes-division/BZX55C27-TAP/4826078) indexed 40,283 pieces, quantity one and ¥3.97 each. The [PR01000101000JA500 listing](https://www.digikey.cn/zh/products/detail/vishay-beyschlag-draloric-bc-components/PR01000101000JA500/7350589) was found through its Chinese category row: 15,472 pieces, quantity one and ¥2.15. These are **dated search-index observations**, not live stock verification; direct retrieval failed. Estimated component subtotal for the three new/replacement parts is about ¥10.09 before freight and R618, subject to confirmation.

The supplier's [China delivery policy](https://www.digikey.cn/zh/help-support/delivery-information) indexed delivery to China and RMB/DDP ordering. That establishes a plausible Chinese purchasing route; the Shanghai address, actual availability, freight and checkout remain unverified. No order was placed. The domestic LCSC C2528 BZX55C24 belongs to **ST(先科)**, not Vishay or STMicroelectronics; its identity cannot be combined with the Vishay electrical data. See `sources/retrieval.json` for distinct observations.

## Disposition and next implementation gate

The local clamp plus uprated R618 is a viable correction candidate within the declared envelopes. It is not an adopted circuit. Preserve this complete correction as one integration set: diodes, R618 rating, R616 pulse evidence, exact footprints and readable schematic. Recheck the updated wet-mute, supply-injection and all relevant voltage-domain routing after integration. The new common loop, actual early B+ range and production component data can change the final envelope.

Remaining qualification includes leakage/nonlinear loading and offset at temperature, actual parasitic contact pulses, repeated-fault behavior, exact Chinese purchasing, native ERC/DRC and populated fit. Do not clear VAL-065's relay hold or claim Shanghai purchase-readiness on this screen alone. All six build scopes remain incomplete.

## Reproduction and evidence ownership

Run `tools/analyze.py` with NumPy, `tools/simulate.py` with KiCad's bundled Python/ngspice, then `tools/pulse_budget.py` and `tools/check.py`. The checker rejects missing runs, stale source identity and false native adoption. Source/deck/waveform hashes bind the evidence. `results/` contains generated products; `sources/` contains primary documents and supplier observations; no active native file is modified. The scoped ICM structural check is supplemented by this manual boundary review: the module owns only wet-contact protection, not the main supply, loop topology, procurement checkout or fabrication release.
