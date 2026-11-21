---
id: DEC-007
type: decision
domain: cross-domain
status: documented
updated: 2026-11-19
---
# Original amplifier with solid-state spring reverb

## Decision and authority
The user requests the original Renegade schematic as the amplifier baseline, replacing the previous added tube reverb with a non-tube-driven real spring reverb for simplicity. Preserve cabinet and other product choices, including China sourcing and 220 V / 50 Hz mains. Use the circuit-design-skill-ladder and operate needed applications to produce schematic, BOM, build plan, and a PCB following applicable rules.

The user subsequently specified a faceplate knob, then explicitly chose **constant dry plus adjustable added wet**, not a crossfade. Label it REVERB. The user has no measured cabinet dimensions and authorizes research of dimensions and China availability. No supplier contact or purchases were requested.

## Scope
Supersedes the tube reverb architecture in DEC-001 and the v0.3 draft. Preserve the original source and previous drafts. Original six tube envelopes: four 12AX7 and two EL34. Changes required for mains compatibility, ratings and review must be identified rather than represented as original circuitry. Existing footswitch requirements remain unless the user changes them.

## Next checks
Research exact cabinet and tank; keep unknown usable dimensions explicit. Complete circuit and PCB connectivity, ratings, simulations and native checks. Physical fit and energized tests require actual hardware evidence. New deliverables live in `engineering/solid-state-reverb/`.

## Whole-amplifier scope clarification, 2026-11-11
The user explicitly requests continued work until build-ready, resolution of remaining parts and fit, simulations, and PCB coverage of the **whole amplifier**, not only reverb. Current work is in `engineering/whole-amp/`; v0.4 is preserved. Board partitioning may keep transformers, panel hardware, valves and mains wiring chassis-mounted, but all remaining electronic assemblies need explicit PCB/harness coverage.

## Supplier inquiry authorization
On 2026-11-11 the user explicitly approved sending the prepared Mable inquiry and chose admin@goodgaryapps.com as sender. Email sent and verified in Sent at 06:22 local time; see `engineering/whole-amp/evidence/supplier-contact-log.md`. This authorizes the inquiry, not orders or manufacturing. The unrelated green-button instruction was withdrawn by the user and is ignored.

## Exact component sourcing correction — November 11
The user requires every component to be searched and selected for audio quality, durability and low-unit-order price from suppliers selling domestically within China. This includes knobs; supplied visual preference is a black pointer/chicken-head form with a white index. Pot shaft/bore, body dimensions and set-screw fit must be selected together. Provisional PCB envelopes do not constrain part selection; layouts must follow verified parts. No purchase authorized.

## Continuation and knob approval
The user accepted the shown pointer knobs and reiterated exact pot matching, all-component sourcing, and a full amplifier PCB update after exact selection. A shortlist is not completion. On November 11 the user completed the requested LCSC login; signed-in domestic product pricing is accessible. No order authorization.

## Expression pedal confirmed — November12

User accepted a passive rocker-pot expression pedal: heel dry only; toe reaches the faceplate REVERB setting; unplugged restores ordinary faceplate control; dry stays constant. Audio remains in the amplifier, with protected low-voltage control over the pedal cable. Preserve the existing on/off footswitch as a separate function. The [interface requirements and work order](../../engineering/whole-amp/expression-control/requirements.md) define required fault/hot-plug tests and affected artifacts. Exact pedal resistance, connector wiring and control element are not yet selected. Existing boards do not implement this feature.

## November19 seller-confirmed received tank interface

User relayed seller confirmation:3springs,input600ohm,output2250ohm,medium decay,input insulated/output grounded,no lock,horizontal/open-side-down. This supersedes800/2575 as the tank design basis. Tank and cabinet are already on hand. The reply does not establish exact body dimensions, DC coil resistance, impedance test frequency or drive current; do not infer them from a similar model code. Historical800/2575 simulations are reference runs, not verification of this tank. Record: engineering/whole-amp/mechanical/review/tank-specifications.md. Continue physical identification/low-level characterization, not repeated datasheet inquiries.
