---
id: VAL-053
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Brownout warning window and rejected reservoir trial

[Owned review](../../engineering/whole-amp/control-switching/brownout-timing-review.md) retains32 gradual-collapse cases:20 miss the provisional AC-detector mute allowance before loss of documented regulator reserve;14 still miss it in a simplified combined rail-monitor/audio-headroom model. Actual regulator dynamics, contact motion and audio artifacts are not established by these diagnostics.

A32-case spare-comparator/10000µF-positive-reservoir trial meets the conditional timing comparison but fails healthy-enable in eight low-line/endurance-sensitivity cases. Minimum initial margin22.68mV becomes−136.83mV with the manufacturer-derived capacitance sensitivity. The trial is rejected for adoption; no native files or the existing7.5k precision-candidate bleeder changed. Three timestep repeats,2000 independent node solutions, two closed-form discharge checks, three corruption controls and22 unchanged native CAD files support the retained results.

KNSCHA152EC0344 has a dated Chinese single-piece listing and domestic courier route supporting Shanghai sourcing. The manufacturer permits25% post-endurance capacitance change; general/specific leakage values conflict, so5mA is screened conservatively. Exact footprint, temperature/ESR/ripple/inrush and fit remain pending. The50VA transformer primary source is retained; Chinese stock remains unverified. Next: investigate bounded faster K3 suppression/release with both existing clamp paths and30V driver limit, then reconcile the raw-warning/supply window with exact components and full power sequencing. All six scopes remain open; no fabrication release, purchase or supplier message.
