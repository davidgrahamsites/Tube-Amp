---
id: VAL-037
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Panel cable capacitance affects placement

[HI-003 review](../../engineering/whole-amp/harness-integration/cable-loading-review.md) records 36 unloaded settings, 504 hypothetical loaded cases, eight individual-pot comparisons and two frequency-grid refinements. The independent RC and topology controls pass; native CAD and functional blocks are unchanged.

Several high-impedance pot runs are strongly treble-sensitive. Even 10 pF per lead to ground exceeds the proposed 1 dB comparison budget at many settings. The 3 pF ground/1.5 pF pair row barely passes this bounded matrix and is not a qualified allowance. Exact cable length cannot be derived without the installed capacitance matrix. Prioritize short complete paths for treble/volume/gain/master; no generic equal-length harness, new buffer, shield connection or additional PCB is adopted.

Actual Chinese order identity/delivery, insulation/fault review, physical capacitance, independent control corners, RV9/RV602 and populated connector/chassis fit remain open. No manufacturing release. Next: exact mating geometry and candidate run lengths, then actual-cable loading and insulation checks before schematic/PCB integration.
