> November21 S1 update: user confirmed approximately **270mm (27cm)** across the large speaker opening. This agrees with the supplier drawing's nominal Ø270mm cutout. The earlier27mm wording is superseded by explicit unit confirmation. This is separate from the294mm opposite mounting-hole readings and210mm adjacent readings; those remain unchanged. Exact dimensional uncertainty and a second perpendicular aperture reading were not supplied. Final chosen-speaker template, basket/depth and assembled fit still require checks. Canonical source: `cabinet.user_measurements.S1_aperture` in [fit register](../fit-register.json).

# Received cabinet versus seller drawings — 20 November 2026

Owner: mechanical integration. Scope: requested A/B/C spot-measurement comparison, now completed. This is not whole-assembly fit approval. Canonical dimensions/source statements: [fit register](../fit-register.json). Reproducible arithmetic: [fit screen](fit-screen.json), received_vs_drawing section. All three drawings were inspected previously; the front drawing was visually rechecked for this comparison.

| Measurement | User reported | Seller drawing | Result |
|---|---|---|---|
| A-front / A-rear clear inside width | 467 / 467 mm | 508 mm outside width; 468 mm separate baffle width | **Not specified directly.** These are different surfaces/components. The 1 mm numerical difference from baffle width is not a verified tolerance match. |
| B, speaker-board rear face to cabinet rear edge | 160 mm | 215 mm top / 242 mm bottom external depth | **Not specified directly.** Internal clearance and outside depth cannot be compared as the same dimension. |
| C1, opposite speaker mounting-hole centres | 294 mm | Ø312 mm mounting circle | **Differs: 18 mm smaller across the circle.** |
| C2, other opposite pair | 294 mm | Ø312 mm mounting circle | **Differs: 18 mm smaller across the circle.** |

Both opposite-hole measurements agree with one another. The initial294mm diagonal interpretation is now supplemented by three210mm adjacent readings; use the measurement reconciliation below for part screening. The drawing and reported cabinet disagree on this datum; do not assume the delivered unit follows the drawing or that this alone means the cabinet is unusable. Exact measurement uncertainty, stud/hole dimensions and angular positions are not independently verified. No general manufacturing tolerance is provided in the drawings.

## Effect on the design

- Keep the cabinet already delivered. Choose the speaker and redesign the internals around the actual measured space.
- Earlier speaker rejection based solely on the drawn312mm circle is historical. The reference Celestion297mm circle would instead differ3mm diametrically/1.5mm radially from the reported294mm pattern. This does NOT qualify that speaker: actual mounting hardware, available hole/slot clearance, cutout and depth still require checks.
- Use467mm width and160mm depth as reported spot clearances, not a finished chassis outside size. Allow for chassis walls, supports, mounting hardware, wiring and service space. These measurements do not establish a complete rectangular free volume.
- Keep the drawing's270mm speaker cutout and other dimensions labeled drawing-only until checked. The known8mm baffle-attachment dimension conflict remains separate from the speaker holes.
- Final speaker/magnetics/tube/tank/board assembly fit remains open. No purchase, drilling or PCB release follows from this comparison.

## Additional adjacent-hole cross-check

User subsequently reported21cm, interpreted as top-left to top-right neighbouring centres:210mm. This is a separate measurement, not a replacement for C1/C2. For an ideal square,210×√2=296.985mm diagonal;294÷√2=207.889mm adjacent spacing. The readings therefore differ from an exact-square relationship by about3mm on the diagonal. Measurement precision or a non-square mounting pattern could account for this; neither is established. A rectangular pattern with210mm horizontal spacing and294mm diagonal would have about205.757mm vertical spacing, so equal diagonals alone do not establish a square.

The drawn312mm circle with equally spaced45degree holes implies220.617mm horizontal/vertical adjacent spacing. The additional210mm reading remains inconsistent with that drawing under the stated interpretation. Do not silently average the measurements or publish final drilling coordinates. Recheck centres and adjacent vertical spacing when selecting exact mounting hardware/speaker.

Bottom adjacent pair subsequently reported210mm, matching the interpreted top pair. Vertical pair dimensions remain unreported; approximately206mm is a conditional rectangular-pattern calculation, not a measured dimension.

## Right-side measurement and practical resolution

Right vertical spacing is also reported210mm. Top,bottom and right adjacent measurements agree at210mm; an ideal square of that side has296.985mm diagonal. Reported294mm diagonals differ by about3mm. Approximate square geometry is plausible, but neither exact294mm nor exact297mm mounting diameter is established. This is a measurement/geometry discrepancy, not an approved294–297mm manufacturing tolerance. The prior instruction to treat294mm as exact was too firm and is superseded by this reconciliation.

No tangent measurement is required. Adjacent spans and diagonals are straight lines between hole centres. User highlighted practical measurement difficulty; stop repeated tape refinements for now. This is sufficient for preliminary speaker screening. Use an exact speaker mounting drawing, full-size template or trial fit for final stud/hole/cutout/depth acceptance. Three adjacent readings would implyabout297mm rather than the seller drawing's312mm circle, so the drawing discrepancy remains.
