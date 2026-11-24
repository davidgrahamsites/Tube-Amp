# R215 minimum-load correction — 24 November 2026

Owner: auxiliary supply qualification. Electrical change under existing repair authority; not a fabrication release. This supersedes only the unadopted-preload portion of [the historical envelope review](envelope-review.md).

## Implemented electrical change

R215 is an 820 Ω, 1%, 0.25 W shunt from +5 V to GND. The source circuit, native sheet 08, native Control board, P129 coverage and an exact-family footprint now agree. Its two tracks terminate at U5's output and ground pads. Six new segments use 0.4 mm copper and horizontal/vertical/45° geometry; no existing footprint, track, net endpoint, sheet object or property was edited. All functional interfaces remain unchanged. This still lives on the transitional Control board; the final three-board allocation is not complete.

[ST L78 DS0422 rev38](https://www.st.com/resource/en/datasheet/l78.pdf), table 10, specifies the L7805C output-voltage range with at least 5 mA output load. The existing logic does not establish that minimum under every state. R215 provides it independently within the stated normal-output and resistor assumptions. This is not a cure for dropout, input-range excursions, reverse current or socket/bypass-loop stability.

## Selected engineering part and physical envelope

UNI-ROYAL **MFR0W4F8200A50**, supplier code **C58624**; manufacturer replacement numbering **MF0W4FF8200A50**, C27412564. The [manufacturer catalog](https://www.uni-royal.cn/images/upload/UniroyalCatalog2024.06.07.pdf), printed pp 72–73, explicitly maps old/new MF0W4 numbers. Those pages were visually inspected and retained in `results/preload/uniroyal-mf-excerpt.pdf`. The [supplier catalog](https://www.lcsc.com/pl/product-detail/C58624.html?is_substitute=1&original_product_code=C27412564&original_unit_price=0.0054) corroborates 820 Ω/1%/250mW/50ppm/°C. Supplier names alone do not qualify an alternative.

Maximum body 7.5 × 2.5 mm, round lead 0.59 mm. The custom footprint reserves the maximum body plus courtyard margin, a 12.70 mm formed pitch, 1.8 mm pads and 0.90 mm finished round PTH holes. With ±0.10 mm hole tolerance, minimum diametric clearance is 0.21 mm. Both actual exported R215 drill hits were found as 0.9 mm plated round holes. Finished-hole tolerance, hole registration, lead forming and received-part fit remain manufacturing/inspection gates. No slot is needed for this round-lead resistor; this does not qualify rectangular regulator/contact pins.

The catalog derates from 0.25W at 70°C to zero at 155°C. Initial 1% tolerance and 50 ppm/°C over the declared −40..125°C screen are included. A deliberately conservative engineering allowance also adds the separate catalog flame-retardant load-life 5%, humidity-life 5%, solder 1%+0.05Ω and temperature-cycle 1%+0.05Ω test limits. These separate test limits are **not** a lifetime guarantee or a claim of demonstrated cumulative exposure.

That declared arithmetic envelope gives 709.2–930.8 Ω: at least **5.103 mA** at 4.75 V, at most 7.403 mA at 5.25 V, and 38.87 mW maximum dissipation. At 125°C the derated rating is 88.24 mW, more than twice this power. A 1 kΩ alternative and a 0.7 mm finished hole fail deliberate negative controls. The editable inputs are [preload-contract.json](preload-contract.json).

## Simulation and native checks

The same raw-supply fixture was rerun for 72 cases with the maximum bounded preload current, plus 2 distinct limiting cases at half timestep. All finish at 0.6 s and pass positive/negative raw-node KCL. This uses generic rectifier and assumed winding/load behavior; it is **not a regulator macro-model or startup/stability simulation**. Existing baseline evidence remains immutable; its original generator now refuses a source containing R215, avoiding accidental reuse without the added load.

| Load scenario | Maximum winding RMS | Maximum conditional four-regulator heat | Tightest common-sink budget at 60°C |
|---|---:|---:|---:|
| Idle |0.1151A|2.081W|17.23°C/W|
| Working reserve |0.2010A|3.175W|10.25°C/W|
| Expansion stress |0.2851 A|4.167 W|7.70°C/W|

The 5 mA minimum-load flag clears.41 of 72 cases still carry other flags:21 positive-above-range,1 positive-below-range,4 negative-above-range,20 above the provisional0.25 A winding rating; counts overlap. Do not select the transformer or heatsink from a nominal-voltage pass. Actual winding/thermal evidence and final effects-loop load remain necessary.

Native export proves exactly two new endpoints: R215.1→+5 V and R215.2→GND. All prior exported components and named-net endpoints remain identical. Full sheet-tree checks preserve prior symbol positions/metadata and wiring. Every previous board footprint and board object remains identical. ERC remains the single existing GND/PE alias warning. Control DRC remains 13 missing-wire-courtyard violations and 90 unconnected items; no new violation. Whole-project 234 unconnected / 68 provisional courtyards are not resolved by this local repair.

The native schematic PDF and native PCB copper/fabrication render were inspected. R215 is visibly connected beside U5, its labels are clear, the board body/holes do not overlap neighboring parts, and the six new tracks are legible. Existing sheet 08 U7/ground text crowding and distant bypass groups remain a separate readability/layout hold. Full-board readability, regulator sockets and heatsink volume are not accepted by this scoped review.

## Startup and procurement holds

The [earlier U3 review](../../component-selection/evidence/electric-lv-parts-2026-11-21.md) already identified the supervisor problem; this pass rechecked the [current TI TPS3808 revN](https://www.ti.com/lit/ds/symlink/tps3808.pdf), tables 6.5/6.6 and section 7.3. A maximum G50 rising threshold of 4.65×1.02×1.025=**4.8616 V** exceeds the 4.75 V rail minimum. Even the below 85°C threshold tolerance gives 4.8377 V. R215 cannot remove this hold. Native U3 is unchanged. Reuse the existing adjustable-supervisor candidate and verify the HC74→MOSFET→relay chain over brownout before adopting it; include its socketed adapter and exact divider parts. The static bounds fail; subsequent startup simulations must evaluate a compatible implementation.

On 24 November the domestic LCSC search for C58624 redirected to the JLC login page. No account or checkout action was taken. Global catalog presence is identity evidence only: domestic stock, RMB price, MOQ and exact Shanghai delivery remain **unverified**. The previously read domestic mainland-shipping policy is only a general route. Neither this part nor the full BOM is declared purchase-ready.

Next: resolve the reset/relay chain with exact socket-compatible implementation; select auxiliary magnetics and regulator contact/heatsink assembly; then move local bypasses and check split-rail startup/protection. Keep all 10 ICs / 6 tubes socket-required. Continue the transformer/RETURN and populated three-board fit tasks. Rear-panel independence is unchanged; actual drill envelope remains pendingNovember 25.
