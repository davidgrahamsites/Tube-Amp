# Electric amplifier packaging and pot panel assessment

Date: 2026-11-21. Branch: electric-guitar-amp. Status: dimensional assessment and proposed layout; **not a drill drawing or verified whole-amp fit**.

## Task card and ownership

Owner: mechanical assessment worker; integration agent owns the canonical fit register, PCB outlines and requirements. Inputs: [mechanical register](../fit-register.json), [current PCB contract](../../pcb-measured-r/CONTEXT.md), [current circuit](../../reverb-600/circuit.json), original three cabinet views linked in the register, [pointer-knob record](../../../../brain/records/CMP-013-pointer-knobs.md) and the user's instruction to include the panel holding the pots. Output: this review only. Scope: P0/P1 dimensional screen, control inventory and assembly interfaces. Operations: read records, count controls, calculate envelopes and identify closure checks. Effort: one bounded assessment. Done condition: distinguish usable design directions from unverified clearances and give the integrator a concrete next sequence. Human evidence: actual opening/support outline, received tank dimensions and an eventual populated assembly trial fit. No shared geometry, CAD or parts register was changed by this worker.

## Evidence limits

The received cabinet is fixed. Its yellow finish and identity do not determine its internal geometry. Retain these facts separately:

| Evidence | Value | Use in this review |
|---|---:|---|
| User-reported clear width, front and rear | 467 mm | Screening width; height/datum remains recorded as uncertain. |
| User-reported baffle rear face to cabinet rear edge | 160 mm | Screening depth at the instructed height; the nearest obstruction and complete three-dimensional interior remain unknown. |
| Supplier top opening | 312 mm straight, 344 mm stepped, 67 mm deep, R31 corners | Proposed top-control access screen only. These are not a rectangular clear opening, panel outer size or chassis internal size. |
| User-reported speaker diagonals | 294 mm, 294 mm | Retain without replacing them with the supplier's 312 mm circle. |
| User-reported three adjacent speaker-hole distances | 210 mm | Ideal square would imply 296.985 mm diagonal. Existing 3 mm disagreement remains unresolved. Use a template/trial fit rather than forcing one set of numbers. |
| Received tank | M8EB2C1B / R2610270015 | Actual body, flange, plug and mounting dimensions remain unmeasured. Other Type8 or Mable drawings are not this unit's dimensional evidence. |

Register SHA256 when read: `7fd6a458f3da4be37ca0edb10c90270bbd7d9f6a80d8c51ecf071ca4ac56a17a`. This is a snapshot reference; the editable register remains authoritative. No new catalogue or stock claim is made here.

## Board and chassis screen

Current outline inputs are Main290×140, Power160×175, Control230×110 and Reverb160×100 mm. Their combined bare area is109,900 mm². The reported467×160 mm rectangle has74,720 mm² area. The boards occupy1.471 times that rectangle before spacing, mounting, walls, wires or large parts. Therefore these four unchanged outlines cannot all occupy that single flat rectangle. The rectangle itself is only a screening assumption, not a confirmed chassis volume.

Main and Reverb side by side with an8 mm gap occupy458×140 mm. That leaves just9 mm total width against the reported467 mm width, before any wall/support allowance. This is not a sensible frozen mounting design. Power160×175 mm cannot fit flat in160 mm depth: rotated, it uses the entire depth with zero remaining allowance. Control230×110 and Reverb160×100 are candidates for repacking; their present outlines are not requirements.

**Integration direction:** separate the accessible control panel from the main circuit-board dimensions. Use chassis-mounted pots with short, strain-relieved harnesses; let the actual six sockets/tubes, speaker and magnetic components establish the chassis envelope before routing the remaining board area. Repacking or changing board mounting planes is necessary. Do not declare the current four-board design finished by merely eliminating airwires.

A conservative *design-search allocation* for a horizontal internal tray is440 mm wide by130 mm deep. Against the screening rectangle it leaves27 mm width and30 mm depth total. These are space reservations, not electrical safety clearances or proof that a tray fits. It would require substantial repacking or separate mounting planes; it cannot receive all four current boards. Do not copy this proposed envelope into the canonical register as a measured cabinet value. The chassis height and vertical position remain open because the speaker frame/magnet, tubes and transformers are not yet assembled in a common model.

For a tangible **second search case**, test a440×145×85 mm electronics cage in the assembly model. The extra depth compared with the first case accommodates vertical auxiliary boards. These targets are deliberately unverified and must not overwrite current board outlines:

| Proposed board target | Size, mm | Example cage-local allocation | Major test before accepting |
|---|---:|---|---|
| Main | 270×92 | Floor x8…278, y8…100 | Current290×140 layout must shrink substantially without compromising HV spacing, wiring or resistor heat. |
| Power | 140×92 | Floor x288…428, y8…100 | Current160×175 layout must shrink by over half its area. Selected large capacitors and their clearances may rule this out; it is not a validated packing solution. |
| Control | 210×70 | Rear vertical plane, x8…218, z8…78 | Allow up to20 mm populated projection in front of the plane and separate solder-side/mounting space. Heatsink/connectors may exceed that budget. |
| Reverb | 200×70 | Same rear plane, x228…428, z8…78 | Repack current160×100 geometry; preserve input/output separation and cable routing. |

For this case only, set the rear board plane to y132 mm, with parts occupying y112…132 and a nominal6 mm rear mounting/solder-side allocation to y138. The floor-board outline stops at y100, leaving a nominal12 mm plan separation. This is a volume-search gap, not an approved electrical clearance. Floor standoffs can initially be studied at8 mm, then component height is added explicitly; the historical41 mm power-film-cap height already reaches approximately50.6 mm above the floor including1.6 mm PCB. Slots, tolerance and fastener tools need their own volumes.

Coordinate origin for this **proposal only**: cage front-left-bottom, x right, y toward cabinet rear, z up. There is no established transform from this cage to the cabinet, opening or baffle. The85 mm cage height is a required empty height for this search case, not a reported cabinet measurement. Tubes, sockets, transformers and tank have **not** been allocated to this cage. A transformer or pot may occupy the space proposed for a board and invalidate it. In particular, a top control panel over the rear of the cage may place its pot bodies directly into the vertical auxiliary-board volume: overlay those bodies before considering this arrangement viable. Shift/shrink/reorient boards if needed; do not silently subtract the pots or tube service paths.

Do not reuse the historical468×190 mm two-plane tray as a validated design. The newer160 mm depth report makes that historical depth assumption unsuitable for the upper measured location.

## Ten user controls, two service adjustments

The current circuit requires these ten face controls:

| Group | Reference | Function | Current electrical value |
|---|---|---|---|
| Clean | RV1 | Treble | 250 kΩ linear |
| Clean | RV2 | Bass | 1 MΩ log |
| Clean | RV3 | Volume | 1 MΩ log |
| Dirty | RV4 | Gain | 1 MΩ log |
| Dirty | RV5 | Treble | 250 kΩ linear |
| Dirty | RV6 | Bass | 1 MΩ log |
| Dirty | RV7 | Mid | 25 kΩ linear |
| Dirty | RV8 | Master | 1 MΩ log |
| Shared | RV9 | Presence | 25 kΩ linear |
| Shared | RV602 | Reverb, adds wet | 100 kΩ log |

RV601 is the100 kΩ tank-send commissioning trim. RV10 is the50 kΩ bias adjustment. Neither receives a user faceplate knob. Verify the eventual bias control is protected against accidental operation. These classifications are panel requirements, not changes to current circuit topology or approval of a particular pot part.

## Proposed top-panel layout

The accepted pointer-knob direction has a historical nominal26 mm envelope. The exact part, bore and rotational swept envelope remain to be confirmed. With26 mm swept diameter and32 mm centres, one row of ten needs9×32+26=314 mm before end margins. That exceeds the312 mm straight opening dimension. A tight single row is rejected as the starting panel plan.

Use **two rows of five** as the first paper-layout option. Example spacing:42 mm horizontally and34 mm between rows. Ten assumed26 mm swept envelopes then occupy194×60 mm. This leaves room across the central portion for logical grouping, but only7 mm total depth margin against the *published*67 mm opening depth. Label space, fingertips, the radiused boundary and panel position must therefore be checked on the actual opening. A26 mm longest dimension is not automatically a26 mm swept circle if the shaft is off-centre: use the real shaft-centred rotation envelope.

The adjustable1:1 paper study should use a **generic shaft-centred swept diameter D**, not a catalogue length. For a deliberately conservative central-width screen, reserve31 mm at each end of a312 mm nominal opening, leaving250 mm; this reserve avoids relying on the corner shape but does not reconstruct that shape. In a local312×67 mm paper frame, start the five column centres at x72,114,156,198,240 mm. For the26 mm example with34 mm row spacing, use y16.5 and50.5 mm. Draw full swept circles and separate pot-body/washer circles; leave hole diameters unset. Mark this frame's origin and cabinet location **unconfirmed**.

For knobs that must rotate fully inside a recessed opening, a useful screen is `2D + row_edge_gap + 2 × boundary_margin ≤ 67`. With5 mm gap and5 mm outer margins, D must be≤26 mm; D32 would require79 mm and D40 would require95 mm. Those5 mm values are provisional handling/geometry allowances, not a validated ergonomic standard. Increase them if real fingers, printing or the wooden lip need more room. The pointer-knob's actual off-centre sweep could therefore rule out the recessed two-row option even though its listed length is26 mm.

There is also a **raised/flush cover-plate option** to examine before considering cabinet alteration: if the knobs are above the wood's top surface, their sweep may overhang the opening while the pot bodies remain inside it. In that architecture the opening constrains the bodies, nuts and lugs, not necessarily the full knob sweep. Model the plate elevation and wood lip explicitly. For example, two nominal16 mm bodies on48 mm row centres occupy64 mm before tolerance/lugs; against67 mm that leaves only3 mm total, so it is a tight screen, not a fit result. A wider/deeper plate alone cannot solve a body collision, and raising it creates new mounting, appearance and handle-clearance requirements. This alternative means the earlier single-row/recessed-envelope rejection must not be read as proof that every raised-panel arrangement is impossible.

Suggested grouping: one row for CLEAN TREBLE / BASS / VOLUME plus REVERB / PRESENCE; one row for DIRTY GAIN / TREBLE / MID / BASS / MASTER. Reverse the order of rows if the actual viewing angle or wiring makes that more usable. Preserve the electrical functions; these labels/positions are a proposal, not released coordinates.

Keep input jack, channel indication and power control access in the remaining reviewed panel area or a separate appropriate panel region. A10-control envelope alone does not prove those additional components fit. Reserve plugs, switch travel and indicator visibility rather than placing their centres in unused graphics space. Mains switching hardware and its wiring require their own electrical clearance review, away from the guitar input and high-impedance pot wiring.

The mounting plate can be part of a folded metal chassis or a removable metal plate fastened to a chassis frame. A1.5 mm steel or2 mm aluminium plate is a reasonable **prototype study input**, not a finalized structural/material specification. Fastening spans, folds, stiffness, finish, corrosion, electrical bonding and available bushing length must be checked before selecting thickness. Do not mount pots only through a printed label, and do not rely on PCB solder joints to resist knob torque.

## Pot, knob and panel interface to freeze

The parts owner must deliver one exact drawing per selected pot/knob suffix. The mechanical register should then own:

- Shaft diameter, shape, usable length above the finished panel and the datum used by the manufacturer's shaft-length callout. Match6 mm to6 mm, or6.35 mm to6.35 mm; do not treat those as interchangeable. A set-screw pointer knob should have a compatible solid or explicitly approved shaft.
- Threaded bushing diameter/pitch, length, manufacturer panel-hole recommendation and anti-rotation tab geometry. Hole size cannot be fixed from the pot's body diameter. Do not automatically use a9.5 mm guitar-pot hole for a metric7 mm bushing.
- Finished metal thickness, label/coating thickness, washers, nuts, thread engagement and available tightening access. Check the sum of the stack against the bushing's usable threaded length.
- Shaft-centred knob swept radius, height, set-screw access, clearance above the panel and visual index at minimum/maximum. Print scales after actual shaft travel and knob orientation are known.
- Pot body diameter/depth, solder-lug or pin projection, insulation and wire bend envelope. Space for26 mm knobs does not necessarily provide space for large24 mm pots plus terminals.
- Terminal numbering and clockwise sense, including wiper connection, so a panel drawing cannot silently reverse controls. Harnesses must be removable for chassis service without stressing pot terminals.
- Panel outer outline, mounting holes and origin/viewing side. Panel attachment must clear the wood opening, supports, handle bolts, washers and screwdriver/wrench paths.

Use positive chassis bonding as specified by the electrical owner. A loose pot nut or painted interface must not be the sole protective-earth connection. Do not conflate signal-ground routing with mechanical pot-case/panel bonding.

## Whole-amplifier interference and service checks

The model must include the speaker's full basket/magnet, not just its diameter; all six tubes, sockets, retainers/shields and extraction paths; PT/OT/choke/aux supply hardware; actual capacitor heights and vents; populated board and solder-side volumes; panel pot/jack/switch bodies; and the received tank with its mounting, RCA plugs and cable bends.

The Celestion Seventy80 remains a reference, not a selected or fitted speaker. The existing register records309 mm outer diameter,297 mm mounting circle,119 mm overall depth and134 mm magnet diameter. On the160 mm depth screen, subtracting119 leaves41 mm at most at the same datum; this is not a guarantee of magnet clearance or permission to fill that space with a board. The required cutout is not established in that record. Speaker mounting-pattern uncertainty, aperture, baffle thickness, terminal projection and nearby chassis remain open.

Mount the actual tank horizontal/open-side-down as specified by the seller. Include clearance for its sprung mechanism and compliant mounting, not a bare rectangle pressed against the floor. Keep its sensitive output end away from magnetic hum sources; final hum must be checked with the installed transformers operating. No assumed distance alone certifies this.

Prefer a removable service assembly. Show the order for extracting the chassis, disconnecting panel/speaker/tank harnesses and removing each tube without removing the speaker or damaging the tweed. Support transformers through appropriate metal structure; board mounting screws are not an assumed transformer load path. Thermal spacing and ventilation remain engineering outputs, not arbitrary visual gaps.

## Minimum additional physical evidence

Do not ask the user to repeat all A/B/C measurements. The following closes different gaps:

1. **Actual top opening and supports:** lay paper over the opening, trace its perimeter and mark existing mounting holes/support edges without drilling. Add a100 mm ruler reference on the same sheet. Also measure the metal-panel seating surface to the nearest obstruction directly below it. This determines which part of the proposed two-row layout is reachable and where pot bodies can sit. A tracing proves an outline only, not bushing or body clearances.
2. **Speaker aperture:** measure the clear wooden circular opening straight through its centre in two directions. This is the hole that the cone/basket enters, not the speaker mounting-bolt circle already measured. Use the selected manufacturer's full-size mounting template/trial fit later to resolve the294/297 mm mounting uncertainty.
3. **Received tank:** measure maximum length, width and height, including flanges/grommets, then RCA socket projection and mounting-hole centres. Leave the actual RCA plug/cable bend envelope to the selected lead drawing or a physical cable. Photographs currently have no scale.

After exact speaker, magnetics and sockets are selected, a single cardboard/full-size printed envelope trial fit can check the planned assembly against the already-reported upper depth and reveal intervening braces. That final trial requires component models; asking the user now for an undefined volume or another diagonal would not solve it.

## Next integration sequence

1. Record the pot-panel requirement in the canonical handoff/event ledger; this worker's evidence must be linked rather than treated as a second requirements store.
2. Merge exact pot/knob drawings from the parts owner. Freeze the shaft/bushing/stack and a maximum rotating knob envelope.
3. Place ten control circles and actual pot bodies on a1:1 top-opening template; include input/power/indication and harness access. Save the layout as a proposal until the physical trace checks it.
4. Select or dimension the speaker, six sockets and largest magnetic components. Establish chassis height/position and complete keepout volumes. Repack board outlines from those volumes; do not route against the discarded flat-area assumption.
5. Generate matching native assembly, PCB outlines and a dimensioned panel drawing from the one fit/interface register. Use separate cut/drill and print layers. Inspect the1:1 print with real knobs and fasteners before machining.

This assessment finds a credible two-row control direction and demonstrates why the current board plan needs repacking. It does not certify that the complete amplifier fits or that the cabinet needs modification. No purchase, supplier message, cabinet alteration, PCB mutation or fabrication release occurred.
