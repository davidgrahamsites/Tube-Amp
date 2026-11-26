# From resistor package correction to a complete rating inventory

**Source checkpoint:** 25 November 2026; VAL-070, VAL-071, VAL-072

**State label:** package edits verified within their stated CAD scope; stress, sourcing, and assembled fit remain open

**Baseline:** individual review baselines differ; current project journal baseline is `d5566cd`.

## The problem

The work began with a specific mismatch: the small native R605 package did not represent the FMP200 resistor envelope being considered for the reverb-tank driver/output series-resistor path. This was not just a symbol or silkscreen issue. Lead spacing, hole size, body clearance, local routing, and credible stress limits all mattered. A related audit then found that thirteen existing FMP200 instances on Main and Power had only a small lead-to-hole allowance relative to the proposed insertion-margin requirement. The old 0.8 mm nominal hole was assigned a 0.7 mm minimum under the proposed tolerance against a 0.6 mm maximum lead, leaving 0.1 mm allowance rather than the proposed 0.2 mm. This was an insufficient declared allowance, not an impossible insertion claim. Separately, the selected-parts coverage process did not account for all source references: R304/R314 were already present in the design but missing from the central register.

These are three different classes of defect: a local footprint integration, a repeated fabrication-hole correction, and an inventory/factory control gap. Treating them as one generic “BOM cleanup” would obscure which evidence closes which risk.

## Requirements and authority

FB-141 records the user's requirement that component watts and physical size be known and appropriately selected. The canonical task card and handoff carry that requirement. It is engineering work to decide which stress applies to each part; “watts” alone is not meaningful for every capacitor, contact, transformer, or semiconductor. Component records and manufacturer documents provide the stated ratings, while native CAD checks establish only the declared file changes.

## Evidence and reasoning

For R605, the review identifies Yageo FMP200FRF52-220R, 220 ohms, with a 9.5 × 4.2 mm maximum body and 0.60 mm maximum round lead. The adopted candidate footprint uses 15.24 mm formed pitch, 0.9 mm finished holes, and 1.8 mm pads. A provisional 3 mm underside standoff yields a 7.2 mm top-side envelope; it is explicitly an allocation, not a fit or thermal test. A source-bound normal signal screen gives about 0.13386 W under an ideal-driver/assumed tank-resistance condition. At the 100°C ambient screen, the candidate's derated allowance is 1.29412 W. The direct 18 V RMS diagnostic is 1.50720 W and fails. That diagnostic is not a claim that the intact coupling capacitor passes DC or that the op amp can sustain that condition; typical current limiting was not credited as guaranteed protection.

The thirteen older FMP200 footprints were corrected to 0.9 mm holes and 1.8 mm pads using a proposed ±0.1 mm finished-hole allocation. The manufacturer lead range is 0.55 ±0.05 mm; at a 0.8 mm minimum finished hole, the remaining diametral insertion allowance is 0.2 mm. The fabricator still must confirm finished-hole and registration capability. The edit preserved placement, connectivity, tracks, vias, outlines, and mounts.

The rating inventory then accounted for all 240 physical references in the current circuit source. It added already-integrated R304/R314 to the coverage/purchasing register and made the BOM factory reject missing references, duplicates, and explicit source/MPN disagreement. Three negative controls demonstrate those failure cases. The bounded manufacturer-based R304/R314 calculation is 2.8125 mW each against 64.706 mW allowed at the assumed 100°C. That closes only the stated resistor-power screen, not ESD, abnormal supply, sequencing, or local thermal behavior.

## Options and tradeoffs

The R605 review compares FMP200 geometry and stress to a Vishay PR03 alternative, but neither the historical supplier listing nor the package comparison establishes a current China supply route. A larger resistor is not a complete driver/tank protection strategy. For the repeated holes, correcting the drill while retaining placement avoided a broad board change, but depends on the fabricator's actual tolerances. For rating coverage, the durable improvement was a factory-level completeness check rather than a one-time manually repaired list; inventory completeness still does not qualify every component electrically.

## Decision and native change

VAL-070 records the R605 package integration as a conditional package correction and explicitly leaves thermal/fault and purchasing qualification open. VAL-071 records the thirteen hole corrections and says they close the insertion-clearance defect only. VAL-072 reconciles R304/R314 into the existing component coverage and tightens the BOM generator. These records do not approve fabrication. No claim here converts candidate listings into orders or fresh stock evidence.

## Verification and limits

For R605, independent checks preserve 240 components and 145 nets, compare 54 other Reverb footprints and all 18 schematic rasters, and verify the declared drill delta. Reverb DRC reports zero violations and zero opens under the unchanged rules; ERC findings are unchanged. For the thirteen FMP200s, parsed-tree comparison and disposable baseline replay pass; exactly 26 holes enlarge, with all other drill hits unchanged. Existing Main findings (43 DRC, 105 unconnected) and Power findings (12 DRC, 39 unconnected) remain. For rating coverage, all 240 source references are accounted for and the three negative controls fail as intended. None of these checks means all ratings, all routing ampacity, or cabinet fit are qualified.

## Remaining tests and next action

Close R605 driver short/thermal limits using an exact sourceable design and measured or otherwise justified operating conditions. Confirm finished-hole tolerances and exact bought suffixes. Continue per-reference operating, transient, fault, and thermal evidence; preserve separate capacitor voltage/ripple and magnetic current/VA constraints. Carry body, standoff, heatsink, and socket envelopes into a populated three-board chassis review. No fabrication release follows from these validations.

## Physical-build placeholder

Record the actual resistor maker/suffix and received lead/body dimensions; measured board holes and forming method; standoff and nearby-component spacing; local temperature under bounded operation; fault waveform/duration only if safely tested; and actual cabinet clearance. Current evidence contains no such assembled measurements.

## Reusable lesson

Separate source identity, package geometry, stress rating, and purchasing proof into linked claims. A good footprint can still represent an under-rated part; a correct rating inventory can still contain unqualified entries; and passing native checks cannot establish real assembly fit. Make each check state exactly which layer it closes.

## Sources

- [VAL-070](../../../brain/records/VAL-070-r605-package.md), [R605 integration review](../../../engineering/whole-amp/pcb-measured-r/r605-package/review.md)
- [VAL-071](../../../brain/records/VAL-071-fmp200-finished-holes.md), [FMP200 finished-hole review](../../../engineering/whole-amp/pcb-measured-r/fmp200-holes/review.md)
- [VAL-072](../../../brain/records/VAL-072-rating-coverage.md), [rating coverage review](../../../engineering/component-selection/rating-coverage/review.md)
- [User rating requirement FB-141](../../../brain/feedback/events.json)
