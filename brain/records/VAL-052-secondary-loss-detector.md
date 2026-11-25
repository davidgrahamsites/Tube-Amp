---
id: VAL-052
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Secondary-loss detector and shared inhibit interface

[Owned review](../../engineering/whole-amp/control-switching/ac-loss-review.md) records84 loaded-supply cases,48 finite interruptions and four half-timestep repeats. The unadopted diode/film/comparator detector has7.839ms maximum conditional detection delay and3.735ms minimum permanent-cutoff reserve after the provisional relay/logic timing allowance. All four finite interruptions losing raw headroom request inhibition early enough, with6.810ms minimum residual reserve. Five short fault pulses cannot establish the prior50ms restart hold; those five retain headroom. One restore trace chatters. Neither quiet recovery nor actual relay contact timing is qualified.

Independent2,000-node comparisons, two branch-current RK4 replays, corruption controls and22 unchanged native CAD files support the calculation. Added comparator loading requires a candidate REF5 bleeder change8.2kΩ→7.5kΩ; the combined conditional reference budget is9.851mA and passive reference-off RAIL_OK0.819V. Precision monitor14 conditional checks still pass; semiconductor sequencing remains open.

Exact Chinese listings show stock for onsemi1N4148TR, KNSCHA82CL0125 and TI LM393BIDR; physical pack quantities, exact resistors, removable comparator carrier, transformer/reservoir and Shanghai checkout remain pending. Manufacturer documents and dated listing hashes are retained. Next: slow brownout and complete reference/logic sequencing, then actual mute response and exact parts before native integration/populated three-board fit. All six scopes remain active; no fabrication release, purchase or supplier message.
