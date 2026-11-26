# Heater elevation: a normal divider was not the whole fault story

**Source checkpoint:** 26 November 2026; VAL-075

**State label:** rating boundary documented; current R506 selection held under expanded conditions

**Baseline:** review source-bound to `78919a2`; current journal checkpoint `d5566cd`.

## The problem

The heater-reference divider already had a normal-operation screen. Extending the question to resistor voltage and dissipation under component faults changed the conclusion: R506 could exceed both its selected continuous-voltage and temperature-derated power limits if C505 shorts at the 550 V engineering ceiling. A wattage-only substitution would still leave distinct R507-open and upper-feed-short hazards at the heater reference and tube interface.

## Requirements and authority

The project requires applicable stress and package ratings for every part; this chapter describes the engineering qualification, not a new user selection. The 550 V figure is an extended engineering ceiling in the review, not a measured transformer limit. Five-percent initial resistor tolerance combined with a separate five-percent drift allocation is a declared engineering allocation, not a guaranteed lifetime bound. Actual tube heater-to-cathode limits must be exact-part sourced before choosing the complete correction.

## Evidence and reasoning

The 220 kΩ/39 kΩ divider with 47 µF was evaluated at three supply cases: the historical 510.312 V simulated peak, 522.693 V ideal peak under existing transformer assumptions, and 550 V extended ceiling. Four thousand thirty-two DC corners cover normal operation, C505 short, R507 open, and a short of the entire upper feed. Independent power-balance checks pass. Eight zero-charge RC startup runs agree with analytical settling within 7.668 µV; longest 1% settling is 9.486 s. The passive model uses a stiff ideal source and no tube/heater leakage, so it bounds a simplified network rather than a fully powered amplifier.

At 100°C and 550 V, normal R506 is bounded by 480.301 V and 1.09926 W; the existing 2 W FMP200's declared derated allowance is 1.29412 W at that temperature and its continuous-voltage limit is 500 V. In the C505-short case R506 reaches 550 V and 1.52355 W, exceeding both. The screen does not credit a datasheet pulse overload as an indefinite fault rating.

Three alternatives pass only that bounded resistor case: Vishay PR03 copper-lead 220 kΩ (750 V, 3 W at the stated reference temperature, with a new larger envelope); Yageo FMP300 220 kΩ (750 V with its own derating and larger body); or two 110 kΩ FMP200s in series, each carrying a lower share in the modeled split. They are not drop-in packages and remain alternatives, not adopted parts. Exact China availability, lead forming, heat transfer to nearby capacitors, and installed temperature remain unqualified.

Separate faults remain important. In the isolated model R507 open can eventually raise HREF and C505 toward 550 V. A short across the entire upper feed drives the lower resistor to 8.59436 W. For the two-resistor alternative, a short of one resistor is a separate condition from a short of the whole feed and is not yet evaluated. No one resistor rating resolves every failure mode.

## Options and tradeoffs

A larger single resistor may solve the stated C505-short continuous rating bound but needs more board envelope and still does not protect HREF/C505/tube interfaces from other faults. Two series resistors distribute voltage and dissipation in the modeled case, but introduce a single-resistor short condition and additional package/fit questions. A clamp or redundant divider could address different faults but must be checked for normal loading, open/short behavior, hot limits, and exact tube limits. The review directs selection of the least intrusive complete correction only after that fault policy is defined.

## Decision and native change

VAL-075 places an explicit hold on the current R506 selection under expanded conditions. PR03, FMP300, and two-series-FMP200 are recorded as bounded alternatives, not decisions. The review states that all 22 schematic/PCB files remain unchanged; no circuit or package substitution is adopted.

## Verification and limits

All 4,032 corner cases and eight analytical RC comparisons have independent arithmetic checks. The values support the stated passive-network bound only. They do not establish the real transformer ceiling, tube leakage, exact heater-cathode safety, component pulse capability, installation temperature, or a complete fault correction. The no-native-change result is part of the evidence and should remain visible in future retellings.

## Remaining tests and next action

Define the heater-reference fault policy using exact tube heater-to-cathode limits. Evaluate the complete correction across normal load, component opens/shorts, startup, hot operation, resistor short within a series pair, and upper-feed fault. Then choose exact sourceable parts, package/lead-forming geometry, and thermal spacing before native integration and refreshed PCB/fit checks. Keep manufacturing release blocked until the broader build gates close.

## Physical-build placeholder

Record actual tube types and manufacturer limits; actual divider parts and markings; heater/HREF voltages under operating conditions; local resistor and capacitor temperatures; startup and defined fault responses; and populated chassis clearances. Do not perform fault tests without a documented safe high-voltage procedure and suitable instruments. No such build evidence is cited here.

## Reusable lesson

For high-voltage dividers, qualify both normal operation and each credible component fault. Voltage rating, power derating, pulse behavior, capacitor stress, tube-interface limits, and package heat are separate checks. A larger wattage number is not automatically a system-level protection solution.

## Sources

- [VAL-075](../../../brain/records/VAL-075-heater-divider-rating-boundary.md)
- [Heater-divider review](../../../engineering/component-selection/heater-divider-rating/review.md)
- [Source-bound corner results](../../../engineering/component-selection/heater-divider-rating/results/)
