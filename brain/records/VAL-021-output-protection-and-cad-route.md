---
id: VAL-021
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Screen protection revision, stress matrix and CAD route

Owner: electric integration. Authority: FB-110/111; ongoing prototype authorization. No fabrication release.

[Electrical review](../../engineering/whole-amp/effects-loop/protection-review.md): adopted socket-local R41/R42=4.7k, minimum10W. Ten full0.5s acceptance cases complete;104 finite-matrix evidence checks pass. Refined1kHz/8ohm result24.536W near5% THD. Checked worst average screen5.232W and resistor5.512W at explicit assumed high-rail/weak-bias/low-R corner. Exact MPN, real thermal/voltage/pulse data, dual-mains corners, load/bias faults and transformer stability remain open. The pessimistic20kHz case completes but does not pass an audio-performance/stability criterion. No block interface or PCB geometry changed.

Native before/after checks preserve named nets/endpoints and every component field except the declared two-resistor changes. Contract reverse delta and baseline-source hashes also match. Explicit GND/PE cut-wire proof still passes. Fixed missing selected-footprint-library entry; ERC13→1, remaining declared GND/PE alias warning, no suppression. Changed output sheet and enlarged branches visually inspected. All-project readability is not re-certified. Pre-existing D3–D6 contract/native value discrepancy recorded for T06.

Fresh PCB checks retain234unconnected and68provisional courtyards. Pad-net mapping passes, board bytes unchanged. [Mechanical handoff](../../engineering/whole-amp/mechanical/review/output-protection-fit.md) records resistor envelopes, independently removable rear cover and pending tool/populated-assembly checks. No drill access or chassis fit PASS.

[FreeCAD capability](../../engineering/whole-amp/mechanical/review/cad-toolchain.md): installed1.1.4, six synthetic-coupon save/reopen/STEP checks pass. NativeFCStd andSTEP automation verified; production chassis, unfold/drawings/render remain incomplete. Smoke-test artifacts were removed; receipt/factory retained.

Next: real-magnetics/feedback envelope and remaining stress/fault/supply cases, D3–D6 reconciliation, protected RETURN, exact parts and physical board/chassis integration. Human check: compare actual parts, wiring, service clearances and measured stresses against the explicit assumptions before fabrication or energizing.
