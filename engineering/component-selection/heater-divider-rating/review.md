# Heater-elevation resistor voltage and heat boundary

November 26, 2026. Task HD-001 extends the older normal-only R506/R507 screen without changing the functional block or native circuit. The source is bound to commit78919a2. All22 schematic/PCB files remain unchanged.

## What the calculation establishes

The current divider is220k/39k with47µF to ground. Three supply levels are compared: the historical510.312V simulated peak,522.693V ideal peak under the existing transformer assumptions, and a550V extended engineering ceiling. None is a measured transformer limit. Initial5% resistance tolerance is combined with a separate ±5% drift allocation; this allocation is not a guaranteed lifetime bound. Local ambient cases are70/100/125°C.

4,032 DC corners cover the current FMP200 and three alternatives, normal operation, capacitor short, lower-resistor open and the whole upper feed short. Independent power-balance checks pass. Eight zero-charge capacitor startups agree with analytical RC response within7.668µV; the longest1% settling time is9.486s. The simulation uses an ideal stiff source and no tube/heater leakage. It is a passive-network bound, not a full powered amplifier simulation.

At100°C and the550V ceiling, normal operation bounds R506 by480.301V and1.09926W and HREF by97.9047V. The current2W FMP200 permits1.29412W at this ambient and500V continuous, so this normal screen passes. With C505 short, R506 reaches550V and1.52355W: both continuous limits fail. Initial charging also applies the full source voltage; no manufacturer pulse-overload exemption is credited in this screen. A transient overload test in a datasheet is not an indefinite fault rating.

| R506 implementation | C505-short maximum per resistor | Continuous allowance at100°C | Result |
|---|---|---|---|
| Current FMP200220k |550V /1.52355W|500V /1.29412W|Fail|
| PR03000202203JAC00, Cu leads |550V /1.52355W|750V /2.30769W|Bounded pass|
| FMP300JT-73-220K |550V /1.52355W|750V /1.94118W|Bounded pass|
| Two FMP200110k in series |302.431V /0.761773W|500V /1.29412W each|Bounded pass|

## Exact-part evidence and sourcing

The retained Yageo FMP V9 document supplies the FMP200/FMP300 ratings and geometry. The [Vishay PR document](https://www.vishay.com/docs/28729/pr010203.pdf), revision8July2025, is already retained under wet-protection/sources. Its PR03 copper-lead version is3W/750V, derating above70°C to zero at200°C; the graph was visually checked. The exact ordering code must retain copper leads: the FeCu variant has a different power rating. PR03 maximum body16.7×5.2mm, coated length19.5mm and maximum lead0.83mm require a new footprint and lead-forming envelope. FMP300 maximum body16.5×5.5mm and lead0.85mm also exceed the current package. Neither is a drop-in assembly.

[Supplier observations](results/source-observations.json) distinguish global indexed stock from a confirmed China order. DigiKey shows single-piece pricing for PR03 and FMP300; the110k FMP200 listing starts at5,000 pieces. China pages could not be read (including an HTTP403 on the PR03 page); this is not evidence of unavailability. No domestic stock, MOQ, Shanghai delivery or authenticity claim is made from a marketplace title or global page. The parts remain alternatives, not adopted selections. A local Taobao/Pinduoduo route remains permitted if traceable identity can be established.

## Separate faults and next action

R507 open can eventually raise HREF and C505 toward550V in this isolated model. A short across the entire upper feed additionally drives the lower resistor to8.59436W. Increasing R506's rating does not resolve these cases. A failed component's zero dissipation or zero capacitor voltage is not a reliability pass. For the two-resistor option, a short of one resistor is a different case from shorting the entire feed and remains to evaluate.

Next choose the complete heater-reference fault policy and correction, including heater-to-cathode limits of the exact tubes, before freezing R506. A local clamp or redundant divider arrangement must be checked for normal loading, failed/open behavior and hot limits. Prefer the least intrusive proven solution. Exact sourcing, lead forming, heat transfer to nearby capacitors, actual ambient and populated cabinet fit remain open. The existing selection is now explicitly held for these expanded conditions. Objective6 is incomplete; no manufacturing release.
