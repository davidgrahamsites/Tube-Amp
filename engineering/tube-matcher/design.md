# Renegade tube matcher — design v0.1

October 4, 2026. **Proposed system design, not construction-ready.** Scope: two **EL34s** and four **12AX7s**, with standalone Raspberry Pi touchscreen operation and BLE result transfer to macOS. More tubes can be inventoried later. No real tubes have been measured.

## 1. What the tool should do

Insert one tube, identify it, close the guard, choose its profile and press the physical TEST button. The instrument screens for faults, warms the tube, records its electrical fingerprint and recommends a bin or amplifier role. Label each tube with an inventory ID. Test all six under identical conditions, then select the EL34 pair and allocate the four 12AX7s.

- **EL34 pair:** compare actual plate current at common fixed grid/plate/screen voltages, gm (change in plate current per change in grid voltage), bias required for a common target current, screen current, drift and several common curve points.
- **12AX7 internal balance:** measure sections A and B separately, with the same measurement channel and fixture; compare current, gm and estimated mu. Both halves may be healthy without matching.
- **12AX7 across bottles:** retain two section fingerprints for every tube. Pick a balanced, stable candidate for V4; reserve the quietest, least microphonic healthy candidate for an early gain stage once audio tests exist. Assign remaining tubes by the actual stage needs, not a universal strength score.
- **Binning:** categorical storage label plus numeric data. Bin membership is a search aid, never automatic proof of a match.

With only two EL34s, the result can be **pair acceptable**, **uncertain/retest**, or **no suitable pair**. The instrument cannot improve a mismatched pair; another candidate or an independently adjustable amp bias arrangement may be required. It cannot predict remaining lifetime or certify the completed amplifier.

The four original 12AX7s do not all need identical characteristics. The source V4 phase inverter uses 82 kΩ and 100 kΩ plate loads. Prefer section balance as an initial selection signal; verify actual output balance/headroom in the completed circuit. Added reverb tubes, including the proposed 12AT7, require separate later profiles.

## 2. Architecture and construction choice

**Recommended:** Pi 4 with 7-inch Touch Display 2, a Pico/RP2040 measurement controller, a protected analog/HV board and interchangeable socket cartridges. Pi provides touch UI, SQLite inventory, curves and BLE; the controller owns the test state machine. Independent analog protection can remove power even when either computer stops.

```text
220 V / 50 Hz wall supply
        |
Certified isolated 24 V / 5 A external adapter (candidate requirement)
        +--> fused logic converter --> Pi + touchscreen + BLE --> Mac client
        |                                  |
        |                           isolated serial link
        |                                  |
        +--> analog supply --> Pico controller + precision ADC/DAC
        |                          |             ^
        +--> heater regulator -----+             | electrode measurements
        +--> plate HV converter / regulator -----+
        +--> screen HV converter / regulator ----+
        +--> negative bias supply / driver -------+
                         |
             hardwired inhibit, cutoff and discharge
                         |
             keyed EL34 OR 12AX7 cartridge
                         |
               tube under interlocked guard

Guard / STOP / bias-present / rail-fault / watchdog --> hardware inhibit
```

One active tube at a time avoids six-channel power and fixture differences. Two EL34 sockets are unnecessary for matching: repeatable sequential measurements are sufficient. A simultaneous pair fixture is a later thermal/interaction test, not a first-version requirement.

Use a 24 V external supply so internal work is on DC conversion. HV remains hazardous despite the low-voltage input. Provide a guarded, inaccessible HV compartment, an RF-transparent region for the Pi antenna, physical TEST/STOP controls and a rail-driven HV indicator. The STOP control interrupts the hardware permit chain. Exact enclosure material, bonding/insulation method and clearances must be resolved in the electrical/mechanical review.

## 3. Supply and measurement interfaces

Ranges below are **instrument design targets**, not instructions to apply maximum voltage/current to a tube. Default profiles stay at or below 250 V; software limits, comparator thresholds, tolerance and stored energy must all be included in the final schematic review.

| Interface | Proposed range / capacity | Essential behavior |
|---|---|---|
| Heater | 0–6.3 V DC, 2 A continuous; short inrush allowance only after review | Soft start; measure at socket; default EL34 6.3 V/1.5 A, 12AX7 6.3 V/0.3 A. Separate fuse/electronic current limit. 12.6 V mode excluded initially. |
| Plate | 0–300 V DC, 100 mA hardware capacity | Actual permitted envelope depends on tube/profile. Current limiting, HV-rated output isolation, bleeders, physical shutdown. HV converter/pass device part numbers unresolved. |
| Screen | 0–300 V DC, 20 mA capacity | Independent regulator, current measurement and current limit; only EL34 cartridge. Screen enabled after plate is established, removed before plate on normal shutdown. Fault removes both immediately. |
| Control grid | −60 to 0 V relative to instrument return | Local stopper, low-impedance bias driver and measured Vgk. Default −60 V hold for EL34; −10 V hold for 12AX7. Loss of negative supply removes HV independently. No intentional positive-grid tests. |
| Cathode sense | 1 Ω Kelvin shunt for EL34; 100 Ω for DC 12AX7 characterization | Shunt raises cathode voltage: measure it and regulate/report Vgk and Vpk, not supply-to-ground values. Ranges switched only with discharged HV. |
| Screen sense | 10 Ω Kelvin shunt with floating isolated amplifier, ahead of socket screen | At 20 mA, 200 mV signal; actual socket screen voltage measured after shunt/stopper. Requires isolated local supply and qualified barriers. |
| Grid current | Protected, high-input-impedance measurement of grid drive/resistor drop | Selectable grid fixture; leakage/gas flag provisional until fixture leakage and bias-driver effects are calibrated. Do not infer gas solely from warming current drift. |
| Voltage readback | Heater, grid, cathode, plate and screen at cartridge terminals | HV divider strings with per-resistor voltage ratings, buffers, fault current limits and clamps. Independent hardware rail monitors do not share the only software ADC path. |

Candidate acquisition: two ADS1220 devices, one for current/shunt measurements and one for voltage channels; DAC80504 for four supply setpoints. Additional range/fixture switching is digitally controlled but mechanically/electrically inhibited under HV. All are candidates, not selected procurement items. The Pi/Pico internal ADC alone is insufficient for the stated precision targets.

Measured plate current is **Ip = Ik − Is − Ig**, with heater/cathode leakage assessed separately. For a 12AX7, Is=0. Cathode current alone must not be labeled EL34 plate current. An optional second isolated plate-current sensor can cross-check the subtraction. Buffer leakage, ADC offset, resistor drift and screen-subtraction uncertainty enter the error budget.

For 12AX7 gain/rp work, sample both sections through the same precision path to reduce channel mismatch. Complete each operating-point sample set while stationary; timestamp readings and ensure voltage/current samples correspond to the settled state. Shunt input conditioning must satisfy the ADC/PGA common-mode requirements using a reviewed level-shift or supported bypass arrangement; do not assume a ground-referenced shunt can feed every PGA setting directly. ADS1220 rates are suitable for DC work, not a 20 kHz noise spectrum.

### Preliminary acquisition numbers

- 100 Ω at 1.2 mA gives 120 mV and 0.12 V cathode elevation. At 3 mA it gives 300 mV: the selected ADC/PGA range must accommodate this, not saturate unnoticed.
- 1 Ω at 60 mA gives 60 mV cathode elevation; compensate the electrode voltages.
- 10 Ω screen shunt at 10 mA gives 100 mV and dissipates 1 mW. Fault ratings still govern part selection.
- A 16-bit full-scale 60 V bias span has an ideal 0.916 mV step. At the JJ EL34 example gm of 11 mA/V this represents about 10.1 µA current change. DAC linearity/reference/driver accuracy and measured voltage settling, not nominal resolution, set accuracy.
- Proposed readback/calibration goals: electrode voltage ±(0.2% reading + 0.1 V), grid-to-cathode ±2 mV locally, heater ±1%; plate current ±(0.5% reading + 5 µA); gm expanded uncertainty ≤2% and session repeatability ≤1%. These are acceptance targets, not demonstrated performance. A full uncertainty budget may force tighter hardware or looser matching limits.

## 4. Socket cartridges and pin mapping

Use one touch-protected keyed cartridge interface carrying plate, grid, cathode A/B, screen, heater H1/H2, heater reference, shield/reference, low-voltage ID and guard contacts. The actual connector must be rated and reviewed for HV, temperature, creepage and insertion sequencing; a breadboard header or generic USB connector is not suitable. Cartridges may be changed only after measured discharge. Cartridge ID permits only its tube family's profile; it does not identify the actual tube in the socket.

| Function | EL34, octal | 12AX7, noval |
|---|---|---|
| Plate | 3 | A:1, B:6 |
| Control grid | 5 | A:2, B:7 |
| Cathode | 8 | A:3, B:8 |
| Screen | 4 | none |
| Suppressor | 1, connected to cathode 8 in tester | none |
| Heater | 2 and 7 | pins 4 and 5 joined as one terminal; pin 9 other terminal, for 6.3 V |
| Unused | 6 unconnected unless exact manufacturer drawing requires otherwise | none |

These are standard family mappings for design review. Validate against the selected manufacturer's bottom-view drawing, the purchased socket and an unpowered continuity test before wiring release. Do not confuse socket-side and tube-bottom views. Do not wire a 12AX7 6.3 V heater across pins 4 and 5 alone. The suppressor connection makes this an EL34 cartridge, not a universal octal cartridge.

For 12AX7 section A testing, connect only A plate/grid/cathode to the measurement fixture; hold the inactive plate and cathode at return and inactive grid at its cathode reference. Switch only after discharge, then test B through the same channel; heater remains common. Guard both socket openings or physically cover an unused fixed socket. **Correct tube type is confirmed by the operator**, especially because many unrelated noval/octals fit mechanically.

## 5. Profiles and test sequence

Profiles in `profiles.json` are non-executable design data and explicitly unreleased. They must not become energizable firmware recipes merely by clearing a flag. Tube-specific current/power limits, fast analog protection and reviewed firmware are prerequisite.

### 12AX7 reference characterization

- Heater 6.3 V; initially all electrode HV off and grid at hold bias.
- Reference point: measured Vpk=250 V, Vgk=−2.00 V, cathode fixture referenced to return. Manufacturer typical 1.2 mA / 1.6 mA/V is descriptive, not a required minimum or pass threshold.
- gm: measure at Vgk=−2.10 and −1.90 V with Vpk held constant. Return to center between excursions; use forward/reverse order to expose drift/hysteresis.
- rp: at Vgk=−2.00 V, use Vpk=240 and 250 V; calculate incremental rp over this explicitly reported interval. A symmetric 240/260 V sweep is a later option after its limits are reviewed.
- Secondary point: Vpk=150 V, Vgk=−1.50 V; compare both sections there too. Additional safe curve points can be added later.
- Revision 0.1 proposed stop limits per active section: Ip 3 mA, plate dissipation 0.75 W, measured Vpk ≤250 V for reference tests. Current-limited or clipped points are marked **censored**, not silently included in gm or pairing.
- Optional loaded-stage fixture: B+ 250 V, Ra 100 kΩ, Rk 1.5 kΩ, selectable cathode bypass, defined output load. This is a separate self-biased fixture mode; 250 V B+ does not mean 250 V at the plate. Record actual quiescent electrode voltages. Required for measured voltage gain, clipping and noise comparisons.

### EL34 comparison profile

- Heater 6.3 V / nominal 1.5 A; hold bias −60 V before HV. Ramp plate first, then screen, while retaining hold bias and watching both currents.
- Repeatable fixed-bias anchor: Vpk=250 V, Vg2k=250 V, Vgk=−20.00 V. **No expected current is assigned**; measure it. If this point does not yield a useful, permitted current for the actual tubes, qualify a different shared profile and retest the entire comparison set.
- Common fixed-bias curve: Vpk={150,200,250} V, Vg2k=250 V, Vgk={−22,−20,−18} V, only while measured current/power stay within limits. Low plate/high screen conditions need especially close screen-current limiting. All common safe points retained; near-cutoff readings excluded from normalized shape scores.
- Separate bias-demand test: Vpk=250 V, Vg2k=250 V, servo Vgk between −50 and −5 V toward Ip=40 mA. Record required bias and local gm. If the target cannot be reached within limits, mark this test incomplete. Never extrapolate or force it.
- gm around each valid anchor: measured Vgk ±0.10 V, actual plate and screen held constant. Changing both plate and screen while estimating gm would measure a different quantity.
- Proposed stop limits: Ip 60 mA, Is 10 mA, Ik 80 mA, plate dissipation 15 W, screen dissipation 2.5 W. Limits are deliberately below the cited JJ maximum dissipation. Hardware trip thresholds/tolerances must enforce a compatible envelope. They do not authorize screening at all maker maximum ratings.
- The JJ EL34 datasheet example is 250 V / 265 V / 100 mA, at 25 W plate dissipation. **Do not make that maximum-dissipation example the unattended default.** Our lower-current comparison profile is an engineering proposal.
- Generic profiles do not establish matching at the amplifier's eventual higher B+. Revision 0.1 supply ceiling is 300 V; if the finished amp operates above it, use a separately designed extended-range instrument or confirm at amp operating conditions during reviewed commissioning. Do not exceed this tester's range.

### State machine

```text
OFF / DISCHARGED → IDENTIFY → COLD CHECK → HEAT
→ BIAS CONFIRMED → HV RAMP → STABILIZE → DC POINTS → OPTIONAL AUDIO
→ HV OFF / DISCHARGE → RESULT / GUARD RELEASE
Any fault → LATCHED INHIBIT → DISCHARGE → LOCAL ACKNOWLEDGEMENT
```

Cold checks use a separate low-energy continuity/leakage source, HV inhibited and capacitor discharge verified. Scan heater continuity and unexpected electrode conduction against tube-family known internal ties. Define test voltage, current ceiling, dwell and trip thresholds in schematic revision; a low-voltage screen cannot certify hot/HV insulation. Hot leakage tests at realistic electrode stress need a reviewed fixture and qualified acceptance thresholds.

Warm for a proposed minimum 120 s and then require ≤0.5% current drift over the final 30 s at a valid operating point; use a 300 s initial timeout and flag instability. Temperature and warm-up time are retained. These timings are qualification starting points, not manufacturer requirements. Never escalate a drifting tube's test voltage to force stabilization.

Run raw traces and fault events into the controller's buffered record; transfer them to the Pi. Session reference tube at start/end, repeated insertion of at least one tube, and A/B order reversal detect instrument drift/contact effects. Repeat critical comparisons after an uncertain result.

## 6. Equations, pairing and bins

All electrode voltages are relative to the **actual cathode**. Use real measured grid steps.

```text
gm [mA/V] = (Ip at Vg+ − Ip at Vg−) / (measured Vg+ − measured Vg−)
rp [kΩ] = (Vp_high − Vp_low) / (Ip_high − Ip_low), with current in mA
mu ≈ gm [mA/V] × rp [kΩ], at the same local operating region
mismatch(x,y) [%] = 200 × |x−y| / (|x|+|y|)
plate power [W] = measured Vpk × Ip [mA] / 1000
screen power [W] = measured Vg2k × Is [mA] / 1000
```

mu is an estimated intrinsic amplification factor, not loaded-stage voltage gain. DC slope estimates may include curvature; report intervals and do not combine widely separated points as a precise local mu.

**Proposed acceptance:** EL34 pair ≤5% plate-current mismatch at the common fixed-bias anchor and ≤10% gm mismatch, with safe, stable comparable screen behavior; multi-point current-curve mismatch RMS ≤10%, at least three valid common points above 5 mA and including the anchor. 12AX7 balanced tag requires A/B current ≤5%, gm ≤5% at reference, and no material divergence at secondary point. All thresholds are adjustable engineering preferences and require real instrument qualification, not industry-wide standards.

Add measurement uncertainty before accepting a pair. For positive quantities with absolute uncertainty bounds, evaluate mismatch at all four interval endpoint combinations and use the maximum. Accept only when that worst-case value fits the threshold; if central values fit but uncertainty does not, report **uncertain/retest**. A zero/negative or censored input is unavailable for matching, not a perfect match. Gain/noise scores require their own fixture identity and calibration.

Curve score uses common fixed-bias points, never two independently servoed currents. Same current achieved with different grid bias does not prove the tubes match. Rank only profiles with matching family/variant compatibility, profile revision, measured setpoints within tolerance, calibration validity and complete required tests. A bias-demand difference is informative; it does not replace fixed-bias matching.

### Storage labels

- EL34 coarse bins: **2 mA current intervals** at the fixed-bias anchor, **1 mA/V gm intervals**, plus stable/unstable/fault. Example syntax `EL34-P01-I[38,40)-G[10,11)-S`. Bin boundaries are half-open intervals in measured units. Compare numeric values across adjacent bins before selecting a pair.
- 12AX7: section-current bins of **0.10 mA**, section-gm bins of **0.10 mA/V**, plus balanced/unbalanced/uncertain/untested, quiet/noise-untested, microphonic/microphonics-untested. A bottle retains both section labels.
- Low current or gm is a characteristic until a validated functional lower limit is available. Keep **fault**, **weak for this role**, **healthy**, and **untested** distinct. Matching does not mean health, and two weak or faulty tubes do not become acceptable by matching.
- Save original values even if bin widths or pair thresholds change. Never pool measurements from unrelated voltages, makers requiring different limits, or uncalibrated revisions.

Illustration only: EL34 readings 40.0 and 41.2 mA have 2.96% central current mismatch. gm 10.5 and 10.8 mA/V have 2.82% mismatch. With ±1% uncertainty on each value, the conservative mismatches become about 4.96% and 4.82%. They pass these two proposed gates; full pairing still requires health, drift and curve checks. No actual tube quality is implied.

## 7. Noise, gain and microphonics extension

Do DC matching first, but show **audio tests not performed** until the audio module is qualified. The initial version cannot honestly label a tube quiet or low-microphonic from current/gm alone.

Audio cartridge fixture: defined loaded triode stage, AC-coupled protected output attenuator, low-noise preamp and 24-bit/48 kHz audio acquisition candidate; separate calibrated stimulus for gain. Source termination, gain, bandwidth, cathode bypass, shielding, heater method and supply ripple are part of the profile. There must be no possible HV path to a consumer audio interface or the Pi.

- Noise: grid terminated with specified source resistance, measure 20 Hz–20 kHz output RMS and 50/100 Hz components; derive input-referred noise using measured gain. Include fixture baseline. DC-heater results do not prove hum performance with the original amp's AC heater scheme.
- Microphonics: reproducible low-energy mechanical excitation of the fixture, fixed position/amplitude, measure output peak/decay and baseline. A casual finger tap is a manual observation, not a standardized bin threshold. Avoid striking hot glass.
- Gain/headroom: small-signal sweep and clipping behavior in the defined load fixture; intrinsic mu alone is insufficient. Exact cathode-follower or elevated-heater stress tests need the amp's reconciled topology and additional qualified profiles.

Until this extension exists, the UI may suggest “balanced candidate for V4,” but must show “input-stage quietness unknown.” Retain manual in-amp noise/microphonics observations separately from calibrated instrument measurements.

## 8. Benchtop display and macOS connection

Pi 4 with 2 GB or greater is a reasonable candidate; reuse an existing suitable Pi if available. Proposed 7-inch Touch Display 2 in landscape gives a 1280 × 720 logical layout. Exact thermal, OS/display and BLE integration must be checked on the purchased revision.

**Primary screen:** tube ID and verified family; cartridge; profile/calibration; heater and electrode readbacks; test phase; explicit HV/guard state. Results view has section A/B comparison, EL34 pairing table, curve plot, bin label and all unperformed/invalid tests. Maintain touchscreen targets of approximately 10 mm and physical TEST/STOP controls; a touchscreen alone does not authorize HV.

```text
RENEGADE TUBE MATCHER                    Inventory | Export
Tube: AX7-003       12AX7       Profile T01       CAL-001

Section A              Section B              Internal balance
Ip 1.20 mA             Ip 1.22 mA              Current 1.65%
gm 1.60 mA/V           gm 1.62 mA/V            gm      1.24%

Balanced candidate for V4 — requires calibration uncertainty gate
Noise: NOT TESTED       Microphonics: NOT TESTED
[View curves] [Compare inventory] [Export result]

HV DISCHARGED — guard release allowed only by hardware monitor
```

Values above are synthetic UI examples. In a running test, the bottom status comes from controller/independent rail monitors, not a UI timer. Pi service stores records transactionally, retains raw samples, and marks interrupted runs incomplete. On reboot, resume the inventory view; never resume HV automatically.

**BLE:** Pi runs a BlueZ custom GATT peripheral, Mac runs a Core Bluetooth central application. BLE transfers status and results; pairing/bin calculations remain available locally even when Mac is disconnected. This requires software implementation and an actual Mac/Pi radio test; it is not an already working feature. Browser-only Mac BLE is not the primary interface.

Proposed protocol version 1, custom 128-bit service UUID, characteristics:

| Characteristic | Access | Payload |
|---|---|---|
| Instrument info | read | protocol/hardware/firmware/schema version, serial and capability flags |
| Status | read/notify | controller state, run ID, physical interlock flags, readbacks, fault code |
| Result manifest | read | completed run ID, family/profile/calibration ID, result byte count, SHA-256 |
| Transfer request | write with response | completed run ID, first requested chunk index; no electrode setpoints |
| Result chunks | notify | transfer ID, index, count, length and data; client checks whole-record digest and requests missing chunks |

Segment to negotiated MTU minus ATT/header overhead; support the default 20-byte ATT value payload rather than assuming large packets. Use explicit fixed-width units or a versioned JSON record transferred in chunks. Completion persists on the Pi before advertising the result. Authorize the Mac through local pairing UI and suitable authenticated bonding; no automatic HV start over BLE in v1. Loss of BLE does not interrupt a locally running test; loss of Pi/controller supervision does.

Fallbacks: CSV/JSON export to storage, or a local Wi-Fi/Ethernet web interface if implemented. A Mac app should show curves, uncertainty, valid profile/calibration and recommended pairs, and export the same IDs as the Pi.

### Minimum stored record

Tube ID, maker/variant/markings, bottle photo optional, family and section, cartridge serial/revision, tester serial/revision, timestamp/session, profile ID+hash, firmware version, calibration ID+validity, temperature/warm-up time, actual Vh/Vpk/Vgk/Vg2k, Ip/Ik/Is/Ig, raw gm/rp samples, derived values and uncertainty, cold/hot fault checks, drift, audio fixture/results or explicit untested status, censored points, bin rule revision, pairing/role result and manual notes. Preserve raw data so later bin changes are reproducible.

The user also asked about writing a computer app here to track and receive measurements. The [app/data contract](app-data-contract.md) defines a native macOS candidate, inventory/history/curve views, local storage on both ends, resumable BLE transfer and a [synthetic import record](example-result.json). Software implementation remains uncompleted.

## 9. Protection, energy and mechanical review

Implement a hardware permit chain from guard contacts, physical STOP, independent negative-bias-valid detector, rail overvoltage/current comparators, thermal trip and external watchdog. Pico heartbeat must keep the watchdog alive; Pi heartbeat is supervised by the Pico. Faults latch and require local acknowledgement with rails discharged. Serial commands request profiles; controller independently checks cartridge/family and all limits.

Shutdown must turn off converters **and disconnect stored-energy sources from the socket**, connect discharge paths and maintain negative bias while necessary. Converter-enable alone does not remove charged capacitors. Fail-safe HV switches/relays need real **DC** breaking ratings and single-fault review; an AC contact rating is insufficient. Plate-present must gate screen permit. Independent screen overcurrent trip acts without waiting for software power calculations. A disconnected ADC, stuck DAC, stuck relay, bias loss and controller reset are explicit fault cases.

Guard release requires independently sensed plate, screen and accessible bias nodes below a proposed **10 V magnitude for ≥1 s**, reliable sensor health and no stored-energy path that can re-energize the socket. Do not infer discharge from elapsed time. Also establish a qualified cool-down/handling condition: electrical discharge does not make hot EL34 glass safe to touch. A lock that stays closed with power removed needs a defined safe manual service procedure; exact hardware mechanism unresolved.

Preliminary energy example: each plate/screen rail has at most 22 µF directly associated with its output; at 300 V that stores 0.99 J. A 100 kΩ permanent bleeder starts at 0.9 W and reaches 10 V ideally in 7.48 s. A separate 10 kΩ switched discharge path starts at 9 W, with 0.99 J pulse energy and ideal 0.748 s to 10 V. These numbers exclude upstream capacitors and wiring. Real total capacitance, tolerance, voltage rating and resistor pulse curves govern final design; all upstream paths must be included. The report deliberately does not use these times to release the guard.

Plate+screen maximum output capacity is 36 W; heater is 12.6 W. At assumed 75% conversion efficiency that is 64.8 W input, plus a 20 W Pi/display allowance and 5 W measurement/fan allowance: 89.8 W. A 120 W input adapter gives roughly 30 W allowance in this initial budget. Continuous converter/pass-device losses need review: a 300→150 V linear drop at 60 mA would dissipate 9 W in the plate regulator alone. Track raw HV to setpoint or design adequate thermal management. Do not mistake tube plate power for regulator heat.

No enclosure dimensions or fabrication holes are assigned from a concept. Required geometry register: display drawing/cutout, Pi antenna and cooling zones, socket/tube max envelopes, guard travel/lock, HV partition, board envelopes, heat-sink paths, connector/fuse access, harness bend space and assembly/service order. Common units are mm; datum/orientation and tolerances are declared when actual parts are selected. Thermal review must include the EL34 glass and screen/plate heat under the guard.

## 10. Qualification and next implementation gates

1. **Schematic review:** choose exact external adapter, converters, pass devices, ADC front ends, bias driver, isolated screen sense, DC cutoff parts, guard/lock and sockets. Produce KiCad sheets and component stress/spacing/error budgets. Resolve family pin drawings and nominal/fault thresholds. No parts purchased by this design request.
2. **Unpowered and resistor-load verification:** continuity/pin maps, reference/protection paths, supply polarity and cold-check injection limits. Calibrate voltage/current channels with traceable instruments and suitable resistor loads before using tubes. Correlate screen subtraction and cathode sense; cover low-current and high-current ranges.
3. **Fault qualification:** independently demonstrate guard-open, STOP, missing bias, plate loss with screen present, sensor disconnect, stuck setpoint, serial loss, Pico reset, Pi crash, power removal and a credible welded/stuck cutoff fault. Record overshoot, peak energy/current and measured discharge at every accessible electrode.
4. **Metrology:** verify heater regulation under EL34 load, supply ripple, long-term drift, profile repeatability, ADC saturation handling and actual uncertainty. Repeat tube A-B-A order and socket reinsertion. Establish reference-tube checks without treating a tube as an absolute calibration standard.
5. **Real tube comparisons:** retain identity and actual results; compare gm/current with another calibrated method if available. Qualify limits and proposed matching tolerances for the user's exact tube variants. Only then turn inventory labels into trusted pairing decisions.
6. **Audio and amp-specific extension:** qualified noise/microphonics fixture; actual amp bias/screen/plate points and V4 behavior; higher-voltage or heater-elevation capability only through a separate reviewed revision.

This revision completes the system/interface design and reproducible calculations. It leaves transistor-level schematic, firmware, working touchscreen/BLE software, procurement BOM, physical assembly and energized validation explicitly uncompleted.
