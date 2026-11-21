# Original amplifier source inspection

Received and inspected October 4, 2026. Source: [Renegade Tube Amp.pptx](<../../Renegade Tube Amp.pptx>), SHA-256 `5e2bca494bf6c9c81c61cfbdce5e4e2ac8458ad87ce4484ce45043bce83ae0ac`.

## Subsequent source comparison

Following the user's “Updated schematic” message on October 4, the current presentation has SHA-256 `00c43b64bb87dee26b7982b797921cbb307a56d60e0324fe06e7f86d9d6eecc9`. All three embedded image bytes, slide order, placement transforms and crop settings match the intake evidence. No editable slide text or additional circuit drawing shapes were found. The prior archive bytes are unavailable for a complete package diff; the reason for the package hash change is unknown. See [comparison report](revision-check-2026-10-04.json) and [VAL-007](../../brain/records/VAL-007-source-revision-comparison.md). The intake hash above and original manifest are preserved as historical evidence.

## Evidence and method
The presentation has three slides, each containing one embedded PNG and no editable drawing text. ZIP integrity passed. [manifest.json](manifest.json) maps slide relationships, original image members, hashes and transforms. Images were extracted byte-for-byte and visually inspected by the root agent and an independent reviewer. No source image crop or rotation is recorded in the slide XML. The original presentation was not changed.

The source drawings carry OpenValve / AX84, Renegade Channel Switching Amplifier, Antony Noel, date 10/17/2001, version 1.2. These labels establish source identity, not engineering approval.

Drawing notes are historical design commentary, not new user instructions. Optional changes mentioned in those notes have not been applied during intake.

| Slide | Extracted evidence | Content |
|---|---|---|
| 1 | [Preamp and channel switching](slide-01.png) | Separate clean/dirty paths, relay contacts, controls, effects send/return, relay supply and footswitch drawing. |
| 2 | [Power amp and supplies](slide-02.png) | V4 phase inverter, V5/V6 EL34 output pair, output transformer/taps, feedback/presence, bias network, rectification/filtering, mains/standby/heaters. |
| 3 | [Original BOM](slide-03.png) | Fifty printed BOM groups, transcribed in [bom-as-printed.csv](bom-as-printed.csv). Printed identities/values are retained; this is not a purchasing BOM. |

## What the source establishes
- The BOM specifies **four 12AX7s, V1–V4, and two EL34s, V5/V6**. Slide 1 depicts three dual-triode envelopes without clearly visible V1–V3 envelope labels; slide 2 identifies V4 a/b and V5/V6.
- The current proposed addition of one 12AT7 and one 12AX7 would make **eight tubes total** if retained. This is a proposed revision, not content of the original drawing.
- Original magnetic part labels: T1 Hammond 272FX, T2 Hammond 1650F and Choke1 Hammond 193D. The BOM identifies T3 as 120 VAC to 12 V centre-tapped; the relay drawing also labels the primary 120 VAC. Supplier replacements must be selected by requirements, not copied model names.
- The shared audio output passes through J3/J4 effects send/return before the phase inverter. That supports investigating the proposed shared reverb insertion region; loading/headroom and connectivity still require circuit analysis.
- The source shows relay channel switching and a pedal circuit, but contains no spring reverb or completed two-button debounced controller.
- The source note says preamp DC filaments were abandoned in favor of AC. A new heater plan must be explicit; do not silently assume DC operation or that heater hum is simulated accurately.

## Reconciliation and limits
The independent visual review found no definite resistor/capacitor value discrepancy between schematic and BOM at this intake stage. Detailed net-by-net capture remains pending.

| Item | Finding and required action |
|---|---|
| 100k resistor group | Enlarged visual review confirms `R12,R15,R21,R4,R7,R5,R22,R30,R31`. R21 is easy to misread as R2; the CSV records R21. |
| 1.5k resistor group | `R3,R8,R36,R37`; R38 is separately 56k. |
| Numbering gaps | R9 and C18 are absent from the BOM and were not found in the schematic review. Treat as numbering gaps, not missing parts without further evidence. |
| Reference case | `c2` is printed lowercase in the BOM; normalize only in a later reconciled engineering BOM with the mapping preserved. |
| LEDs | The BOM prints quantity 1 for `Led1,Led2`, while two LEDs appear in the preamp/pedal drawings. Reconcile pedal versus amplifier scope and quantity. |
| Jacks | Six phone jacks J1–J6 appear in the BOM, but the diagrams visibly label J1–J5. Resolve J6's function. J7 is the mains plug/inlet in the BOM without a visible diagram reference. |
| Dirty gain control | A 1M Log control is visible without a clear Vol2 reference; confirm its mapping during capture. |
| Ratings | Capacitor voltage ratings and most resistor wattages are absent. Fuse values 3 A and 500 mA are legacy source values, not reviewed choices for the revised mains design. Relay contact/coil details, diode stress, insulation and other ratings require evidence. |
| Power and fit | No measured output-power specification, operating voltages, physical chassis/cabinet dimensions, component envelopes or thermal results. Neither an EL34 pair nor a transformer name establishes actual delivered amp power or box fit. |

## 220 V / 50 Hz and selected-component simulation
The user explicitly requires the complete revision to suit Chinese 220 V / 50 Hz supplies and to be simulated with the chosen components. This includes the main HV/heater/bias supply and relay/control supply; internal voltages still follow the circuit's requirements. Preserve source values separately from new selections. Simulate the reconciled baseline before evaluating revisions, and link each selected part to its datasheet/model, pin mapping and stated model limitations.

Manufacturer checks on October 4 establish that the original [272FX](https://www.hammfg.com/part/272FX) is specified for **115 V / 60 Hz**, so it cannot simply be retained as the project's main transformer. The [1650F](https://www.hammfg.com/part/1650F) is specified **25 W, 7.6k centre-tapped, 4/8/16-ohm secondary**; that is a component rating, not measured amplifier power. The [193D](https://www.hammfg.com/part/193D) is listed **8 H, 150 mA, 75 ohms**, useful for an initial documented reference model. Confirm applicable drawing revisions and actual selected/replacement parts before design release.

The [372FX](https://www.hammfg.com/part/372FX) has a manufacturer-specified universal 50/60 Hz primary including 220 V. It is a comparison reference only, not a selected purchase or a completed load-budget match. Its 6.3 V / 5 A winding and total rating still need evaluation with reverb, lamps and the chosen tubes; China sourcing and cabinet fit remain separate requirements.

## Next work
Capture a faithful baseline with explicit net/valve-half mapping. Resolve the small reference/scope ambiguities, select an output-power goal, complete the supply/load budgets and obtain real cabinet geometry. Select traceable components and qualify their simulation models before integrated sweeps and revision approval. Source recovery is complete; native capture, component selection, simulation and hardware validation are not.
