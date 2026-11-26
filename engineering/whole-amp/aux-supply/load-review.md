# Cold relay load and current-path screen — 24 November 2026

Owner: auxiliary supply qualification. This corrects a mismatch between the relay-driver and auxiliary-supply analyses. It does not change the schematic, PCB, functional blocks or mechanical design.

## Correction and source binding

The previous supply model used the [Omron G5V-2-H1 DC12](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v2.pdf) coil's minimum room-temperature resistance, 864 Ω. The existing control-switching contract already screens −25°C with a copper coefficient of 0.00393/K, giving 701.015 Ω. That temperature correction is an engineering approximation, not a guaranteed manufacturer cold-resistance limit. The current model now imports that same contract and verifies K1/K2/K3's exact selected family and coil nets against circuit.json.

At the 12.6 V screen bound, one coil draws 17.974 mA, the channel pair 35.948 mA and all three 53.922 mA. This is **23.25% above** the previous room-temperature screen. Ignoring driver/wire drop increases the load conservatively. R215's existing full allowance remains included: maximum 7.403 mA. The 2/10/20 mA logic profiles and 30/50/100 mA audio profiles remain explicit scenario assumptions; they are not newly qualified maximum loads.

The source-bound heater inventory counts each physical tube once: four [JJ ECC83S](https://www.jj-electronic.com/images/stories/product/preamplifying_tubes/pdf/ecc83s.pdf) packages at nominal 0.3 A and two [JJ EL34](https://www.jj-electronic.com/images/stories/product/power_tubes/pdf/el34_e34l.pdf) packages at nominal 1.5 A give **4.20 A** at 6.3 V. R508/R509's 200 Ω series path adds 31.5 mA; the existing unselected pilot allowance adds 150 mA, totaling **4.3815 A**. This is a nominal-plus-allowance inventory, not a maximum or startup-surge bound. It does not approve the historical 5 A heater winding or select a China-sourceable transformer.

## Updated results

All 72 line/frequency/reservoir/winding/load cases reached 0.6 s. Four distinct limiting cases were repeated at 10 µs instead of 20 µs. Raw-voltage differences stay below 10 mV, winding RMS differences below 0.5%, and path-current RMS/peak differences below 1%; observed maximum path difference was 0.0052%. Both raw-node instantaneous KCL and independent mean-current accounting pass. The latter uses a 1 µA numerical residual allowance; the largest observed residual was 44.5 nA.

| Scenario | Maximum half-winding RMS | Maximum conditional regulator heat | Tightest shared-sink budget at 60°C |
|---|---:|---:|---:|
| Idle | 0.1151 A | 2.081 W | 17.23 °C/W |
| Working reserve | 0.2111 A | 3.267 W | 9.75 °C/W |
| Expansion stress | 0.2941 A | 4.258 W | 7.44 °C/W |

**44/72 cases carry unresolved flags**, up from 41: 24 exceed the illustrative 0.25 A half-winding rating, 20 exceed the positive regulation input range, four fall below that range, and four exceed the negative regulation input range. Counts overlap. An out-of-range flag means the documented regulation conditions are not met; this fixture has no regulator control model and cannot predict the actual output waveform there. Cold-coil maximum load and hot-regulator ambient are independent conservative corners, not one claimed thermal equilibrium.

Current-path evidence adds what average DC load omitted:

| Path, maximum across cases | Steady RMS | Steady absolute peak |
|---|---:|---:|
| Each secondary half winding | 0.2941 A | 0.7888 A |
| D201/D202, positive rectifier individual branch | 0.2567 A | 0.7888 A |
| D203/D204, negative rectifier individual branch | 0.1436 A | 0.4955 A |
| C201 reservoir branch | 0.2962 A | 0.5790 A |
| C208 reservoir branch | 0.1741 A | 0.3910 A |

The largest whole-run charging peak is 3.133 A. It is only the result of this assumed winding/diode/ESR model with zero-phase sine startup. It is **not** a worst switch-on phase, saturation, fault or capacitor surge rating. Capacitor-branch RMS is a useful ripple-current input; exact capacitor endurance/ripple rating and board copper still need qualification. Individual-path maxima need not occur in the same case.

The read-only checker rejects eight corruptions: reintroduced room-temperature resistance, missing preload, missing case, incomplete run, altered deck, pulse current replaced with a load average, wrong shared-sink calculation and double-counted valve package. Stored decks and input/factory hashes allow reproduction. The original envelope and preload evidence remain unchanged.

## China procurement and remaining work

On this pass, [LCSC C128021](https://www.lcsc.com/product-detail/C128021.html) again identified the exact relay, but the global catalog is not proof of a domestic order route. [Mouser China's OPA2134PA page](https://www.mouser.cn/ProductDetail/Texas-Instruments/OPA2134PA?qs=7nS3%252BbEUL6uyT34OzaiM4g%3D%3D) appeared in search with indexed stock and RMB pricing; a live fetch timed out, so those cached numbers were not adopted as current stock or price. The [TI China direct page](https://www.ti.com.cn/product/cn/OPA2134/part-details/OPA2134PA) exposed unavailable/login-dependent stock. These remain sourcing leads; neither Shanghai checkout nor the complete BOM is verified. No order or supplier message was sent.

Next: replace reserve load assumptions with actual signal/dynamic/fault budgets, select the auxiliary transformer and protective/thermal implementation together, then qualify copper and connector paths against continuous, pulse and fault currents. Do not simply enlarge a provisional winding rating in this model to remove flags. All socket, three-board consolidation, populated fit and full drill-envelope gates remain open; the measured chuck remains 46 mm. The removable rear and functional-block requirements are unchanged.

## 25 November update — native reverb loads

The values above describe the November24 checkpoint. Current results/loads now include R619/R620; see [VAL-064 integration review](../reverb-600/rail-load-integration/review.md) for the replacement current/heat table and checks. All72 cases complete with44 engineering-flagged cases; those flags remain unresolved. The old source hashes and numerical values above are not current verification.

## 25 November VAL-069 update — circuit-derived working allocation

The working audio allocation is now70mA per rail before separately adding R619/R620, replacing50mA. [Current-budget review](../pcb-measured-r/current-budget/review.md) owns the passive-load assumptions and new current/heat table. All72 cases and four refinements complete;42 cases remain flagged. Historical numbers above are retained as dated evidence. The checker preserves the historical comparison with an explicit20mA working-profile delta and checks allocation against the new budget. The model still does not qualify hot/startup/fault current, actual transformer or cooling.
