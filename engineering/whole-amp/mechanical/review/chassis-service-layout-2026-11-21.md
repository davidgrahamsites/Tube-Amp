# Removable chassis service proposal

This is a construction arrangement, not a dimensioned chassis or a fit approval. Canonical constraints are in `../fit-register.json`, under `chassis_service_study`. The generated SVG is a schematic view with no scale.

## Mounting and service sequence
1. Attach the chassis supports to fixed cabinet structure. Candidate: side-wall rails with rear-facing retaining screws. Wood attachment, insert/bolt type, load capacity and final location remain unresolved.
2. Keep the upper rear wooden cover entirely independent. Its screws hold only that cover. Remove the cover to expose chassis retaining screws.
3. Point the drill/driver straight into each retaining screw from behind the cabinet. Reserve space for the chuck, tool body, bit, fingers and withdrawal. A wide flange alone does not prove access.
4. Support the chassis before releasing retainers. Provide accessible, labelled harness interfaces and an earth-bond service arrangement. Do not use the protective earth wire as a carrying tether. Exact connectors, strain relief, disconnect order and service procedure remain engineering work; this is not an instruction to work on an energized amp.
5. Withdraw the cassette through the rear. Prove its entire swept volume, including tubes, transformers, connectors and guards, clears the fixed wood, speaker and tank. If this fails, use a separately removable carrier while preserving functional blocks; do not force the cabinet.
6. Place the cassette on a stable bench support. Reach PCB fasteners from their screw-head side. Metal flanges extend outside the PCB footprint; establish screw-axis overhang from the actual tool envelope plus handling margin and fastener edge distance. Reserve electrical clearance to the metal too.
7. Drill and deburr bare metal before electronics are fitted. Use controlled torque for final screw tightening; a powered tool must not bend the board or crush standoffs.

## Block ownership
Main retains the original amplifier signal circuitry. Power retains supply/bias circuitry. Control retains switching logic. Reverb retains solid-state drive/recovery/mix. This checkpoint changes packages within their existing boards; no circuit was moved across these interfaces. Final physical compartments, tube-socket position, shielding and interconnect routes remain to be resolved together.

The four present board outlines occupy 109,900 square mm. The reported 467 by 160 mm rectangle has only 74,720 square mm. Even with zero spacing, the unchanged boards cannot share that one plane. A multi-plane carrier or repacked boards is required. This area calculation is a necessary screen, not a 3D fit result.

The natural tube-glow preference is retained. Align suitable tubes with the two oval rear slots only after heat, guards, socket removal, magnetic separation and block layout are resolved. No tube position or sightline is approved yet.

## Received measurements and next work
P1=307–308 mm and P2-clear≈53 mm were supplied under upper rear cover ON instructions. P3=383 mm was supplied under cover OFF access instructions, from fixed top underside to fixed inside floor top. They are user measurements, with no stated tolerance or independent setup verification. The383 mm is total inside height, not a free chassis height once the speaker is installed.

The revised ten-control staggered study occupies215×48 mm, within a conservative307×53 mm rectangular screen. Minimum nominal knob gap4.414 mm and frame gap2.5 mm. Rounded opening shape, finger access, knob seating and actual face elevation remain unverified. The former60 mm-deep layout is superseded. No further ruler measurements requested now; next allocate selected speaker, magnetics, socket/tube/service and wiring envelopes before sizing the cassette and support flanges.

## Checkpoint result
Six exact packages integrated. C602 now uses 10 mm pitch; SEND_TOP trace endpoint shortened to the new pad. C321 moved 0.5 mm left and 1 mm upward to clear CLK_REV after adopting the larger pads. All four native DRC reports have zero violations. Main/Power/Control retain 105/39/99 unconnected items; Reverb has zero. All 444 pad/net checks pass, including ten explicit no-connect pads. Previous source boards are unchanged. These checks do not establish cabinet fit, thermal safety or routing completion.

Native project design rules were restored byte-for-byte from e6811e6 after detecting KiCad SaveBoard project-setting serialization. Both new mutation factories now preserve paired project bytes. Fresh DRC under those original rules retained the results above. No rules or exclusions were relaxed.
