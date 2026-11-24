# Through-chassis execution card

Owner: Renegade integration. Updated 2026-11-24. Authority: FB-114–116 and the canonical handoff. This card interprets the six requested scopes; it does not replace the ordered [task queue](tasks.md).

## Inputs and process

Use the active `reverb-600/circuit.json`, current `pcb-measured-r` boards, exact component coverage and the measured cabinet contract. Use the latest verified package checkpoint (VAL-025 follows3efa8d9); preserve unrelated in-progress edits. Select available parts before freezing dependent values, footprints or geometry. A substitute reopens its affected electrical and mechanical checks.

All ICs and all six tubes must be socketed. Include regulators, the supervisor and any future effects-loop IC. Surface-mount adapters are only candidates until their contacts, pin map, spacing, retention, bypass placement and thermal path are qualified. Never equate a DIP footprint with an installed socket. Include socket height and extraction space in the populated assembly.

## Six scopes and closure evidence

| Scope | Queue | Remaining evidence |
|---|---|---|
| 1. Transformer/output stage | T04/T08 | Exact available transformer; winding/DC/current/frequency evidence; feedback, treble and load-corner qualification; approximately 25 W reported against distortion. Generic parameter sweeps remain experiments. |
| 2. Effects SEND/RETURN | T05 | Available socketed implementation at the existing interfaces; resolve 20 kHz failures; loading, headroom, overload/recovery and supply requirements. |
| 3. Power/protection | T06/T07 | Both 120 V/60 Hz and 220 V/50 Hz modes; supply/load/heat budget, startup/brownout/shutdown, protection, local bypass and spring-driver limits. |
| 4. Exact parts/footprints | T08/T12/T13 | Manufacturer identities, drawings, pin maps, round/rectangular-lead and slot tolerances, readable schematic and native parity. Chinese purchase route, quantity/MOQ, dated stock and Shanghai delivery basis for every purchase item. |
| 5. Harnesses | T09 | Headers AND mates AND contacts, insulated wire, shielding, crimp method, strain relief, cable ties, service loops and mating/extraction envelopes. |
| 6. Populated three-board chassis | T10/T11 | Audio/power/reverb physical boards with all functional blocks preserved; six tubes/sockets, magnetics, speaker, tank, heat shields, wiring and fasteners. Independent rear removal, chassis extraction and actual drill access. |

Outputs are checked engineering artifacts in their modules, linked evidence and current handoff/catalogs. The design is not build-ready merely because a simulation finishes. Fabrication packages and physical commissioning remain T15–T18 gates.

## Current next actions

1. Inventory socket requirements against every active IC/tube reference, including parts whose package must change; retain pending qualification explicitly.
2. Resolve component constraints in parallel with necessary circuit calculations: regulator contact/heat budget, transformer and capacitor geometry, speaker fit and exact connector mating sets. Work sequentially within each owned module; no independent-worker delegation implied.
3. Rerun affected simulations with traceable inputs. Carry adopted parts into readable CAD only after pin/function and package evidence agree.
4. Repack the populated assembly, then route the three physical boards and rerun electrical/mechanical checks.

## Physical dependencies and human check

Actual drill envelope remains deferred until November 25. Cabinet depth datum, actual speaker fit and 1:1 assembly checks remain open; do not replace them with inferred measurements. Domestic shipping policy establishes a supplier route, not an exact delivered price or accepted order. No purchase, supplier contact or fabrication upload is authorized by this card. At review, trace one part from stock/datasheet through schematic pin, socket/contact, PCB hole and assembly clearance.

## Auxiliary-supply checkpoint — November24
[VAL-026](../../brain/records/VAL-026-auxiliary-supply-envelope.md) adds72raw-supply cases,4refinement runs and3unadopted820Ωpreload comparisons. Evidence checks pass;48base cases have engineering flags. Raw-winding/thermal assumptions remain unqualified. Contact screening has not selected a regulator socket. Native CAD unchanged; exact auxiliary magnetics, preload integration, startup/reset, socket/heatsink and all populated-fit gates remain open.
