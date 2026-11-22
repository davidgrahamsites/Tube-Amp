---
id: CMP-001
type: component
domain: components
status: documented
updated: 2026-11-21
---
# Delivered Mable 5E3 yellow-tweed cabinet — fixed build constraint

## Current state
Cabinet AND reverb tank are received, as confirmed by the user. Yellow-tweed cabinet is fixed. Current dimensions and user measurements live in [the mechanical register](../../engineering/whole-amp/mechanical/fit-register.json); A-front/A-rear were reported November20. A/B/C spot measurements are now reported; [received-versus-drawing comparison](../../engineering/whole-amp/mechanical/review/received-vs-drawing.md) records the speaker-pattern discrepancy. Complete populated fit remains open. See [measurement card](../../engineering/whole-amp/mechanical/review/measurement-guide.md). The procurement/candidate material below is retained history, not current instructions to buy another cabinet.

## Identity and role
Shenzhen Mableaudio Company Limited, model 5E3 empty single-12-inch combo shell. The user prefers its appearance; physical/electrical integration is not approved.

## Evidence
[Exact Alibaba listing](https://www.alibaba.com/product-detail/Empty-5E3-wooden-cabinet-for-5E3_60117280028.html) was visually inspected by the sourcing agent on October 3, 2026: MOQ one set, advertised ¥801.08 for 1–9; shipping negotiated. Five advertised shells subtotal ¥4,005.40, not a delivered quote.

[Own supplier listing](https://mableaudio.com/en/productview.asp?sid=848) displays US$120 singly and describes birch plywood. An Alibaba gallery image instead labels pine/MDF/plywood; current stock materials require written confirmation. Published weight fields disagree. The 59×31×52 cm dimensions describe packaging, not the cabinet.

## Required specification and gaps
Obtain actual inner/outer dimensions, chassis/control opening and supports, speaker cutout/bolt pattern and depth, tank floor/mounting area, tube/transformer heat clearance, ventilation/service access, handle/load paths, hardware, joinery, material/finish and packaging. Verify against the released assembly model and prototype. No PCB footprint applies.

The user accepts top-mounted or front-facing main controls. For this candidate, verify that the actual control opening supports an upward-facing panel with enough usable length/depth and knob access. Its appearance and model name do not prove panel capacity or amplifier fit. See [control-placement requirement](DEC-002-combo-shanghai-automation.md).

## Procurement
Prepare a one-prototype delivered Shanghai RMB quotation request, current stock/material evidence, gross/volumetric weight, tax/freight, expiry and substitution restrictions. Five-piece pricing is deferred. A tier price is not a delivery guarantee; supplier contact and purchases still require authorization.

## Next check
Resolve source amplifier geometry before making a purchase-ready fit drawing; obtain a dimensioned supplier drawing or measured sample. See the [active prototype plan](../../plans/renegade-working-prototype/plan.md).

## November 11 dimension recovery

The exact product page still lists this empty cabinet through the China-based supplier. Three linked manufacturer drawings were recovered and visually inspected: width508mm,height420mm,depth215/242mm,top opening312mm; baffle468x380mm,cutout270mm,bolt circle312mm. See [dated research and original images](../../engineering/solid-state-reverb/evidence/cabinet-research.md). This closes the external-drawing gap, not actual chassis/support/tank/speaker fit or current stock/material confirmation. No supplier messages or purchases were sent.

## November19 all-view fit review

[Current review](../../engineering/whole-amp/mechanical/review/fit-review.md) supersedes any implied stock-speaker or flat-board fit. It records concrete speaker-hole and single-plane-board failures, ambiguous baffle attachment dimensions, and the installed-clearance gaps. [Tank specifications](../../engineering/whole-amp/mechanical/review/tank-specifications.md) distinguish Mable's conflicting mini-tank listing from the original8EB2C1B reference. Three-view drawing evidence does not release the complete assembly. Supplier clarification draft remains unsent.

## November19 user correction: delivered cabinet

Cabinet is on hand and is a fixed requirement. Earlier preferred-candidate/procurement sections are history. Redesign boards/chassis and choose compatible internal parts, preserving yellow tweed and the original six-tube amp. Stop making repeated supplier datasheet requests the next step. Actual cabinet measurements override ambiguous drawings. Later user confirmation: tank also arrived. See current state above; the earlier arrival uncertainty is superseded.

## Received tank photo checkpoint — 2026-11-20
See the [photo intake](../../engineering/whole-amp/mechanical/review/received-tank-photo-intake-2026-11-20.md): six original photos archived and hash-checked, label and socket identity confirmed. Coil readings and dimensions remain unmeasured; no fit or electrical release follows from photographs.

Subsequent DC readings are now recorded in the [canonical register](../../engineering/whole-amp/mechanical/fit-register.json). The earlier pending-reading note is closed; AC behavior, grounding and dimensional checks remain open. Simulation updates must distinguish measured DC resistance from assumed inductance.

## Received tank dimensions — 2026-11-21
User reported T1/T2/T3 outer envelope149.5×60×36.5mm. See the [canonical mechanical register](../../engineering/whole-amp/mechanical/fit-register.json) for datums and uncertainty, and [current specification note](../../engineering/whole-amp/mechanical/review/tank-specifications.md). This closes the basic reported-envelope gap, not mounting-hole, cable or assembled fit qualification. Earlier catalogue tank dimensions are not the received-unit design envelope.
