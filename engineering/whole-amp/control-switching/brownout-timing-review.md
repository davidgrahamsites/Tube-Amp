# Brownout warning — failed baseline and rejected repair trial

Owner: Renegade integration. Task card: baseline5700c97, VAL-051 supply decks and VAL-052 detector, plus the precision rail-monitor thresholds. Test whether gradual mains collapse leaves the proposed mechanical wet mute enough warning. Outputs are reproducible failed cases, independent checks, a concrete raw-warning comparison and source evidence. This screening step is complete when those results are preserved; full power-sequence/contact qualification and native adoption are separate gates. No schematic, PCB, mounting or functional block changed.

## Result and decision

The existing secondary-loss detector is insufficient by itself for gradual brownout. Of32 cases,20 miss the provisional mute allowance before loss of documented regulator input-output headroom. A separate memoryless regulator diagnostic still misses the allowance in14 cases when the precision rail monitor is also considered. These are **model failures**, not measured audio pops. Neither actual regulator dynamics nor contact movement is represented.

A spare-comparator raw-warning trial with a10000µF positive reservoir improves the timing comparison, but is **not adopted**: eight low-line/endurance-sensitivity cases fail the healthy-enable threshold. Do not release this circuit or simply keep increasing capacitor size. Next: compare a faster K3 suppression/release arrangement against the existing30V driver limit and the raw-warning window, then establish the exact transformer/load/temperature budget. Reference/logic sequencing remains open.

## What was tested

The32 baseline cases span120V/60Hz and220V/50Hz, low mains, the prior−5% winding sensitivity, two starting phases, fast/slow detector profiles and10/50/200/1000ms linear secondary-amplitude collapse. Four representative cases from each mains mode are shown below for the slow/high envelope profile and zero-degree phase.

| Mains mode | Ramp | AC detector reserve before raw floor | Combined reserve in simplified audio-rail model |
|---|---:|---:|---:|
|120V|10ms|49.75ms|103.89ms|
|120V|50ms|14.66ms|68.80ms|
|120V|200ms|−97.46ms|−12.73ms|
|120V|1000ms|−667.28ms|−5.66ms|
|220V|10ms|1.96ms|56.10ms|
|220V|50ms|−32.94ms|21.20ms|
|220V|200ms|−137.55ms|−12.73ms|
|220V|1000ms|−706.30ms|−7.96ms|

The subtraction includes the same10µs comparator allocation,13.947ms coil-current decay screen and5ms contact/logic allowance as VAL-052. None is a guaranteed complete mute time. The raw floor is18.836V, required for the worst calculated regulator setting plus3V input-output reserve. Crossing it is not automatically an audible fault. The separate diagnostic assumes output magnitude follows `min(setpoint, raw−3V)` and uses the existing positive13.5V/negative12.5V audio floors; it is not a manufacturer regulator model. Constant current loads after dropout are artificial. Results below the declared reserve boundary are diagnosis only, not physical qualification.

Two baseline half-step repeats agree within the retained0.1ms numerical criterion. Exact decks and logs are in results/brownout-timing/screen.json and simulator.log. The extended0.5s observation after collapse captures both raw-rail crossings; it does not assert that post-dropout current remains constant in hardware.

## Concrete raw-warning trial

Use the unused half of the candidate AC-detector LM393BIDR: minus to REF5, plus to RAW_SENSE, collector to shared RAIL_OK. RAW_SENSE connects to raw positive through3kΩ, ground through1.01kΩ and RAIL_OK through1MΩ. The positive reservoir trial becomes10000µF/50V; negative stays6800µF. A separate6.8kΩ REF5-bleeder trial is recorded, but its full shared-node audit is pending; the existing precision candidate remains7.5kΩ.

The inherited0.4% resistor/0.3% reference allocations produce enable19.671–20.062V, disable19.657–20.049V, minimum same-corner hysteresis11.61mV. Those are conditional bounds, not exact sourced resistor lifetime guarantees. The actual added divider is present in SPICE, with5mA reservoir leakage added conservatively. Held feedback profiles and separately enclosed thresholds do not constitute a coupled comparator simulation.

32 comparison cases use the slow AC-envelope profile, both phases/mains modes/all four ramp lengths, and two capacitor conditions:

| Condition | Positive capacitor/ESR | Minimum healthy enable margin | Minimum provisional timing reserve |
|---|---|---:|---:|
|Initial low capacitance|8000µF /0.15Ω|+22.68mV|+7.895ms|
|Post-endurance sensitivity|6000µF /0.30Ω|−136.83mV|+0.939ms|

Every credited fault request remains asserted at least2ms, with the existing conditional50ms restart hold covering first headroom loss. Shorter intervals are retained but do not receive that credit. All32 meet the provisional timing comparison; eight fail healthy-enable in the second profile. Even the initial22.68mV margin is too small to turn these allocations into a robust design. One worst-case half-step repeat is retained. No candidate is marked accepted.

The manufacturer's3000h/105°C test permits25% capacitance change from the initial value. Combining initial−20% and another−25% gives60% nominal; the earlier exploratory64% assumption was replaced. This is a sensitivity, not a service-life prediction. The two ESR allocations are not guaranteed cold/endurance limits.

## Sources, China route and fit

[KNSCHA152EC0344, C5456836](https://item.szlcsc.com/6369689.html): November25 public record168 stock, minimum1/ratio1; structured offer¥8.31 before freight. Manufacturer PDF is retained with its URL/hash in source-observations.json. Exact product table:10000µF±20%,50V,35×40mm body,4.04A at120Hz. The specific table's2121µA leakage conflicts with the general series0.01CV expression (5000µA); the larger5mA is used until conditions are reconciled. Neither figure establishes full-temperature leakage. Lead/slot drawing, vent space, inrush, ripple, heat and populated fit remain unqualified. A larger capacitor is not a drop-in native footprint change.

The [domestic courier policy](https://www.szlcsc.com/help/202.html) names SF, EMS and ZTO and makes freight depend on weight/checkout. Together with domestic stock, this supports a Shanghai sourcing route; it does not quote an exact address or reserve inventory. The engineering rejection remains even though the part has a plausible purchase route. No order or supplier message was sent.

The retained [Triad VPT36-1390 manufacturer sheet](https://catalog.triadmagnetics.com/asset/vpt36-1390.pdf), October12,2021, confirms the50VA reference's12% typical regulation, dual18V,115/230V inputs and83mm maximum diameter/36mm body height plus3mm mounting allowance. Typical regulation is not winding tolerance or a guaranteed DC-resistance model. A Chinese in-stock route for this exact transformer remains missing.

[Omron's relay precautions](https://www.ia.omron.com/product/cautions/36/safety_precautions.html) support investigating faster release with revised coil suppression. That general guidance does not establish G5V-2 timing or permit exceeding the AO3400A30V rating. Both native local and remote clamps must be considered together; adding a zener while leaving a parallel ordinary flyback path would not achieve the intended clamp voltage.

## Verification and remaining boundary

check_brownout_timing.py verifies report/source hashes,64 primary cases, retained failures, timing arithmetic, three negative controls and22 native CAD files. It independently solves2000 divider nodes and checks two post-collapse capacitor discharges against closed-form equations (errors below0.04µV). These verify the calculations, not transformer accuracy, regulator behavior or contacts. Source/reference/logic supply sequencing, suppression choice, exact socket/carrier and resistor selection remain open. The model does not address individual rail shorts or guarantee silence for arbitrary hard faults.

Human check: with eventual exact components, measure raw rails, REF5/RAIL_OK, regulated rails, coil current and K3 contacts during slow brownout and recovery at load/temperature. Verify the amplifier also reliably unmutes at the lowest healthy line. All six scopes remain incomplete; no manufacturing release.
