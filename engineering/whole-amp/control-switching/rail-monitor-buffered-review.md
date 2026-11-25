# Buffered analog-rail inhibit candidate

Owner: control-switching integration. Input revision c6559ed; output is a candidate contract and reproducible static budget. No schematic or PCB changes. Done-condition for this checkpoint: correct the temperature limits, compare independent circuit equations, retain supplier gaps and identify the next implementation gate. Native adoption additionally requires exact sourceable parts, timing qualification, socket/pin mapping and preservation/ERC/DRC/visual review.

## Circuit and blocks

Keep the user latch, existing relay driver and reverb signal path. Both LM393P open-collector outputs join RAIL_OK, with a1.5k pull-up to+5V. Reuse the existing unused SN74HC14N U1E gate (input11/output10) to generate FAULT. FAULT drives an added NPN pull-down on REV_GATE through10k, with100k base/emitter. The candidate changes R341 from native1k to4.7k and retains its100k gate pull-down; user OFF can still inhibit independently. Exact NPN and timing components are not selected. U1F remains spare. A delay must not be added directly to the hysteresis node.

The original comparator feedback depended on relay gate voltage. This revision obtains feedback from RAIL_OK and reduces divider impedances tenfold to reduce input-bias sensitivity. The editable interface is [rail-monitor-buffered-contract.json](rail-monitor-buffered-contract.json).

| Network | Resistors |
|---|---|
| Positive sense | +15V through3.83k;499Ω toGND;33k feedback |
| Positive reference | +5V divider3k/1k |
| Negative clamp/sense | +5V through1k toCLAMP;−15V through5.1k toCLAMP;CLAMP through3.01k toNSENSE;1k toGND |
| Negative reference | +5V through9.1k;1.01k toGND (1k+10Ω);249k feedback |

Candidate low-leakage clamp: one BAV199-7-F junction, anodeGND/cathodeCLAMP. Manufacturer top-view diode orientation was inspected; numbered footprint assignment still requires the package drawing. The second junction must not be left as an unintended signal path.

## Evidence and limits

The earlier classic LM393P budget mixed room-temperature bias/output limits with full-temperature offset. It is corrected to±525nA per input and0–0.7V collector low. The symmetric independent current envelope conservatively covers400nA average bias plus half250nA offset current; it is not a prediction that physical input currents reverse direction. TI SLCS005AH page8 is authoritative. The rejected LM2903B model remains unused.

The buffered screen uses+5V4.75–5.25, offset±9mV, total resistor±0.4%, feedback high4.45–5.25V and clamp leakage±80nA. ST L7805CV's4.8–5.2V limit is room-temperature only and was not substituted for the wider full-condition reference range.

| Settled rail magnitude | Positive | Negative |
|---|---:|---:|
| Enable threshold | 10.139–11.776V | 9.594–11.937V |
| Disable threshold | 9.612–11.258V | 9.102–11.462V |
| Minimum same-unit hysteresis | 0.432V | 0.395V |

The engineering screens remain maximum enable12V, minimum disable9V and hysteresis0.35V. These are allocations, not proof of quiet operation or op-amp headroom at every intermediate voltage. 18,432 endpoint cases and2,004 independent nodal comparisons support the static equations. Eleven conditional checks pass; qualification remains false. Pull-up budgeting gives RAIL_OK≥4.471V and comparator sink≤3.718mA. These bounds assume powered, nonnegative sensing nodes; startup/back-powering is outside this calculation. TI's collector-low test uses1V differential overdrive, so near-threshold dynamics require separate evaluation.

Vishay TNPW e3 is a **family candidate**, not a purchased resistor set. Total error sums initial0.1%,25ppm/K over film0–85°C referenced to20°C, general-mode8000h endurance(0.1%+0.02Ω), and solder heat(0.02%+0.01Ω). Series1k+10Ω uses resistance-weighted error rather than applying the10Ω absolute term to the whole divider. This declared profile fits0.4%; it does not establish lifetime beyond8000h, arbitrary humidity/assembly stress or actual film temperatures. The cabinet thermal check remains mandatory.

BAV199 publishes80nA leakage at75V/150°C, used conservatively at much lower voltage. The1.1V forward-clamp allocation gives comparator-input magnitude≤0.277V, but its temperature guarantee is unresolved: the published forward-voltage maxima are at25°C. Upper fault-current bound is3.25mA. Do not mark this fault input protected solely from the passing arithmetic check. Comparator state is not assumed valid belowGND; independent+5V reset behavior remains required.

## Chinese sourcing and next action

[BAV199-7-F C155248](https://item.szlcsc.com/166590.html) reports minimum buy1, stockNumber11302 and validStockNumber2260 on2026-11-25. Both differing stock fields are retained in results/rail-monitor-buffered-sources.json. Domestic delivery policy supports a Shanghai route in principle; address-specific checkout is not verified. Nothing was ordered.

Exact TNPW resistor stock is incomplete; a499Ω LCSC catalog page is not evidence of available stock. Source the required values in small quantities or qualify another manufacturer's temperature/endurance limits. Do not transplant the TNPW error budget to a generic0.1% listing. Resolve NPN full-temperature behavior, clamp bounds, all supply sequences and fast-fault versus relay-release timing before native adoption. Chassis, sockets and drill access are unchanged and unqualified.

Reproduce with `python3 engineering/whole-amp/control-switching/tools/rail_monitor_budget.py` and `python3 engineering/whole-amp/control-switching/tools/buffered_rail_budget.py`. Primary PDFs and source hashes are retained under evidence/ and results/. Human check: measure thresholds, fault response and temperatures on the assembled unit, including the actual relay flyback circuit and harness.

Correction2026-11-25: rail-monitor-precision-review.md binds acceptance to the native10Vpeak signal target. This historical candidate passes its original numerical screens but fails the retained audio-headroom boundary; do not adopt it on the11/11 count.
