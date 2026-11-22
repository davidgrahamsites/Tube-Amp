# Electric reverb connector and capacitor qualification — 21 November 2026

Owner: component-selection investigation agent; integration owner controls coverage, circuit, native CAD and release.

Inputs: electric branch, coverage groups P077/P087/P088/P089/P093/P095/P099/P100; reverb-600 circuit; dated 11 November sourcing register. Process: compare exact manufacturer specifications, domestic catalogue identities and existing footprint/interface requirements. Outputs: the proposed changes below. No shared register, schematic or PCB was changed by this investigation. Human check: verify pin 1 and mating direction on actual samples, inspect manufacturer drawings against native footprints, check harness retention, then inspect rerouted board and DRC. Done for this investigation: actionable proposals with unresolved qualifications stated. Fabrication release remains open.

## Result

C605 has an actionable candidate correction. The existing 50 V candidate does not meet its 63 V requirement. Six reverb connectors now have an exact JST header/mate/contact proposal, but the present harness requirement and 2.54 mm footprints prevent promotion to a released selection. C603 remains held for an exact manufacturer dimensional drawing.

## C605: replace the inadequate candidate

Group P093, C605: existing `1206CG331J500NT` is a 50 V candidate against a 63 V minimum. Proposed replacement candidate: **Yageo CC1206JRNPO0BN331**, LCSC **C527285**, 330 pF, ±5%, 100 V, C0G/NP0, 1206. It preserves the intended capacitance and dielectric class.

[Yageo manufacturer specification, version 25, 8 December 2022](https://yageogroup.com/content/Resource%20Library/Datasheet/UPY-NP0X7R_MV_100-TO-630V.pdf) establishes voltage code 0 = 100 V, NP0 temperature coefficient ±30 ppm/°C and operating temperature −55 to +125 °C. [Exact-part distributor entry](https://www.digikey.com/en/products/detail/yageo/CC1206JRNPO0BN331/5884450) confirms 3.20 × 1.60 mm body and 0.70 mm maximum thickness.

[LCSC exact-part global listing](https://www.lcsc.com/product-image/C527285.html?whichImg=pcb), indexed when checked on 21 November, reported 4,000 stock, MOQ/multiple 10, USD 0.0402 each at 10. This is global catalogue evidence, **not a verified mainland RMB quote**. An exact domestic product page was not located. Do not convert this quote into RMB or claim Shanghai delivery is confirmed.

Native consequence: C605 is presently through-hole `C_Rect_L7.2mm_W2.5mm_P5.00mm`; adopting this part requires a genuine 1206 SMD footprint and rerouting. The component is between REC_OUT and REC_FB in the low-voltage recovery block. For 100 kΩ feedback resistance, nominal pole remains 1/(2π×100k×330p) = 4.823 kHz. This calculation is not a new SPICE run. Keep P093 as candidate/qualification incomplete until native implementation and domestic sourcing are closed.

## Six reverb headers and their mates

Primary source: [JST XH manufacturer drawing and specification](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf), reviewed 21 November. XH uses **2.50 mm pitch**, not 2.54 mm. Assembled height is 9.8 mm before wire bends. Rating: 250 V AC/DC and 3 A with AWG22; temperature −25 to +85 °C including self-heating. The standard SXH-001T-P0.6 contact accepts AWG28–22, insulation diameter 0.9–1.9 mm. Avoid the low-insertion-force N contact variant where vibration retention matters. JST calls for consultation for shielded wire. Header body widths are 7.4/9.9/14.9 mm for 2/3/5 positions, depth 5.75 mm; housing widths 7.3/9.8/14.8 mm. Review the drawing for hole tolerances and orientation; do not substitute a generic header by pitch alone.

| Coverage / refs | Header exact MPN | Domestic product | Mate | Header quote retained from 11 Nov |
|---|---|---|---|---|
| P077 JR1; P088 JR2; P089 JR3; P099 JR5 | B2B-XH-A(LF)(SN) | [C158012](https://item.szlcsc.com/169360.html) | XHP-2 | RMB 0.2044, MOQ 20, stock 566k+ |
| P095 JR4 | B3B-XH-A(LF)(SN) | [C144394](https://item.szlcsc.com/155726.html) | XHP-3 | RMB 0.2738, MOQ 10, stock 125k+ |
| P100 JR6 | B5B-XH-A(LF)(SN) | [C157991](https://item.szlcsc.com/169339.html) | XHP-5 | RMB 0.5509, MOQ 5, stock 70k+ |

The three domestic header pages again returned the exact product identities on 21 November. Current prices and MOQ were not exposed in their public page output. Therefore the table deliberately retains the date of the prior quote and does not claim those stock figures are current.

New exact domestic mate/contact routes:

- [XHP-2, C144401](https://item.szlcsc.com/155733.html): quantity four for the four two-pin board connectors.
- [XHP-3, C144402](https://item.szlcsc.com/155734.html): quantity one.
- [XHP-5, C144404](https://item.szlcsc.com/155736.html): quantity one.
- [SXH-001T-P0.6, C140573](https://item.szlcsc.com/151899.html): quantity sixteen contacts for these six cable ends, before spares. Other ends are extra.

These domestic pages confirm exact identities; no current RMB quantity-tier quote was exposed for the mates/contacts. Their low-MOQ procurement is not yet closed. Global LCSC XHP-3 listing reports MOQ 20, but this is not a substitute for a domestic quote.

### Interface stays unchanged

| Header | Pin order in current circuit |
|---|---|
| JR1 | 1 FX_RETURN; 2 GND |
| JR2 | 1 TANK_IN; 2 GND |
| JR3 | 1 TANK_OUT; 2 GND |
| JR4 | 1 WET_TOP; 2 WET_W; 3 GND |
| JR5 | 1 MIX_OUT; 2 GND |
| JR6 | 1 +15V; 2 GND; 3 −15V; 4 +12V; 5 COIL_REV |

### Release conditions

The coverage requirement is “soldered locking harness or retained socket.” XH is friction retained, without a positive latch; its domestic listings explicitly say no locking buckle. **Do not mark these harness groups selected solely because the header is electrically adequate.** Either engineer an independent cable clamp/retainer and validate retention, or choose a positively latched family and requalify its dimensions.

Also required: replace all six generic 2.54 mm board footprints with verified XH 2.50 mm geometry; budget plug extraction and wire bend space above the 9.8 mm mating height; specify actual wire and crimp tooling; keep the connector ambient below 85 °C including self-heating; check pin numbering from mating and solder views; resolve shield termination without forcing a braid into an unsuitable contact; label the four interchangeable two-pin plugs so tank drive cannot be swapped with recovery or return. Connector supports attach to the chassis, not the removable wooden back. No harness shall bridge a service cover that must be removed independently. These are low-voltage reverb connectors only; do not extend their selection to mains, B+ or heater power.

## C603: source retained, package qualification still open

P087 C603 candidate **KNSCHA 224CL0045**, C47917108, remains 2.2 µF ±5%, 63 V metallized polyester, pitch 5 mm, −55 to +105 °C according to [exact LCSC catalogue entry](https://www.lcsc.com/es/product-detail/C47917108.html?is_substitute=1&original_product_code=C89819&original_unit_price=3.0598). The linked datasheet endpoint returned an HTML viewer, not a readable exact manufacturer drawing during this check. Therefore its body size, lead diameter and thermal voltage derating were not qualified.

Existing 11 November domestic source: [C47917108](https://item.szlcsc.com/50153065.html), RMB 1.935, MOQ 1, stock 4,062. A [domestic related-part catalogue](https://item.szlcsc.com/6172087.html) indexed two weeks before this check showed 224CL0045 among alternatives with stock 4,160 and RMB 2.47; quantity tier was unspecified. Treat it only as continued domestic catalogue presence, not a new low-quantity quotation. C603 current 7.2 × 7.2 mm / pitch-5 footprint must not be frozen until exact maximum dimensions are obtained. Do not automatically replace polarized C212 with this nonpolar part; that is a separate design change.

## Proposed register actions for integration

1. P093: retain incomplete status; replace/add candidate with CC1206JRNPO0BN331; identify former 50 V candidate as not meeting 63 V minimum. Attach this evidence path. Do not populate selected_mpn yet.
2. P077/P088/P089/P095/P099/P100: preserve current candidate headers; add the exact mate and contact dependencies and the retention/footprint holds above. No selected_mpn promotion yet.
3. P087: preserve candidate and explicit maximum-body/lead/derating hold.

No procurement, live circuit test, native footprint replacement, PCB reroute, simulation or DRC was performed in this evidence-only part-selection subtask. Root integration owns those checks and catalog/ICM synchronization.
