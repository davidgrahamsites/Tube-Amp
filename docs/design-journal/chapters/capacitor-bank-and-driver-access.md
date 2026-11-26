# Capacitor-bank fit review and chassis tool access

**Source checkpoint:** 26 November 2026; FB-143, FB-144, and FB-145

**State label:** standalone and combined five-pass reviews complete; conditional comparison only; no native edits, part adoption, or fit approval

**Baseline:** intended three-board architecture retained; current native CAD has four incomplete boards; actual drill envelope incomplete

## The problem

During populated chassis planning, the user asked whether the high-voltage film capacitors could be raised over other components or placed on a small breakout board, and asked about a flexible tool for tight-corner access. These questions prompted two related but separate checks: capacitor lead/body packaging and mechanical access to chassis screws. Neither proposal authorizes a new layout or a relaxation of ordinary service access.

## Requirements and authority

FB-144 asks to evaluate elevated bodies, a supported capacitor board, and other packaging approaches while preserving the power-supply functional block. FB-145 asks for a Five Times Skill Plus fit improvement review. The intended three-board architecture remains the design preference, but current native CAD contains four incomplete boards; this review does not imply that the three-board version has been laid out. FB-143 defers the remaining drill measurements until tomorrow; only the 46 mm chuck diameter is presently known. These are proposals and open measurements, not adopted hardware or fit approval.

## Evidence and reasoning

The Panasonic EZPV R9 datasheet gives the candidate EZPV60506MTC an exposed lead length of 4 ± 2 mm. With the 1.6 mm nominal PCB and the capacitor seated, the minimum 2 mm exposed lead leaves only 0.4 mm below the board. Raising the body 3 mm leaves the shortest lead 2.6 mm short of the PCB underside, before accounting for solder protrusion or board thickness tolerance. CRC FC6136 has a 4 ± 1 mm lead; its minimum 3 mm lead leaves only 1.4 mm beneath a seated 1.6 mm board and is also 1.6 mm short if raised 3 mm. The calculations do not support simply bending or extending these leads to suspend the bodies above other parts.

The fit research preserves electrical identity and returns for all four 50 µF references: C12 connects B_EARLY to GND; C13 and C25 are distinct references on the shared B_PRE/GND node; C26 connects B_SCREEN to GND. C13 and C25 are electrically parallel in the present circuit, but their physical positions and deliberate returns must not be collapsed or reassigned as a packaging shortcut. C29/C30 remain the separate raw reservoir.

The assembly-options receipt estimates a conditional four-body 2 × 2 extent of 126 × 62 × 41 mm for Panasonic EZPV bodies with its manufacturer-recommended 10 mm neighbor gap, or 127 × 82 × 51 mm for CRC under a comparison-only 10 mm gap. Panasonic horizontal compact row is 134 × 58 × 42.6 mm including nominal PCB thickness; vertical 2 × 2 is 126 × 42.6 × 62 mm. The Panasonic vertical arrangement trades 19.4 mm of local depth for height but does not prove the complete cassette clears its depth deficit. Whole-tier diagnostic arithmetic gives Main + Reverb at 508 × 160 mm against a provisional 467 × 160 mm frame (41 mm width overrun), rotated Power + Control at 463 × 180 mm (20 mm depth overrun), and Main + rotated Reverb at 448 × 180 mm (also 20 mm depth overrun). These frame and allowance values are diagnostic, not verified usable cabinet dimensions. The envelopes also omit board margins, supports, solder, clearance, connectors, underlying components, removal/tool paths, cabinet/speaker/transformer fit, and thermal qualification. They are not cabinet-fit results.

The mechanical review distinguishes flexible/right-angle screwdriver accessories from drilling equipment. A documented DeWalt flexible right-angle accessory has a 120 in-lb (about 13.6 N·m) maximum torque, which is the accessory ceiling, not an amplifier-fastener tightening recommendation. Tool-specific adapters such as the Bosch IXO example do not establish compatibility with the user's drill chuck. A flexible accessory could be a service aid only after its head size, bend radius, length, torque/speed/direction limits, retention, and stabilization space are checked against the complete approach and withdrawal path.

## Options and tradeoffs

The five-pass plan prioritizes a dedicated capacitor area on the revised power PCB, comparing a compact 2 × 2 group with a short-axis row. It preserves the intended three-board architecture if the rest of the board repack permits it; it does not describe the current four incomplete native boards as a completed three-board layout. This is the preferred starting point because it avoids extra high-voltage interconnects, while still requiring actual body/pin limits, support, thermal space, and service access. A supported vertical or upper bank is conditional on a whole-cassette model showing a real benefit after supports, wiring, service paths, and existing width/depth overruns are included.

A capacitor board mechanically supported by chassis brackets or standoffs remains a conditional alternative if the populated assembly demonstrates a real benefit. It would add a physical PCB while retaining the same power-supply functional block. It requires a rated and insulated connection system, explicit supply and return paths, high-voltage spacing, supported mass, removal sequence, heat review, and access. A suitable chassis-mounted capacitor bank with insulated harness is another unselected option requiring exact components and revised wiring/return checks.

Discharge behavior is a separate service gate. The raw reservoir discharges through R501/R502, but that path is upstream of standby switch S2 and is disconnected from the downstream filters when standby is open. Downstream discharge paths do remain in the source through B_SCREEN → R506 → HREF → R507 → GND, with C505 and filter coupling affecting the behavior. Tube loads and switch state also change decay, so a single RC time is not a valid system claim. A disconnected capacitor-only bank may lose its discharge paths. Charged, powered-off, standby-open, partially disconnected, and removed states need explicit path accounting, residual-voltage/service-time criteria, worst-case decay calculations, accessible test points, and hardware verification. No extra bleeder is proposed here; it would be a separate circuit change.

Elevating capacitors on their leads alone is not supported: short leads, lead-root and solder-joint loading, exposed high voltage, obstructed components, and blocked screws remain concerns. A flexible screwdriver extension does not make an otherwise blocked or trapped chassis acceptable and does not qualify drilling access. Straight access and ordinary bench servicing remain the mechanical preference.

## Decision and native change

No capacitor package, daughterboard, chassis-mounted capacitor, mounting scheme, or layout has been adopted. The capacitor-bank board remains conditional and would be an additional physical PCB, not a new power functional block. No native files were changed and no populated fit is approved. The intended three-board architecture remains the preference; current native CAD still contains four incomplete boards. The standalone five-pass fit plan and combined FB-147 synthesis are complete. The synthesis retains the capacitor-area comparison as conditional; neither plan adopts a part, layout, or fit. No flexible or right-angle accessory is selected, and no tool-access waiver is made.

## Verification and limits

The cited package comparison is conditional arithmetic, and its result explicitly says assembly is not approved. It does not establish exact purchased part identity, supported mounting, high-voltage clearance, cooling, harness performance, cabinet fit, or service access. For tool access, only the 46 mm chuck measurement is known; the accessory examples and their published limits do not prove fit with the user's tool or the chassis.

## Remaining tests and next action

When available, capture the exact drill/driver body, chuck, bit, and accessory dimensions and check the screw approach, withdrawal, and hand stabilization path with the actual chassis configuration. Separately compare the repacked power-PCB area against a mechanically supported capacitor bank in the common populated assembly using actual capacitor, speaker, magnetics, socket, and support envelopes. Confirm high-voltage wiring/returns, insulation, thermal behavior, mass support, and service sequence before any board or chassis change.

## Physical-build placeholder

Record actual capacitor markings and body/lead dimensions, formed-lead geometry, support method, board thickness, solder protrusion, nearby-part clearance, temperatures, and removal access. Record the actual driver/accessory identity and full tool envelope, then photograph or measure the complete screw path with the chosen installed-cover state. None of these physical checks is complete in the cited reviews.

## Reusable lesson

A packaging sketch must honor component lead geometry and a real structural load path. A second supported PCB can preserve functional ownership while changing the physical board count; that distinction must stay explicit. Likewise, a flexible screwdriving accessory is a possible aid, not a substitute for measured clearance or normal service access.

## Sources

- [Completed capacitor-bank fit plan](../../../plans/capacitor-bank-fit/final.md)
- [Combined synthesis contract](../../../plans/power-packaging-synthesis/CONTEXT.md)
- [FB-145 fit plan and module contract](../../../plans/capacitor-bank-fit/CONTEXT.md)
- [Fit improvement plan, version 4](../../../plans/capacitor-bank-fit/v4.md)
- [Mounting research](../../../plans/capacitor-bank-fit/mounting-research.md)
- [Electrical interface and discharge research](../../../plans/capacitor-bank-fit/interface-research.md)
- [Geometry research](../../../plans/capacitor-bank-fit/geometry-research.md)
- [FB-144 proposal and packaging review](../../../engineering/component-selection/power-film/assembly-review.md)
- [Conditional assembly arithmetic](../../../engineering/component-selection/power-film/results/assembly-options.json)
- [FB-143 tool-access review](../../../engineering/whole-amp/mechanical/review/driver-access-options.md)
- [Feedback entries FB-143, FB-144, and FB-145](../../../brain/feedback/events.json)
