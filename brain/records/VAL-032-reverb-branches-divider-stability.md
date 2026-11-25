---
id: VAL-032
type: validation
domain: pcb
status: documented
updated: 2026-11-24
---
# Reverb branch repair and reset-divider stability

[PCB review](../../engineering/whole-amp/pcb-measured-r/review/branch-routing-review.md):
seven additional Reverb T-junctions replaced with fourteen tangent arcs. Exact
native/drill preservation, negative controls, visual review and fresh native DRC
pass (zero violations / zero open connections). Socket verification follows the
explicit delta chain. Four other-board branch candidates remain; current capacity,
remaining routing and return-path/EMI qualification remain open.

[Divider review](../../engineering/whole-amp/control-switching/divider-review.md):
manufacturer-backed TNPW candidates improve the 8,000-hour margin with soldering
and temperature allowances. Longer-duration and combined-stress screens still
fail the unchanged proposed 20 mV allocation. No supervisor/divider is adopted;
exact Chinese stock for the candidate pair is not confirmed. Supplier observations
and the China delivery-policy basis are recorded without claiming an accepted
Shanghai order. No additional nominal simulation is presented as a corner pass.

Current board mechanical inventory, socket screen and FreeCAD native/STEP receipts
were refreshed. Support-plane failures and missing populated envelopes remain.
The measured chuck is 46 mm; full tool access is still pending. Functional blocks,
socket requirement and independent rear-panel removal are preserved.

Next: resolve the supervisor/available divider/carrier as one interface, qualify
current paths, and continue the remaining branch and three-board placement work.
All six through-chassis scopes remain in progress; no fabrication release.
