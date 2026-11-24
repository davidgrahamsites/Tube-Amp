---
id: VAL-022
type: validation
domain: cross-domain
status: verified
updated: 2026-11-24
---
# Transformer diagnosis and board-only FreeCAD seam

Owner: integration. Authority:FB-112. Verification applies to model/geometry evidence only, not all amplifier performance or manufacturing.

[Feedback review](../../engineering/whole-amp/effects-loop/feedback-review.md):83 AC cases with preserved DC and closed/open return-ratio identity,18 independent transformer terminal measurements,five full0.5s transients and four local HF burst runs.283 provenance/negative-control checks pass. The rejected220pF compensation candidate oscillates at fine resolution while a coarse step hides it; the two fine timesteps agree within0.13% on late peak. No native compensation change adopted. Exact China-source magnetics, actual phase/load/capacitance, supply and fault corners remain open.

[Mechanical review](../../engineering/whole-amp/mechanical/review/board-fit-review.md):actual native outlines and16 mounting holes exported through a read-only adapter; editable FreeCAD/native reopening and STEP solids/positions/rotation/volumes verified. A trial support/flange budget fails width/depth by41/20mm.196 footprints lack3D models; no populated clearance, manufactured chassis or final fastener qualification. Actual drill envelope deferred until November25. Functional blocks and native circuit/PCB bytes preserved.

Next: select/characterize transformer, qualify compensation and loop headroom, add exact component envelopes and repack the desired three boards before routing/release. Keep chassis attachments on fixed cabinet structure and rear wood independently removable. A successful solver completion and a valid CAD solid are necessary evidence, not physical acceptance.

FB-113 adds explicit treble retention for occasional acoustic use in the current electric build.48 matched compensation comparisons at5/10/20kHz are retained; the larger C22 option loses up to2.97dB at5kHz and6.64dB at10kHz relative to the unchanged matched circuit. It remains unadopted. No numeric user bandwidth limit or pickup model was inferred.
