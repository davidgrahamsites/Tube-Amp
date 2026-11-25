---
id: VAL-040
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# RETURN supply/bypass diagnosis

[Review and task card](../../engineering/whole-amp/effects-loop/return-supply-review.md) retain eight causal cases, including two reproduced timestep failures and two10nF timeouts. Adding50Ω isolation after each floating supply follower allows both20kHz cases to complete with100nF bypass retained. Ten regression cases and two half-step refinements complete;108 evidence checks pass with explicit negative controls and unchanged native board hashes.

This unadopted fixture gives approximately−0.2815dB gain error at20kHz and half-step amplitude change below0.00787%. It is not an integrated RETURN, complete-band, startup, noise, protection, thermal, socket or Shanghai-purchasing qualification. It does not establish that TI's published circuit is unstable. Three high-voltage ICs/additional rails remain outside the build; LND150 is a researched lower-cost direction, not a selected substitute. The prior passive wet-mix conflict remains open.

Next: current loaded-output clean/overload and source-impedance envelope, costed discrete comparison, then integrated dry/spring/wet preservation. Functional blocks and all native mounting geometry are preserved. Goal scopes1–6 remain open; full drill access still needs dimensions beyond the measured46mm chuck. No mail, purchase or fabrication release.
