> November20 update: A/B/C measurements are now available. The received294mm speaker pattern supersedes the drawing-only312mm assumption for selection. Read [received-versus-drawing comparison](received-vs-drawing.md). The historical screens below do not reject a speaker against the actual cabinet.

> November19 correction: cabinet is delivered and fixed. This review diagnoses draft-part/layout conflicts; it is not a recommendation to replace the cabinet. The two-plane sketch is exploratory only. Actual cabinet spot measurements have priority over ambiguous drawing callouts.

# Complete-amplifier fit review — 19 November 2026

**Verdict: not cleared for purchase, drilling or PCB release.** All three cabinet views were inspected. There are definite clashes with the current assumptions, plus missing assembly dimensions. This is a completed evidence screen, not a completed 3D fit validation.

## Inputs and ownership

Owner: current Renegade integration agent. Canonical dimensions: `../fit-register.json`; calculations: `../tools/check_fit.py`; results: `fit-screen.json`. Requirements stay in the root handoff. Native boards were read, not modified. User drawings were supplied November16; top PNG is preserved under evidence. The two WeChat temporary files are no longer on disk, but all three corresponding manufacturer views were already preserved under `../../../solid-state-reverb/evidence/cabinet-size-01.jpg` through `03.jpg`; each was visually re-inspected against the supplied views.

## Drawing readout

| View | Dimension evidence | What it does not prove |
|---|---|---|
| Top | 508 width; 312 opening between straight sides; 344 stepped width; 67 opening depth; two R31 corners; 11 diameter5 holes and offsets shown | Chassis interior, support-block positions, bolt projections, material tolerance or installed clear space |
| Side | 420 height; 215 top and242 bottom depth; 48 rear strips; 9/18/11/25 offsets | Usable depth behind speaker, shelf/chassis height or exact interpretation of all material layers |
| Front/baffle | 468×380 panel;270 cutout;312 speaker bolt circle; four diameter5 holes at45degrees; speaker center204 from left as drawn | The cabinet interior is not necessarily468×380. Two9mm side labels do not establish one9mm assembly. |

Baffle speaker center is30mm left of the panel midpoint in the shown view. Height-center190mm is inferred from symmetry, not separately dimensioned from the panel edge. Keep viewing direction attached to coordinates; a rear-view mirror flips the horizontal offset. Do not fabricate from inferred hole positions.

**Drawing conflict:** side offsets20+20 with overall468 imply428mm between outer attachment rows; lower labels218+218 imply436mm. Difference8mm. Clarify which callouts apply to which layer/datum before drilling. The speaker bolt circle is a separate callout.

## Whole amplifier

Native KiCad outlines read November19: Main290×140, Power160×175, Control230×110, Reverb160×100mm nominal. `GetBoardEdgesBoundingBox` includes0.05mm total edge-stroke growth in both axes; this agrees with the stored nominal outlines. KiCad emitted wx initialization/image-handler warnings but loaded all four boards and returned geometry; no save operation occurred.

Total bare-board area109900mm². The entire *external* top footprint is508×215=109220mm². Therefore the four unchanged boards cannot all lie flat, without overlap, within that top footprint—even before chassis walls, standoffs, wiring, tubes or transformers. This does not prove that every lower-level/vertical arrangement fails.

A board-only two-plane arrangement is geometrically possible inside an **assumed**, unverified468×190mm tray: Main+Reverb side-by-side with8mm gap occupy458×140; Power+Control occupy398×175. This is a routing direction, not an assembly design. Board populated heights, interplane insulation, capacitor venting, heat, extraction and access need actual parts. The source tube count remains four12AX7 and twoEL34. No actual PT, OT, choke or auxiliary transformer outline has been approved; historical reference sizes cannot stand in for them. All six socket/shield/retainer envelopes, tubes and magnetic components must be inserted before 3D interference review.

Controls: ten26mm knobs alone occupy260mm before spacing; a312mm opening leaves52mm for all gaps and margins, with no allowance for jacks or switches. Two rows are a possible direction; exact shafts/pot bodies and rounded opening clearance remain open. Do not drill a stock three-control5E3 chassis for this design.

## Speaker

There is no final exact speaker selection in the current records. Existing candidate Celestion Seventy80 has309mm frame,297mm four-hole PCD,7.9mm mounting holes,119mm overall depth and134mm magnet. Manufacturer: https://celestion.com/product/seventy-80/ (checked November19).

Its bolt circle differs from the supplied312mm pattern by15mm diameter /7.5mm radius. Even the combined radii of the5mm cabinet hole and7.9mm speaker hole are only6.45mm. The holes cannot share a straight pin with the driver centered. **Unchanged baffle-hole fit fails.** A factory-drilled matching baffle or a verified compatible speaker is needed; no cabinet alteration has been executed or approved by this report.

Frame projection fits within the panel outline at the drawn horizontal center:49.5mm left and109.5mm right margins;35.5mm top/bottom if the inferred vertical center is correct. These figures do not establish cone clearance through the270mm aperture. Celestion's reviewed page does not state the required cutout. Its119mm depth is also not a rear-clearance result: baffle setback, rear panels and chassis positions remain unresolved. LaVoce WSF121.70G is still an alternative, not selected or mechanically cleared.

## Reverb tank

See `tank-specifications.md`. The bare reference Type8 body is small compared with the cabinet exterior, but the quoted Mable item is ambiguous. No approved floor location exists. Model the actual tank plus bag, compliant mounting, RCA plug projection/bend space and fastener clearance, horizontal/open-side-down. Check speaker-frame/magnet and amp-module interference and hum pickup after placement. A tank may fit geometrically and still hum excessively near transformers.

## Work that must close the fit

1. Supplier identifies quoted tank and confirms cabinet drawing applicability, dimensions/datum conflict, interior supports and actual clear floor/chassis space.
2. Choose a speaker with an exact mounting drawing; resolve its baffle pattern/cutout before purchase.
3. Freeze actual transformer/socket/tube/large-cap envelopes and chassis/board arrangement. Keep yellow-tweed shell choice.
4. Build a dimensioned 3D assembly, check populated-board/tube/magnetics/speaker/tank interference, fasteners and service paths; then revise board outlines/routing as required.
5. Verify physical fit, ventilation, handle/load paths and vibration on the prototype. Current screen does not certify thermal or electrical safety.

No mail, purchases, drilling or native PCB edits performed. Stable checking code is separated from evidence and review products. Root status and mechanical contract link this result.

## Checks performed

`check_fit.py` regenerated the arithmetic results and checked known values. All three cabinet source paths exist; evidence SHA256 hashes saved in `evidence-hashes.json`. `render_fit.py` generated PDF/PNG and the PNG was visually inspected. Initial macOS plotting backend aborted; the renderer now explicitly uses the non-GUI Agg backend and succeeds. Scoped ICM checker reports clean for this module. Manual seam review confirms register-only geometry input, independent check/render tools and separate evidence/products. The geometric failures above remain failures; checker cleanliness is not an assembly-fit pass.
