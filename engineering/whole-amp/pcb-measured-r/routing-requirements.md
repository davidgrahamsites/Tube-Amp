# Interference and conductor design contract

Owner: PCB integration; chassis integration owns mounting, shielding and harness envelopes.
Revision: 2026-11-21, FB-075. Applies to electric revision600R-1 and the four current boards.
Inputs: native boards, circuit.json, selected component ratings and mechanical fit-register.json.
Outputs: copper audit, per-net current budget, native routing rules and populated assembly review.
Human check: inspect the actual wiring/earth bond and measure temperature, hum, switching noise and radio susceptibility on the assembled prototype.

## Task card

Keep Main, Power, Control and Reverb ownership intact. First inventory existing widths, necks and bends without altering connectivity. Next establish operating RMS, startup/inrush and fault-protection requirements by circuit path. Only then freeze copper construction and class-specific widths. Preserve existing high-voltage spacing rules; do not weaken them to route. This checkpoint is an audit and design requirement, not fabrication release. Effort: one audit pass now; current qualification and physical validation depend on final magnetics, wiring and construction.

## Assembly and wiring requirements

- Place the mains transformer, mains wiring, rectifiers and first reservoir charging loops in the power area. Keep their outgoing and return conductors close. Keep pulsed reservoir current out of input, preamp and reverb recovery return paths.
- Route heater supply and return as a close twisted pair to the sockets. Keep them away from grids and low-level audio; cross unavoidable signal paths near right angles. Check heater-reference voltage against every tube's heater-to-cathode rating before implementation. Twisting is not a substitute for current and insulation ratings.
- Keep input jack to first grid wiring short. Locate the existing grid stopper at the socket end where practicable. Reserve space for an input RF filter only if susceptibility testing requires it; qualify its effect on guitar loading and treble before changing the circuit.
- Keep tank drive and recovery cables separate. Shield the recovery path. Preserve the specified isolated input and grounded output arrangement, verify shell-to-case continuity on the received tank, and document the complete signal-ground/chassis connection. Do not assume all RCA shells should be bonded to the chassis.
- Put relay suppression at the coil loop and local IC bypass capacitors at supply pins. Keep coil and logic switching returns out of sensitive audio paths. Review control cable filtering and connector-side ESD protection before the expression interface is released.
- Keep speaker/output-transformer current loops away from the input and recovery stages. Evaluate transformer orientation and distance against hum measurements; a nominal90-degree rotation alone does not prove low coupling. Cabinet fit must include these separation envelopes.
- Use protective earth directly bonded to the metal chassis with a dedicated secured connection. Never lift protective earth to cure hum. Signal grounding and chassis bonding are separate review items.
- Fixed chassis metal carries the shielding and electrical bonding. The removable wooden rear cover carries neither electronics nor essential bonding. Any tube guard attaches to fixed metal and preserves cooling, cover removal and service access. Tube visibility remains subordinate to these requirements.
- Reserve full drill/driver approach space outside electrical and harness envelopes. Drill and deburr metalwork before fitting electronics. Verify cassette withdrawal without pulling or pinching bonded/shielded cables.

## Return paths and functional blocks

Partition component placement and current loops. Do not cut a ground plane merely to outline a functional block. Do not route a signal over a return-plane gap. Where blocks connect, specify both signal and return at the interface. Review the present shared GND net geometrically: its name alone does not keep charging, heater-reference, relay and low-level signal currents separate. High-voltage copper spacing remains mandatory even where a continuous low-voltage plane would otherwise be useful.

## Current and copper release gates

For every power path record RMS current, peak/inrush waveform and duration, supply tolerance, branch/return sharing, ambient temperature, permitted rise, permitted voltage drop, copper thickness after fabrication and layer. Include vias, thermal-relief spokes, connector pins, pad necks and off-board wire. Fault protection and fusing need a separate review; steady-state trace sizing does not qualify fault survival.

Use IPC-2152 data or an identified validated implementation with its assumptions for temperature-rise estimates, followed by a prototype temperature test. The public contents page confirms scope but supplies no usable sizing charts. Do not label a generic0.30mm minimum or an old empirical calculator as IPC-2152 qualification. Thin copper at a pad or via can govern the route despite a wide main segment. Trace resistance and voltage drop must be calculated for the actual route length.

Required current families: HEAT_A/B; mains primary; HV secondary/rectifier/reservoir; B+ branches and output transformer; speaker tap/return; control rectifier/relay feeds; reverb supply/driver; local audio; and shared returns. Unknown budgets are release blockers, not default low-current nets. A signal net at high voltage may carry little current yet still need large spacing.

## Trace shape

Use45-degree changes of direction or smooth arcs for new routes. Avoid acute wedges and gratuitous right-angle bends. Inspect transitions into pads, vias and branches separately from simple bends. Do not widen high-impedance audio traces without cause: extra copper can add capacitance and coupling. The reason is controlled geometry, fabrication and parasitics, not electrons colliding with a corner. Corner styling is secondary to loop area, return continuity and spacing for this audio amplifier.

## Verification and evidence

1. Read-only native inventory: widths by net, lengths, vias, exact joined-segment bend candidates and board hashes. This does not establish ampacity or detect every copper neck/zone junction.
2. Qualified per-path current budget and fabrication stackup, followed by explicit native rules and audit of all narrow transitions.
3. Native DRC, pad/net parity, rendered routing inspection and populated chassis/harness interference review after edits.
4. Physical check: earth continuity, tube-temperature effects, heater voltage at each socket, conductor/connector temperature at maximum intended load, hum with input terminated, relay/pedal transients, and controlled RF susceptibility. Record setup and limits. Formal EMC compliance needs an applicable test plan; no compliance claim from a quiet bench test.

Primary references checked2026-11-21:
- TI, PCB Design Guidelines for Reduced EMI, SZZA009: https://www.ti.com/lit/an/szza009/szza009.pdf (loop area, layout and bypassing principles; digital examples require application-specific interpretation).
- TI, Grounding in mixed-signal systems demystified, Part2: https://www.ti.com/lit/an/slyt512/slyt512.pdf (partitioning and return paths; not a tube-amplifier earthing standard).
- IPC-2152 public contents: https://www.electronics.org/TOC/IPC-2152.pdf (conductor thickness, environment, temperature-rise and via scope; full charts not accessed).
