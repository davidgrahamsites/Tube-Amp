---
id: DEC-014
type: decision
domain: schematic
status: proposed
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
