---
id: DEC-014
type: decision
domain: schematic
status: documented
updated: 2026-11-23
---
# Effects-loop qualification and optical-control recommendation

Owner: electric-build integration agent. Authority: engineering recommendation from user-authorized research, not user approval of a component substitution. User events FB-099 and FB-100 requested optical switching research, combined optocoupler/relay study and five-times-skill-plus effects-loop planning.

## Recommendation
Retain existing K1/K2/K3 signal-relay functions and 2N7000 drivers during loop qualification. Shared +12V/GND means an optocoupler before the relay driver adds no system galvanic isolation. It retains coil demand and contact behavior; isolation of a future remote control domain is a separate possible use. Relays here switch audio, not a heavy load. K3 wet-only optical muting is an experiment only if measured noise/pops justify it; preserve de-energized mute and qualify output capacitance/leakage.

The circuit already has J3 EFFECTS SEND and J4 normalled EFFECTS RETURN. The new work is qualification/improvement of that passive interface. Return precedes spring send and passive dry/wet mixing. Lowering its source impedance can change all three transfers. R100 DNP leaves an indirect approximately10.1MΩ DC return through R612/R24, not a completely floating node.

A historical isolated preamp fixture gives approximately11.95Vpeak clean in one case, with far greater clipped extremes. It does not establish integrated signal limits. Do not select±15V recovery until actual PI drive and intended envelope are known; send attenuation alone cannot restore lost return headroom. Discrete HV recovery is an option at the existing insertion point. Additional tubes or insertion relocation require a separate architecture decision.

## Evidence and output seam
- [Reviewed execution plan](../../plans/effects-loop-optical-review/final.md)
- [Independent manufacturer and China-supplier research](../../plans/effects-loop-optical-review/evidence/phase-3-research.md)
- [Circuit extraction](../../plans/effects-loop-optical-review/evidence/circuit-interface.json)
- [Historical preamp-level extraction](../../plans/effects-loop-optical-review/evidence/existing-preamp-levels.json)

## Human check and remaining work
Read the plan recommendation and compare intended use with the qualified pedal/amp envelope before accepting changed behavior. This review changes no native circuit or PCB. Supplier examples remain unqualified candidates; global indexed USD listings do not prove domestic RMB availability. Full-amp model validity, protection, board consolidation/routing, populated fit and actual drill access remain open. Next action: establish the actual loop/PI baseline and recovery envelope.

## Authorized execution checkpoint — 23 November 2026
FB-101 authorizes executing the reviewed plan. [Integrated reference and candidate screening](../../engineering/whole-amp/effects-loop/review.md) now records 74 reference AC cases, 108 separate-SEND branch cases, four completed nominal transients and two refinements. A low-output-impedance unity return buffer changes wet contribution by −2.26/−6.88 dB at checked clean/dirty settings and is rejected as a transparent drop-in. The separate SEND branch preserves checked transfers within 0.134 dB in an ideal-follower test; no galvanic isolation or real short-circuit protection is established. Retain relay/MOSFET controls. Corrected ideal-transformer feedback sign is a model correction only. Heavy-overdrive convergence and recovery voltage/mix topology remain unresolved. LND150 is a researched HV candidate, not a BOM release. Next: resolve the large-signal model gap and qualify recovery before native schematic/PCB integration.

## Numerical correction checkpoint — 23 November 2026
[Domain-guard and manufacturer SEND review](../../engineering/whole-amp/effects-loop/solver-review.md): localized the initial large-signal failure to an unguarded fractional power in the retained EL34 model. Optional fixture-only guard changes checked normal fundamentals by less than 0.00002%; original model files remain unchanged. Ten of twelve heavy cases complete; dirty/5 kHz at both rails still time out. The checked internal signal reaches approximately −80/+66 V, reinforcing that ±15 V unity recovery is unsuitable for transparent overload handling. TI OPAx134 padded SEND tests complete six AC and four transient cases, including limited external shorts; no fault/thermal or integrated hardware release. Keep relay controls and functional blocks. Next: remaining nonlinear/model work and protected HV return design with preserved passive wet mix, then exact parts/native CAD. PCB routing, populated fit and actual drill access remain open.

## Current repair checkpoint — 23 November 2026

FB-102 authorizes continued repair and GitHub upload. This checkpoint supersedes the numerical counts and next actions above. Both original dirty/5 kHz timeouts now complete after saving only measured vectors and allowing bounded 300-second retries. All 12 heavy cases finish; largest checked internal excursion is −135.094/+97.777 V. Save-list equivalence gives zero fundamental change. Full fixture and hardware limitations remain.

[RETURN candidate report](../../engineering/whole-amp/effects-loop/return-headroom-review.md): a three-OPA462 floating-supply experiment completes eight bootstrap cases plus a clipped fixed-supply comparator. Both 20 kHz acceptance cases fail; trap, tighter tolerances and gradual amplitude start do not resolve the fault. ESR diagnostic is incomplete. No RETURN native adoption or headroom qualification. Next: establish the real required envelope, compare protected discrete HV recovery, and preserve dry/wet/spring transfers before exact-part selection.

[PCB adoption review](../../engineering/whole-amp/pcb-measured-r/review/local-loop-review.md): bounded local bypass/relay repairs adopted after hash and native-net checks. Functional blocks preserved. Main/Power/Control/Reverb unconnected counts are 105/39/90/0; courtyard errors 43/12/13/0, all provisional wire ports. Every current circuit pad/net mapping passes. Native UUID reconciliation and explicit signal-ground/protective-earth bond contract remain open; protective earth must not be removed to satisfy a checker. Hole inventory is nominal CAD evidence, not lead/finished-hole tolerance qualification.

Mechanical screening remains unreleased. The reference speaker's 283 mm cutout conflicts with received 270 mm. Four bare-board areas exceed one external top footprint; this does not rule out every multi-plane or consolidated arrangement. Received top opening 307–308 × approximately 53 mm and inside height 383 mm remain the basis. Chassis must attach to fixed structure, with independent rear-cover removal. Drill-tool envelope remains deferred by user. Complete populated layout and access checks after exact components and physical board allocation.

No fabrication release or claim of build readiness.
