---
id: VAL-028
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Logic-level relay drivers and local clamps

Owner: Renegade integration. Advances T06/T08 under the existing socket, Shanghai sourcing and six-scope requirements; it does not close them.

[Control-switching review](../../engineering/whole-amp/control-switching/review.md) owns the exact changes, retained decks/results, manufacturer sources and dated domestic observations. Q1/Q2 change from 2N7000 to AOS AO3400A with verified G1/S2/D3 mapping. D333/D342 add controller-side drain clamps while D331/D332/D341 remain beside the remote coils. New routes preserve functional ownership and use H/V/45-degree segments. All previous copper, unrelated footprints and mounting holes are unchanged.

Independent native comparisons pass, including wrong-gate and undersized-hole negative controls. KiCad Excellon confirms four 1.2 mm diode holes and two 0.4 mm drain vias replacing the six old transistor holes; all unrelated drills/slots are preserved. ERC retains one existing finding. Control DRC retains 13 existing findings, with unconnected items reduced from 90 to 84. Source, board plan and coverage agree on the adopted parts. R215's missing board-plan entry was also reconciled to the already verified circuit/PCB.

32 driver runs, ten nominal TI supervisor runs and 13 finite-rail/harness sensitivity runs completed. The local-clamp cases remain below 13.47 V in the tested models; remote-only and missing-decoupling controls exceed 30 V. These use explicitly bounded surrogate assumptions, not measured harness or manufacturer MOSFET/relay transient qualification. The candidate TPS3890 remains unadopted: manual-reset model timing, fast collapse, threshold margin, edge conditioning and its removable carrier remain open.

The temporary process-launch outage is resolved: KiCad 10.0.6, native export and independent checks ran again. No fabrication release. All 16 IC/tube socket assemblies remain tracked but unqualified. Populated three-board conversion, exact magnetics and drill clearance remain open; actual tool dimensions are deferred to November 25.
