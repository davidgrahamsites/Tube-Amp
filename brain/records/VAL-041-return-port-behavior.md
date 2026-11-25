---
id: VAL-041
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Effects-loop port behavior and pending choice

[Port review](../../engineering/whole-amp/effects-loop/return-port-review.md) records36 control combinations,324 circuit configurations and2592 exact-frequency AC solutions. Complex port predictions match direct full-circuit comparisons within1.675e−9 relative error;382 evidence checks pass. All four native boards are unchanged.

A1MΩ-input/1kΩ-output unity buffer changes wet gain by−7.501 to−0.636dB and dry gain by+0.070 to+2.117dB in the declared sampled ranges. All eight fixed output-resistance candidates fail the proposed preservation screen. Native1kHz wet transfer varies6.272dB with controls; a control-independent replacement cannot match both extremes within±0.5dB, even after a fixed trim. This is nominal-model interface evidence, not a qualified recovery circuit or hardware measurement.

FB-121 asks for [functional diagrams of all three options](../../engineering/whole-amp/effects-loop/signal-path-options.md). It is not topology approval. The choice between a consistently buffered/recalibrated path, original bypass with different effects-mode loading, and more complex compensation remains open. No part adoption, extra tube, insertion relocation, native change, supplier contact, purchase or fabrication release. Continue independent China-device qualification and required-envelope work while awaiting the behavior choice.


November 25 follow-up: FB-123 / DEC-016 selects option 1, consistent buffering in effects and bypass modes with reverb recalibration. Earlier choice-pending language above describes the experiment checkpoint; component and circuit qualification remain open.
