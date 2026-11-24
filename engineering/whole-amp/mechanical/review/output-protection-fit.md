# Output-protection mechanical handoff — 2026-11-24

Owner: mechanical integration. Inputs: current fit-register.json, four native PCB outlines, output-protection experiment and manufacturer part drawings. This is a constraint check, not a populated chassis model or fabrication release.

R41/R42 belong at the output sockets on the removable metal chassis. Preserve short screen-side connections, insulating/support hardware and PCB-side removable supply connectors. The rear wooden cover supports none of this hardware. Resistor bodies must not obstruct socket retention, tube extraction, retaining-screw approaches, chassis withdrawal or cabinet-side cable disconnection.

Two documented 4.7 kΩ / 10 W package candidates have materially different envelopes:

| Candidate | Maximum body envelope | Maximum round lead diameter | Status |
|---|---|---|---|
| RESI EWWR0010J4K70T9 | 37.5 mm long × 10 mm diameter | 0.80 mm | China catalogue candidate, exact working-voltage/pulse and thermal qualification pending |
| Yageo SQP10AJB-4K7 | 49.5 × 10.5 × 10 mm | 0.85 mm | China catalogue candidate; stock/one-piece availability not freshly confirmed |

Body dimensions do not include bent leads, terminal supports, insulation, heat exclusion or tool space. No board hole is required by the present socket-local allocation; any future support PCB requires a finished-hole tolerance/lead-fit check. Do not equate the body envelope with a safe hot-component keepout. See the component research and electrical protection review for sources and ratings.

The current Main/Power/Control/Reverb outlines remain 290×140, 160×175, 230×110 and 160×100 mm. Their 109,900 mm² area exceeds the provisional 467×160 mm rectangle (74,720 mm²), even before flanges, transformers, tubes, connectors and cable bends. The 160 mm depth datum is unresolved. Three-board consolidation and a populated arrangement are still needed; rearranging functional boundaries is not authorized by this area result.

The installed control opening is 307–308 × approximately 53 mm; inside height is 383 mm. These dimensions do not establish the rear extraction aperture or speaker/tank/magnetics clearances. The reference speaker's required 283 mm cutout still fails the received approximately 270 mm aperture.

Drill/driver diameter and bit-tip-to-back length remain deferred. Flange width and screw coordinates cannot receive a tool-access PASS without them. Preserve the existing rule: at every point on the tool approach/withdrawal, screw-axis distance to obstruction must exceed the local tool radius plus handling margin; also reserve fastener edge distance. Existing service architecture is independent cover removal, rear-facing chassis retaining screws, bench support and unplugged cabinet-side harnesses.

Next mechanical action: select the socket/retainer, transformer and speaker envelopes; allocate protection bodies and supported terminals on the chassis; create the populated FreeCAD assembly, then check full removal and tool sweeps. No dimensional chassis or supplier release is produced by this handoff.
