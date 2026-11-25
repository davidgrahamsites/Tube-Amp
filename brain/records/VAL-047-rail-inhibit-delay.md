---
id: VAL-047
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Rail-inhibit delay and short-fault limit

[Owned review](../../engineering/whole-amp/control-switching/rail-delay-review.md) records192 conditional RC corners and384 independent current-integration comparisons. Ten arithmetic/logic screens pass; a separate brief-fault hold screen fails. Settled-fault recovery is54.650–864.386ms under allocations, but0.1–1ms faults can recover without50ms hold. Direct driver inhibit does not prove immediate relay-contact or quiet-audio response.

Candidate uses existing socketed U1E/U1F and two proposed transistors; no native CAD/BOM change or socket exception. KNSCHA82CL0117 has Chinese stock356/minimum1;33k TNPW candidate has zero stock. Hot-component limits, exact precision-network sourcing and Shanghai checkout remain open. Primary sources and numerical hashes are retained in the module.

Next: full rail/reset/driver/contact-response model and audio fault-width requirement, then sourceable component qualification and native integration gates. All six scopes remain active; no manufacturing release or fit/drill-access approval.
