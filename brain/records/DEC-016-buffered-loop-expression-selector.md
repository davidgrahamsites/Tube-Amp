---
id: DEC-016
type: decision
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Buffered loop approved; expression selector requested

Owner: electrical integration. FB-123 accepts option 1 in the three-path comparison: common SEND and RETURN circuitry in loop and bypass modes, loop before spring reverb, recalibrated dry/wet mixing. The original passive loading need not be reproduced; tone, headroom, noise and consistent mode behavior still require qualification. VAL-041 remains baseline evidence, not validation of the eventual circuit.

FB-124 requires a dedicated reverb expression jack and PANEL / EXPRESSION selector. FB-125 proposes a miniature toggle, matching pedal/knob resistance and debounce. The image establishes appearance only, not pole count, contact rating, dimensions or a selected part. Preserve constant dry, separate reverb on/off control, protected low-voltage pedal wiring and removable rear panel.

The newer wording describes selecting one control in place of the other. Proposed interpretation: independent full-range pedal control in EXPRESSION mode rather than the earlier knob-times-pedal relationship. This interpretation is stated to the user; do not silently retain the old panel maximum limitation or claim it explicitly approved. Exact control law, parts, transition smoothing and fault handling remain engineering work. See [selector review](../../engineering/whole-amp/expression-control/selector-review.md).

No native schematic/PCB change or release follows from this decision record. Next: select the wet-only gain-control method, establish endpoints/taper/pinout and protection, then simulate before native integration and populated fit checks.
