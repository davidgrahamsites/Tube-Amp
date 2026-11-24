---
id: VAL-023
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Loaded feedback diagnosis and power-capacitor fit defect

Owner: integration. Authority: continuation of FB-112/113 and the prototype queue. Scope: model evidence and candidate-fit rejection, not amplifier or manufacturing acceptance.

[Loaded-winding review](../../engineering/whole-amp/effects-loop/loaded-feedback-review.md): 18 analytic probe controls, seven winding checks, 87 AC cases and four local HF bursts. The 312-check evidence audit passes. Forty-two AC cases fail the engineering response screen; all 18 tested output damping branches fail. The 220 pF feedback negative control sustains approximately 0.936 V oscillation at two fine timesteps. No compensation or native circuit change adopted. The initial transient metric was corrected to remove independently measured DC offset; raw and corrected evidence remain visible.

[P057 fit review](../../engineering/whole-amp/pcb-measured-r/review/fc6136-fit-review.md): corrected mixed Panasonic/CRC metadata. FC6136 needs a 20.3 mm row pitch; all four native power-capacitor footprints have 10.2 mm. Centered maximum-body projections overlap by 0.95 mm in two pairs. New five-control read-only guard detects the mismatch; no footprint replacement or assembled-fit approval. Exact lead tolerances, terminal grouping, support and revised placement remain open.

[Additional China supplier screening](../../engineering/component-selection/evidence/output-transformer-screen-2026-11-24.md) adds MATR0280/0279B/0241 with explicit impedance, dimensional and evidence limitations. No exact transformer selected, supplier contacted or part ordered.

Next: qualify exact magnetics and compensation before RETURN closure; independently resolve P057 identity/footprint/placement before populated chassis work. Preserve separate functional blocks, fixed-structure chassis attachment and removable rear wood. Actual drill envelope stays pending until November 25. T04 remains active and all manufacturing gates remain held.

Checkpoint validation: scoped ICM checks for effects-loop, pcb-measured-r and component-selection are clean. Both brain catalogs rebuild with valid IDs, paths and nonduplicated component coverage. The new capacitor guard completes with five controls passing and fit explicitly rejected; the loaded-feedback audit reports 312 evidence checks passing. These results do not close T04 or fabrication gates.
