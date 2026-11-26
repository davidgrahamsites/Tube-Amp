# Package names were not enough: regulator contacts and rectifier integration

**Source checkpoint:** 24–26 November 2026; VAL-073 and VAL-074

**State label:** documented/verified bounded checks; no regulator contact selected; rectifier identity/package integration recorded

**Baseline:** exact baselines are revision-bound in the linked reviews; journal checkpoint `d5566cd`.

## The problem

Once component identity and package geometry became release gates, two interface problems surfaced. First, power regulators were expected to remain serviceable while transferring heat to a shared sink. Common socket names and headline current ratings did not show that the regulator's rectangular lead tolerances fit the socket, nor that a previously inserted larger lead could be replaced later. Second, D3–D6 had conflicting identities across source, readable schematic, and Power board: the source said 1N4007, the board STTH112, and the footprint DO-41, while the selected design intent was BY255P-E3/54 in a two-series-diode-per-half-winding topology.

The two issues share a lesson about interfaces, but their engineering outcomes differ: the contact screen rejects several candidate fits without choosing a replacement; the rectifier task reconciles an already selected part identity and integrates its actual package.

## Requirements and authority

The default requirement that components be serviceable remains in force; no socket exception or contact adoption is recorded. The exact contacts require full-lead-range acceptance, replacement retention, thermal/current ratings, mechanical retention, isolation, and a sourcing route. For the rectifiers, the selected BY255 identity is preserved while correcting stale representations. Manufacturer evidence and project engineering reviews define the bounded package/rating checks; passing CAD integration does not certify transformer stress, thermal conditions, or fabrication tolerances.

## Evidence and reasoning

For ST L78/L79 leads, independent extrema from the manufacturer drawings give a diagonal range of 0.7762–1.1245 mm. This is a geometric inference, not a sample measurement. Mill-Max #34 misses the smallest lead and, after the largest lead has been inserted, its minimum replacement lead rises to 0.8705 mm. #36 cannot accept the maximum diagonal by 0.0577 mm. #18 fails both ends. Thus those three exact contact candidates do not cover the full published regulator lead range as a universal replaceable socket. This conclusion does not rule out other contacts or a keyed part/contact pairing.

The cooling calculation carried forward from the auxiliary-supply owner peaks at 4.286827 W total conditional heat across four regulators. Under the stated 60°C ambient, 100°C junction target, and 1°C/W case-to-sink assumption, the shared sink must be no more than 7.3961°C/W. This is a conditional thermal requirement, not a selected heatsink, actual cabinet ambient, or fault/startup qualification. Mechanical support must carry the heatsink independently, isolate U7's tab, preserve fastener access, and allow regulator extraction; socket contacts must not carry heatsink or service loads.

For D3–D6, Vishay's BY255P-E3/54 maximum lead diameter is 1.32 mm. The custom footprint uses 1.7 mm round holes and 2.6 mm pads, with a proposed ±0.1 mm finished-hole allocation. The minimum hole leaves 0.28 mm diametral lead allowance. Four diodes moved vertically within the Power board and supporting resistors/headers moved to keep the stated HV clearance rule. The diode topology and all 145 net groups were retained. The provisional 3 mm standoff and 8.3 mm height are assembly envelopes only.

## Options and tradeoffs

Contact candidate screening shows why a nominal “fits this package” result is not enough for serviceable equipment: tolerance extremes and replacement cycles can change acceptance. No candidate in the screened set satisfies the full range, so retaining the default socket requirement means finding a purpose-built flat-lead contact or documenting a specific regulator/contact pairing. For rectifiers, retaining the selected diode topology while repairing identity and footprint avoids silently substituting electrical architecture. However, the existing generic diode model cannot prove BY255 pulse loss or reverse-voltage stress.

## Decision and native change

VAL-073 is a documented no-selection boundary. The three tested contact fits are not adopted; the default socket requirement remains. VAL-074 records consistent BY255P-E3/54 identity across source, readable schematic, and Power PCB, with native package and placement integration. It does not change the two-series-diode topology and does not declare fabrication readiness.

## Verification and limits

Contact arithmetic includes virgin-fit and replacement-fit controls; all three exact candidates fail at least part of the full lead range. VAL-074's guarded native integration check preserves 145 net groups and all 20 other native files; only the four value labels change on one schematic page. Excellon accounts for all 79 holes, with eight diode holes and six support-component holes moved; other holes remain unchanged. ERC's existing GND/PE warning and Power's 12 existing DRC findings/39 unconnected items remain without new findings under unchanged rules. The board is not fully routed or populated, and width preservation does not qualify ampacity.

## Remaining tests and next action

Identify an exact purpose-built flat-lead contact or regulator/contact combination that meets full tolerance and replacement requirements, then confirm plating, retention, current derating, supplier identity, sink insulation and cabinet airflow. For the rectifier stage, qualify transformer regulation/leakage, repetitive pulse and average loss, startup/fault energy, hot junction temperature, transient reverse voltage, trace capacity, and the populated three-board fit. Confirm actual fabrication hole tolerance before release.

## Physical-build placeholder

Capture actual regulator leads and contact gauges, insertion/replacement cycles, contact temperature and extraction forces; measure mounted heatsink interface and insulated U7 tab. For rectifiers, photograph exact part markings and lead forms, inspect soldered clearances, measure board holes, and log temperatures/current waveforms only under a documented safe test setup. None of those observations is present in the cited validations.

## Reusable lesson

A package is an interface contract across part tolerances, contacts, service life, thermal paths, and manufacturing. Check full ranges and replacement conditions before freezing a footprint. When a selected part is correct but representations disagree, repair each representation under a revision-bound native check and keep electrical qualification separate.

## Sources

- [VAL-073](../../../brain/records/VAL-073-regulator-contact-tolerance.md), [contact review](../../../engineering/component-selection/socketing/contact-review.md)
- [VAL-074](../../../brain/records/VAL-074-rectifier-package-integration.md), [rectifier integration review](../../../engineering/whole-amp/pcb-measured-r/rectifier-package/review.md)
