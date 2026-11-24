# Output-transformer screening — 24 November2026

Owner: electric integration. Status: research, **no exact part selected**. Target remains approximately25W guitar amplifier, economical and sourceable in China. Keep the original two-EL34 output block and current7.6k full-primary /8Ω simulation basis until an explicit load-line change is validated.

[Hammond1650F manufacturer data](https://www.hammfg.com/files/parts/pdf/1650F.pdf) provides a useful specification example:25W,7.6k centre-tapped primary,4/8/16Ω connections, full-primary DCR210Ω and separately stated inductance/leakage measurement terminals and conditions. Its10.40mH leakage entry is for Brown–Red, not automatically the full-primary value used in our fixture. This Canadian reference is **not a sourcing choice** and no premium hi-fi bandwidth requirement is imposed on this guitar build.

A domestic supplier route is [Mable MATR0233](https://www.mableaudio.com/en/productview.asp?sid=8762), advertised as40W push-pull for EL34/6P3P, selectable4–6.6k primary impedance,0/4/8Ω secondary, EI86 core and inductance above100H without useful test conditions. Body text gives2kg while header gives2.2kg. Listed price is US$58; no current stock, delivered RMB quote or mounting drawing was qualified. The advertised primary range excludes7.6k. Therefore it is **not approved as a drop-in part**, even though the tube family and wattage look plausible. Listed inductance and core designation cannot supply missing leakage, phase, capacitance, physical envelope or thermal evidence. Reviewed November24; no contact/order.

Other [Mable output-transformer listings](https://www.mableaudio.com/en/products.asp?sid=73) include30W,40W and50W options; category titles do not establish fit or the required impedance. Some product pages could not be retrieved. No part was marked unavailable merely because retrieval failed.

Before selecting a domestic stock or custom unit, prepare this data request (not sent):

- Exact winding diagram: full-primary impedance at specified load, CT, phase marks, secondary4Ω feedback and8Ω speaker taps; available alternatives and actual ratio tolerance.
- Winding DCR and DC current rating per half, allowed imbalance; expected B+ and insulation test/rating. Retain insulated flying leads with specified length and strain relief.
- Open/short inductance with exact terminal combinations, excitation frequency/voltage and DC bias; leakage/capacitance or loaded amplitude/phase plots sufficient to fit a model.
- Full-power and overload limits over the intended guitar band, distortion/saturation and temperature-rise conditions. Model high-rail clipping can approach48W;25W nominal alone does not qualify a25W transformer for sustained abuse.
- Overall envelope including bell covers, lead exits, holes/slots/tolerances, mounting plane, mass and orientation. Fasten heavy magnetics to structural chassis, not PCB or removable rear wood.
- One-unit RMB price, domestic delivery, quantity/lead time and return/quality terms. Do not infer these from export USD listings.

[Feedback evidence](../../whole-amp/effects-loop/feedback-review.md) shows why selecting compensation before knowing leakage/phase would be premature. Supplier evidence and subsequent bench checks must be reconciled with the finite model, not made to fit an attractive curve.
