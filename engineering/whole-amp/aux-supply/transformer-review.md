# Auxiliary transformer comparison and supplier inquiry

Owner: auxiliary supply qualification. Date: 24 November 2026. No candidate selected or native CAD modified.

## Task and decision

Inputs: the current cold-coil/R215 load model, three explicit reserve profiles, requested120/220V modes, primary manufacturer data and Chinese supplier observations. Output: a reproducible option comparison plus a concrete [transformer inquiry](../../../plans/renegade-working-prototype/transformer-inquiry.md). This checkpoint is complete when input ratios, current rating, simulation evidence and limitations are traceable. Part acceptance requires actual winding tolerances and commercial/mechanical evidence. Estimated effort: one bounded research/simulation pass.

**Do not select a transformer from the old generic ±10% line factors.** For a115/230V primary, the proposed120V±10% screen means108/115 through132/115, or0.93913–1.14783. The220V±10% screen means198/230 through242/230, or0.86087–1.05217. These are engineering operating targets, not a claim about legal utility limits or approved primary operation. Core flux, temperature and actual allowable input range require manufacturer evidence.

## Parts and model

[Triad VPT30-830](https://catalog.triadmagnetics.com/Asset/VPT30-830.pdf):25VA, two15V secondaries rated0.83A in series,115/230V50/60Hz primary. Its typical regulation is12%. Body envelope74mm diameter ×34mm, with an additional3mm stated for mounting hardware; mass0.4kg. [VPT30-1670](https://catalog.triadmagnetics.com/Asset/VPT30-1670.pdf):50VA, corresponding series current1.67A,83mm ×36mm plus3mm hardware,0.6kg. Both need lead exits, mounting bolt/chassis stack and tool space in addition to those nominal envelopes. Neither is inserted into the populated chassis model or approved for the stated line extremes.

The electrical surrogate derives16.8V open-circuit per half from15V×1.12, with a resistive equivalent of1.8V divided by the series current. This is **not measured winding DCR**, not an electromagnetic model, and does not turn typical regulation into guaranteed bounds. The comparison uses current generic diodes and0.15Ω capacitor ESR. Reservoirs1000/4700µF are compared at−20% capacitance only; plus tolerance, ripple/endurance, startup phase and exact parts remain open.

The existing ST L7812CV's output-voltage guarantee uses14.5–25V input at5mA–1A over its stated temperature range; its separate higher-input test row has different conditions. See [ST L78 table15](https://www.st.com/resource/en/datasheet/l78.pdf). A plausible exact replacement is **TI LM340T-12/NOPB**, whose12V output range11.4–12.6V covers14.5–27V input at5mA–1A and0–125°C, subject to power limits. [TI LM340 section6.7](https://www.ti.com/lit/ds/symlink/lm340.pdf). Its current screen uses10mA including listed quiescent variations. The unchanged ST15V stage limits its input to28V under the corresponding voltage-guarantee row, so the proposed shared positive-rail screen becomes27V. This is a genuine component-specific comparison, not a relaxed limit for the existing ST part. Pin/package/socket/bypass/thermal checks must precede any replacement.

## Results

Seventy-two cases cover two transformers, both selector modes, low/nominal/high mains, two reservoir sizes and three load profiles. Eight limiting cases are repeated at half timestep. Raw-node KCL, deck/input hashes, full matrix membership, actual primary ratio, candidate winding-current limit and numerical refinement pass. Four negative controls reject nominal-factor reuse, the old0.25A limit, a missing case and interpreting a clean screen as a selected part.

| Transformer | Nominal reservoir per rail | Flagged/18 | Lowest positive raw | Lowest negative magnitude | Highest positive raw |
|---|---:|---:|---:|---:|---:|
|25VA VPT30-830|1000µF|2|16.184V|17.588V|25.496V|
|25VA VPT30-830|4700µF|1|17.023V|18.029V|25.318V|
|50VA VPT30-1670|1000µF|2|16.830V|18.026V|25.910V|
|50VA VPT30-1670|4700µF|0|17.803V|18.521V|25.744V|

The larger option clears this typical-value screen only with the proposed TI U4; the native ST U4 still exceeds its documented input range in two of those18 cases. Even with TI, the negative-rail low-line margin is just **21.2mV** above18.5V. That is insufficient evidence for selection with unbounded winding tolerances, diode temperature effects and actual loads. More capacitance also changes charging pulses, physical size and fault energy. Do not spend more on a50VA unit simply because its nominal test has zero flags. Maximum model winding RMS is0.3846A and conditional regulator heat4.288W for that option; neither proves real thermal performance.

## Procurement evidence and action

The [domestic LCSC page for LM340T-12/NOPB](https://item.szlcsc.com/150727.html) identifies TI, TO-220 andC139404, but the returned page contains no usable current stock/price quantity; catalog identity alone is not purchase readiness. The exact [DigiKey China transformer URL](https://www.digikey.cn/zh/products/detail/triad-magnetics/VPT30-830/2090064) returned403 through the research tool, and the Mouser China page could not be fetched. Those failures do not prove unavailability. The global distributor listing is a lead, not a confirmed domestic delivery offer.

The prepared inquiry asks Mable for stock/custom output, main and auxiliary transformer options, actual winding data, mounting drawings, Chinese order links and a one-set RMB quote to Shanghai. The [manufacturer's contact page](https://www.mableaudio.com/en/contact.asp) publishes mable@mableaudio.com and its Taobao shop. The draft contains no personal address, payment details or project CAD and explicitly authorizes no purchase or manufacture. It has **not been sent**. Existing models and all native parts remain unchanged while exact information is obtained; independent connector/current/socket work can continue.
