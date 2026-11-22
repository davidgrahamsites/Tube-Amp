# Reverb repair part qualification — 21 November 2026

Owner: delegated component evidence worker. Integration owner controls coverage, BOM, native CAD and release.

Task card: input is electric 600R-1, coverage P086/P087/P093/P098, the delivered tank's reported 76 ohm input DC resistance and seller's nominal 600 ohm AC impedance, and the earlier 19/21 November dossiers. Process is manufacturer-first rating/package review, public China supplier lookup and explicit stress calculations. Output is this dossier only. Dependencies are exact capacitor drawing, current domestic quotation, actual rail/temperature bounds and integration checks. Human check: compare purchased markings and dimensions with the exact drawing, confirm actual output/load/fault conditions, then review the resulting native board. Done-condition is an auditable recommendation with remaining holds; no claim of build readiness. Effort: bounded L1 investigation, approximately 30 minutes.

## Recommendations

| Reference | Exact recommendation | Qualification status |
|---|---|---|
| C603 | Retain **KNSCHA 224CL0045**, LCSC C47917108, as the existing source candidate | Catalogue meets 2.2 uF, 5%, 63 V film; exact drawing and thermal/pulse limits remain unavailable. Do not freeze package or promote to a fully qualified selection. |
| C605 | **Yageo CC1206JRNPO0BN331**, LCSC C527285 | Meets 330 pF, 5%, C0G/NP0, 100 V requirement. Suitable electrical/package recommendation; requires real 1206 SMD integration and domestic quotation refresh. |
| R605 | **Yageo FMP200FRF52-220R**, LCSC C3405818 | Meets 220 ohm, 1%, 2 W flameproof family requirement. Passes the stated <=16 V continuous resistor-voltage envelope at <=100 C. Current mainland stock/MOQ remains unverified. |
| R616 | **Yageo MF0207FTE52-100R**, LCSC C513679 | Meets 100 ohm, 1%, metal-film, >=0.25 W, >=250 V family rating. Conditional normal-service choice; sustained output-short/fault envelope remains unresolved. |

These are separate electrical, package and sourcing conclusions. A supplier's “similar part” label does not clear the original requirement.

## C603: exact drawing located but not retrieved

The [exact LCSC listing](https://www.lcsc.com/es/product-detail/C47917108.html?is_substitute=1&original_product_code=C89819&original_unit_price=3.0598) identifies **224CL0045**, C47917108, 2.2 uF, ±5%, 63 V, metallized polyester, pitch 5 mm, −55 to +105 C. Its datasheet link goes through a [viewer entry](https://www.lcsc.com/datasheet/C47917108.pdf). Following that entry exposed the actual manufacturer-document target:

- [Exact KNSCHA PDF target](https://datasheet.lcsc.com/datasheet/pdf/fe8ce22493d5a958fc45c0f9c3442d0d.pdf?productCode=C47917108)
- [LCSC PDF.js viewer carrying that target](https://static.lcsc.com/feassets/pc/html/pdfjs/web/viewer.html?file=https%3A%2F%2Fdatasheet.lcsc.com%2Fdatasheet%2Fpdf%2Ffe8ce22493d5a958fc45c0f9c3442d0d.pdf%3FproductCode%3DC47917108)

Direct PDF access failed with and without its query string. This investigation therefore has **not** read that document and cannot attest to its maximum body/height, lead diameter, voltage derating, ripple rating or permitted dV/dt. Do not infer 0.22 uF from the first characters of the proprietary MPN; the exact catalogue says 2.2 uF, which still needs drawing/received-marking corroboration. An unrelated KNSCHA CL23/104J63 sheet found in search was excluded.

The [domestic related-part page](https://item.szlcsc.com/6172087.html) indexed two weeks before this check repeats 224CL0045 stock 4,160 and RMB2.47 without a quantity tier. The exact domestic product [50153065](https://item.szlcsc.com/50153065.html) returned an anti-bot response. Retain the original **11 November** signed-in observation: RMB1.935, MOQ1, stock4,062. None is a refreshed 21 November mainland quote.

Manufacturer-documented fallback, if the exact KNSCHA drawing cannot be obtained: **WIMA MKS2C042201K00JSSD**, 2.2 uF/63 V/5%, bulk with 6−2 mm pins. The [WIMA MKS2 specification](https://www.wima.de/wp-content/uploads/media/e_WIMA_MKS_2.pdf), revision03.26 pp34–36, gives width7.2 × height13 × length7.2 mm, pitch5 mm, lead diameter0.5 mm; −55 to125 C with125 C limited to1000 cumulative hours. DC voltage derates1.25%/K above85 C: 63 V becomes51.19 V at100 C. For2.2 uF/63 V maximum pulse rise rate is7.5 V/us. Its40 VAC rating is specified only at<=50 Hz; frequency/ripple heating requires separate checking. Values are published drawing dimensions, not a separately established all-dimension maximum tolerance envelope.

This fallback does **not** close sourcing: [LCSC C19836445](https://www.lcsc.com/product-detail/C19836445.html) is the different **MKS2C042201K00JF00** suffix, out of stock, MOQ1, USD1.2565 reference only. Packaging suffixes must not be interchanged on a purchase line. No current China low-quantity stock route for JSSD was verified. The [manufacturer KEMET part sheet](https://search.kemet.com/component-documentation/download/specsheet/R82CC4220DQ70J) also shows the suggested R82CC4220DQ70J alternative is50 V and obsolete: reject it against63 V. Likewise WIMA MKS2B042201F00KSSD is50 V, not a compliant fallback.

## C605: electrical and package selection supported

[Yageo NP0/X7R mid-voltage specification V25](https://yageogroup.com/content/Resource%20Library/Datasheet/UPY-NP0X7R_MV_100-TO-630V.pdf), pp2–3,7,16: CC1206 is1206 size, J=±5%, NP0 dielectric, voltage code0=100 V,331=330 pF. NP0 has±30 ppm/C temperature coefficient and−55 to125 C operation. For this value/package, nominal thickness0.6±0.1 mm; [exact distributor entry](https://www.digikey.com/en/products/detail/yageo/CC1206JRNPO0BN331/5884450) corroborates3.20×1.60 mm body and0.70 mm maximum thickness. Review manufacturer land-pattern and soldering guidance during native implementation; board bending and solder thermal shock remain MLCC assembly concerns.

The [LCSC C527285 listing](https://www.lcsc.com/product-image/C527285.html?whichImg=pcb), indexed yesterday when checked, reports stock4,000, minimum/multiple10, USD0.0402 each at10. This is a global catalogue observation, not a mainland RMB or Shanghai-delivery confirmation. Existing50 V1206CG331J500NT remains rejected. The old through-hole pitch5 capacitor footprint is incompatible. In the100k recovery feedback path, nominal pole remains4.823 kHz; this is arithmetic, not a fresh simulation.

## R605: conditional stress qualification; China source lead added

[Yageo FMP V9,13 January2026](https://yageogroup.com/content/datasheet/asset/file/YAGEO-FMP_DATASHEET), pp2–4: FMP200=2 W at70 C; F=1%; R=reel; secondF=±100 ppm/C;52 denotes52.4 mm tape dimension, **not board pitch**. Body9.0±0.5 mm by diameter3.9±0.3 mm; lead0.55±0.05 mm. Maximum working voltage500 V is also power limited. Ambient range−55 to155 C; linear power derating above70 C to zero155 C. Coating is described as equivalent toUL94V-0, without claiming a fusible function. The5-second2.5×RCWV overload test is not permission for indefinite overload or arbitrary repetitive pulses.

For resistance217.8 ohm (1% low), at100 C permissible power is2×55/85=**1.2941 W**. A16 V continuous differential gives256/217.8=**1.1754 W**,90.82% utilization. At125 C allowance is0.7059 W: the same envelope fails. This retains the earlier conservative <=100 C condition with little margin near its ceiling. The selected operating point and local enclosure temperature must be materially established; temperature drift is separate from initial1% tolerance. No tank-current limit is inferred from these numbers.

The [exact LCSC C3405818 route](https://www.lcsc.com/product-detail/through-hole-resistors_yageo-fmp200frf52-220r_C3405818.html) did not fetch successfully; no new stock/MOQ claim. A useful China-facing alternate source was found: [Mouser.cn603-FMP200FRF52-220R](https://www.mouser.cn/ProductDetail/YAGEO/FMP200FRF52-220R?qs=EiYF7fRZytyh2xGsCnyIzQ%3D%3D) indexed stock2,749, quantity-one priceRMB1.8193 including13%VAT, ten-piece priceRMB1.1526. **Its crawl is four months old**, and direct fetch failed. Treat as a quotation-refresh lead, not verified current mainland stock or delivery. This adds a concrete low-quantity route without closing procurement.

Prepared15.24 mm formed-lead footprint is an integration proposal. Allow maximum9.5×4.2 mm body, verified0.60 mm maximum lead, thermal standoff and proper drill/courtyard. Do not use the previous generic6.3×2.5 mm outline.

## R616: normal rating passes; fault hold persists

[Yageo MF0 V4,13 January2026](https://yageogroup.com/content/datasheet/asset/file/YAGEO-MF0_DATASHEET), pp2–4: MF0207 is0.6 W at70 C,350 V maximum working voltage,−55 to155 C; F=1%, T=box pack, E=±50 ppm/C,52=tape dimension. Body6.3±0.5 by diameter2.4±0.2 mm; lead0.55±0.05 mm. Linear power derating reaches zero155 C. The5-second overload test is distinct from a continuous output short. This general-purpose metal-film family is not the requested R605 flameproof family.

At100 C allowance is0.6×55/85=**0.38824 W**. Conservative continuous current limit at101 ohm is sqrt(0.38824/101)=**62.0 mA**; at the requested0.25 W nominal design budget it is49.75 mA. Conversely16 V continuously across99 ohm gives**2.586 W**, so the part cannot survive an unrestricted full-rail short. The series350 V rating satisfies the catalogue voltage class; power limits the actual voltage across this100 ohm part to about6.2 V at100 C. Do not interpret “>=250 V” as250 V usable across100 ohm.

[LCSC C513679](https://www.lcsc.com/product-detail/C513679.html) indexed one month before this check reports29,500 stock, MOQ/multiple50, USD0.0209 at50. Another catalogue extract reported12,000; these are asynchronous cached observations, not a settled current stock count. Retain original11 November domestic signed-in priceRMB0.1271,MOQ50,stock11K+. [Mouser.cn exact part](https://www.mouser.cn/ProductDetail/YAGEO/MF0207FTE52-100R?qs=sGAEpiMZZMtlubZbdhIBIFoOGUvNp40aTMV5FT6wEv0%3D) indexed four months ago reports4,521 stock andMOQ/multiple1; itsRMB0.99214 unit figure has no clear quantity tier. It is an alternate quote lead only.

The delivered tank does not determine R616 output-load stress. Keep the existing fault hold until guaranteed current protection or a specified load/fault-duration envelope is established. Typical OPA2134 short-circuit current does not provide that guarantee. Prepared10.16 mm formed pitch needs native review and a maximum6.8×2.6 mm body/0.60 mm lead allowance.

## Tank boundary and integration handoff

76 ohm is reported input-coil **DC resistance**;600 ohm is seller's nominal **AC impedance**, with test frequency still assumed in the circuit model. Neither gives a permissible coil current. The current1 kHz surrogate impliesL=sqrt(600²−76²)/(2π1000)=94.72 mH. This is a calculated model parameter, not a measurement. Keep C6032.2 uF, C605330 pF and R605220 ohm unchanged while closing exact part selection; no tank redesign is implied.

Integration owner should link this evidence to P086/P087/P093/P098 without treating the rows as a blanket selection release. Carry C603 exact-drawing hold, C605 footprint change, R605 local-temperature/rail and procurement holds, and R616 guaranteed fault-envelope hold forward. Scope check: only this new evidence file was created; no native circuit, shared ledger, catalog, BOM, purchase or mail action occurred. Existing evidence folder contract remains the ownership seam. No code/UI/refactor/file move was performed; no native ERC/DRC was appropriate to this evidence-only task. Recalculated the numerical stress/inductance results with Python and checked dossier contract/part identities: PASS. Scoped structural command `python3 /Users/appleadmin/.codex/skills/icm-check/scripts/icm_check.py . engineering/component-selection/evidence` returned `ICM CHECK: clean`; this does not clear the stated electrical or sourcing holds.
