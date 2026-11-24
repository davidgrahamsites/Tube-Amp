---
id: VAL-020
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Logical grounding proof and approximately 25 W reference

Owner: electric integration. Authority: ongoing prototype work and FB-109 power target. This is an engineering checkpoint, not fabrication or hardware acceptance.

[Grounding review](../../engineering/whole-amp/reverb-600/review/grounding-review.md) owns T03: eight native baseline/cut-wire checks, 231 components / 599 connected pins, and all four PCB pad/path checks. Native CAD unchanged. Explicit GB1 proof replaces unconditional PE aliasing. Physical earth hardware and return routing remain T09/T12/T17 gates.

[Power-target review](../../engineering/whole-amp/effects-loop/power-target-review.md) owns T04 evidence: twelve full-window runs; 66 consistency/numerical checks pass. Refined nominal point 25.002 W fundamental into 8 ohms at 1 kHz, 1.767% harmonics-2–10 THD, approximately 3.07 V peak internally. Ideal magnetics and stiff rails are unqualified; the transformer's nonphysical DC transfer is explicitly recorded. No exact 1%/5% threshold or measured power rating.

Next: qualify output-transformer behavior and the all-setting clean/overload envelope, then choose protected RETURN while retaining dry/wet behavior and blocks. Selectable mains follows DEC-015. Independent rear-cover removal, actual drill envelope and all fabrication holds remain.

Human check: inspect linked evidence scopes and verify actual bond/transformer wiring and measured output before treating a logical/model result as hardware acceptance.
