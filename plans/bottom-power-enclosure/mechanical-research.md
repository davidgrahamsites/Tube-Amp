# Bottom power enclosure — mechanical and procurement research

2026-11-26. Owner: delegated mechanical researcher; integration owns adoption and common registers. Status: bounded research supporting [v2](v2.md), no geometry adoption, fabrication release, supplier contact or purchase. Applied Physical Design Agent Ladder P0/P1/P3 and Circuit Design Skill Ladder L0/L1. Only this file is authored by this worker.

## Finding and scope

A lower metal power module is a credible packaging candidate, but **neither lower allocation B nor C has demonstrated cabinet fit, safe thermal operation, low hum, structural retention or service access**. Moving power below can reduce upper carried mass and separate power hardware from input circuitry, while taking the floor volume already intended for the tank and adding cable/connector/service requirements. No saved measurement establishes spare floor space. Unknowns prevent ranking, rather than constituting a pass.

Inputs are [mechanical register](../../engineering/whole-amp/mechanical/fit-register.json), [received tank record](../../engineering/whole-amp/mechanical/review/tank-specifications.md), [upper chassis concept](../../engineering/whole-amp/mechanical/review/three-board-chassis-concept.md), [OT screen](../../engineering/component-selection/evidence/output-transformer-screen-2026-11-24.md), [Mable catalogue screen](../../engineering/component-selection/evidence/mable-catalogue-review-2026-11-12.md), [prototype allowance](../../engineering/component-selection/evidence/prototype-cost-allowance-2026-11-24.md), and [previous capacitor geometry study](../capacitor-bank-fit/geometry-research.md). Those records remain authoritative. Evidence retrieval is bounded; failed page retrieval is not a stock/unavailability claim.

## Occupied and unknown volumes

| Item | Supported fact | Consequence for lower-module trial |
|---|---|---|
| Cabinet | Fixed delivered Mable yellow-tweed shell. User-reported widths 467 mm, depth reading 160 mm, inside height 383 mm; differing/unverified datums | Do not construct a guaranteed 467 × 160 × 383 mm free box. Floor width/depth, corner joints, cleats, foot fasteners and floor thickness/material/condition remain unknown. |
| Upper opening | 307–308 mm width, approximately 53 mm clear depth with upper rear cover on | These constrain panel access; they do not define floor space or rear withdrawal clearance. |
| Current Power PCB | 160 × 175 × 1.6 mm bare outline | Even its rotated shallow dimension is 160 mm before walls, board margins, fasteners, cables or insulation. Whole-board transfer is the first screen, but cannot be declared to fit the reported 160 mm depth. Floor datum may differ; a repack is a separate change, not assumed saving. |
| Received tank | 149.5 × 60 × 36.5 mm reported maximum envelope; T1 includes flanges, T2 fixed sockets, T3 feet; horizontal/open-side-down required | Installed RCA plugs, bends, compliant mounts/bag, fastener access and spring clearance remain additional unknown volumes. Do not substitute catalogue 178/180/235 mm tanks. |
| Speaker | No selected exact speaker. Reference Seventy 80: 309 mm frame, 119 mm depth, 134 mm magnet; requires 283 mm cutout against received approximately 270 mm aperture | Reference is not adopted. Basket shape, magnet, terminals, moving-system clearance and installed coordinates must enter common geometry. The apparent 160−119=41 mm residual is not verified space behind the speaker. |
| Film bank | Panasonic candidate maximum body 58 × 26 × 41 mm; CRC candidate 58.5 × 36 × 51 mm | C has four bodies below; B has C26 below and C12/C13/C25 above. Include actual support/PCB/connector/insulation envelopes. Existing scalar 41 mm capacitor height does not cover CRC. |
| Magnetics | No exact approved PT/OT/choke/auxiliary set or complete drawings | Core labels and catalogue body dimensions cannot supply full feet, bells, lead exits, tolerances, mass or mounting interfaces. |

The previous geometry study gives a Panasonic four-body 2 × 2 conditional array of 126 × 62 × 41 mm with the recorded 10 mm neighbor recommendation. This is a body-array bound, not a lower enclosure size; it excludes reservoirs, rectifiers, magnetics, other power parts and construction. The same study's 41 mm upper carrier width and 20 mm tier-depth overruns remain separate from lower power relocation. Lower placement does not automatically repair Main/Reverb geometry.

## Structure, placement and removal

**Load path proposal:** transformer feet/clamps → structural metal base or crossmember → removable lower-module mounting flanges → fixed floor/side structure → cabinet joints and feet. PCB standoffs and removable rear wood carry no transformer load. Floor mounting means attachment to fixed cabinet structure during use; it need not mean a permanently trapped power module. Retain a bolted removable metal module with reachable retention points and a supported extraction sequence.

Do not prescribe sheet thickness, screw type or number from photographs. Required structural inputs are exact masses and centers of gravity; mounting-hole pattern and clamp stack; metal material/thickness/folds; support span; floor wood material/thickness and joints; edge distance, engagement and backing arrangements; cabinet foot positions; and the chosen carry/handling load case. Assess base bending, fastener shear/pullout, local wood crushing and loosening under speaker vibration. A possible backed/through-bolted load spreader must itself fit, avoid exposed underside hazards and preserve finish/feet; it is a proposal pending cabinet evidence. Low center of gravity is a plausible benefit, not proof of retention under handling.

Keep the **upper audio/tube module removable on fixed side supports**, with the rear wooden cover independently removable. Lower retention, lid screws and connector latches must remain accessible after that cover is removed, without reaching behind a speaker magnet or removing unrelated assemblies. Prefer bench access to PCB screws after module withdrawal. If the lower box has a removable lid, verify its screw and lift/slide path independently of upper-module extraction; a box that only opens after removing its live-connected harness is not a completed service design.

Reserve two separate sweeps: upper withdrawal with tubes/retainers/guards and plugged or deliberately disconnected cables; lower withdrawal with magnetics, inlet/fuse/selector protrusions, lid and harness. Neither sweep may rely on the rear wood as support. Tank relocation, if needed, is a distinct consequence: preserve horizontal/open-side-down orientation, support/compliance, cable access and a new hum test. Do not hang it vertically or use the power box lid as its mounting surface merely to reclaim floor area.

Output-transformer placement remains a separate comparison. Keeping it near output tubes and feedback/speaker routes may be preferable; putting every transformer below would add output-stage wiring and alter coupling/stability conditions. The OT mass quoted below is not part of a settled lower load budget.

## Ventilation and transformer mounting evidence

The lower enclosure needs an actual heat budget for transformer copper/core loss, rectifiers, resistors and capacitors under both mains cases. Locate the candidate air inlet/outlet and trace obstruction by the tank, bag, wood, speaker and upper assembly. Natural convection may send warmed air toward the upper electronics; the metal box does not establish cooling. Record component case/hot-spot and accessible-surface limits from the exact parts and applicable electrical review, then measure with covers fitted at the agreed operating/load and ambient conditions. A fan is not assumed. Vents must also meet touch, wire protection and mechanical requirements; no numerical vent area or clearance is established here.

Manufacturer construction precedent is narrow: [Hammond 516](https://www.hammfg.com/electronics/small-case/general-purpose/516), directly read November 26, uses a substantial raised mounting panel and louvered sides. It illustrates independent structural support and ventilation, **not** a selected enclosure, sufficient thickness calculation or a transferable thermal clearance. Its listed size is not adopted.

**Conditional toroid precaution:** only if a toroidal PT/auxiliary transformer is actually selected, ensure mounting hardware cannot form a closed conductive path through its center and around the outside, including accidental contact between a center bolt/top clamp and the metal lid. This can act as a shorted transformer turn. The primary manufacturer source is [Toroid Corporation, power-supply transformer mounting caution](https://toroid.com/power-supply-transformers-toroidal/), retrieved in the November 26 search extract; direct open subsequently failed. Its [mounting-options page](https://toroid.com/mounting-hardware-options/) was directly read and distinguishes horizontal/vertical hardware. Follow the exact selected maker's clamp/pad and torque instructions. No toroidal part is currently adopted, and this warning is not presented as the mounting mechanism for the EI candidates. [MCI manufacturer's toroid mounting sheet](https://mcitransformer.com/pdf/MCI-Manual-Toroids-Page.pdf) was also retrieved; indexed text supports the same conditional shorted-turn caution. No generic torque value is inferred.

For EI candidates, obtain the manufacturer's complete feet/bracket drawing, permitted mounting direction, fastener/clamp stack and insulation/earth instructions. Existing seller data does not establish these. Ordinary metal enclosure shielding is not evidence that 50/60 Hz magnetic pickup into the tank or input stages is controlled. Layout must be tested with actual loaded magnetics; match tank orientation/load/recovery gain and wiring, vary placement/orientation one factor at a time, then test the combined assembly.

## Harness and tool service interface

Mechanical integration must supply bounded route lengths and minimum/maximum service positions to the electrical owner, rather than assume a generic vertical cable length. Include fixed anchor locations, edge protection, connector protrusion/latch access, bend radius, slack storage and retention against speaker/tube motion or heat. Distinguish an operating harness from a service loop: extra slack must neither pull terminals during extraction nor fall into the speaker or hot parts when stowed.

Reserve separate routes for power/heater bundles and sensitive input/tank return. The electrical owner determines conductor current/voltage ratings, supply-return grouping, wrong-mate prevention and unmated protection. Both modules need an explicit PE/bonding and residual-charge service design; moving the upper module cannot silently remove lower protective bonding or discharge provisions. This research does not approve connectors or an energized disconnect sequence.

Current tool evidence is only a 46 mm chuck diameter. The known radius is 23 mm, not a complete clearance rule. Full bit projection, chuck length, motor envelope/offset and bit-tip-to-back length are still missing. Check screw-axis approach, engagement and withdrawal at every depth with the selected tool and actual part obstruction. Retain deferred measurement rather than claiming a short or flexible driver solves access. An inert full-size mock-up should demonstrate cover removal, latch operation, supported module withdrawal, socket/tube/chip replacement, lid access and reconnection without cable strain.

## China purchasing leads and comparable cost boundary

These are existing local project leads, not a new shopping selection. All need exact quantity-one domestic price, tax/shipping, availability/date, variant identity and drawings. No contact was made.

| Lead | Recorded catalogue evidence | Qualification/quotation gap |
|---|---|---|
| [Mable MATR0277 PT](https://mableaudio.com/en/productview.asp?sid=10619) | Earlier five-unit plan records US$45 tier at ≥5 | Historical anchor only; page retrieval failed this session. No accepted switchable 120/220 V 50/60 Hz winding/thermal/insulation or complete envelope/mass evidence. Not a quantity-one quote. |
| [Mable MATR0264 choke](https://mableaudio.com/en/productview.asp?sid=8793) | November 12 record: 10 H/250 mA, EI76, 1.6 kg; US$23.35 at ≥5 | Alternative to original 8 H/150 mA/~75 Ω, not drop-in. Need DCR, biased inductance, insulation, full mounting and one-piece RMB delivery. |
| [Mable MATR0280 OT](https://www.mableaudio.com/en/productview.asp?sid=10643) | Directly reread November 26: 30 W, 8.5k primary, 0/4/8 Ω, body 86 × 45 × 72 mm, pitches 57 × 60 mm, 2.1 kg. Header US$57; table ≥5 US$57 | Mounting pitch beyond stated body width means full tab envelope unknown. Different impedance from 7.6k baseline and no accepted EL34 DC/imbalance/leakage/phase qualification. No quantity-one RMB delivered quote or live-stock check. |
| [Mable MATR0233](https://www.mableaudio.com/en/productview.asp?sid=8762) / [MATR0279B](https://www.mableaudio.com/en/productview.asp?sid=10642) | November 24 record: US$58 / US$54 header anchors; 4–6.6k / 10k primary respectively | Both differ from baseline. MATR0233 weight conflicts 2/2.2 kg; MATR0279B 1.45 kg. Full envelope and electrical qualification remain absent. |
| [Mable MATR0265 OT](https://www.mableaudio.com/en/productview.asp?sid=8858) | Earlier US$60 at ≥5; 3.6k primary | Explicitly rejected as direct substitution in November 12 screen. Do not quote its price as cost of a compatible OT. |

Mable is the documented Shenzhen route already used for the delivered cabinet/tank; its directly read MATR0280 page links a [Taobao shop](http://shop36263610.taobao.com). The shop link is a purchasing lead, not verified stock, domestic price or manufacturer certification. Exact auxiliary supply magnetics remain undefined. Existing LCSC/RS China component routes do not themselves provide a qualified lower chassis, magnetic set or complete harness.

For like-for-like A/B/C costing, preserve the same compatible magnetic set, circuit values, required dual-mains hardware and labor scope. Quote separately: metal base/lid/partitions and finish; lower fixed supports/load spreaders; upper supports still required; connector pairs/contacts/caps; rated wire, sleeving/grommets/strain relief; bonding hardware; harness manufacture/testing; tank relocation mounts/cables; extra board fabrication/repack; and assembly/inspection. Credit an upper-metalwork reduction only after actual drawings remove material or work. Moving existing capacitors is not a new capacitor purchase unless the package changes.

The November 24 prototype estimate contains a **¥700–1,100 unquoted magnetic allowance**, plus **¥1,300–2,500** for a broad category covering electronics, PCBs, sockets, controls, harnesses and simple chassis/panel/hardware. Its **¥150–400** dual-mains addition is also unquoted. These are context for a common-BOM comparison, not bottom-module quotations, and cannot be added as independent enclosure prices. The dated selected-parts subtotal ¥359.3217 is already included in that broad category and is not the latest full amp BOM. **No A/B/C cost delta or new total can be responsibly calculated from the present evidence.**

## Gate handoff

| Gate | Result now | Owner / next evidence |
|---|---|---|
| Lower occupied volume clears tank/speaker and independent rear cover | UNKNOWN | Mechanical: common datums, exact speaker/magnetics and complete installed envelopes, then inert mock-up |
| Fixed floor and module metal retain handling/vibration loads | UNKNOWN | Mechanical/builder: wood/joint/support evidence, masses, fastener stack and justified structural checks |
| Whole Power PCB relocation preserves function and fits | UNKNOWN | Electrical + mechanical: populated board/connector model and exact enclosure screen; one bounded repack only if needed |
| Tank orientation retained | Required; no installed pass | Mechanical: horizontal/open-side-down mounting and plug/service proof |
| Magnetic pickup and enclosed thermal behavior | UNKNOWN | Integration/builder: matched loaded placement test and covers-on thermal evidence |
| Upper/lower removal, residual-charge checks and reconnection | UNKNOWN | Joint electrical/mechanical: defined connector state/bonding/discharge procedure plus inert service trial |
| China cost advantage | UNKNOWN | Sourcing: same-revision quantity-one delivered BOM and metalwork/harness quotes |

Research is complete at the P0/P1 feasibility boundary. The next useful artifact is a single shared populated fit/service model with explicit unknown volumes and electrical interface ownership, followed by an inert trial. No blanket measurement request, native edit, final dimensions or supplier order follows from this report.
