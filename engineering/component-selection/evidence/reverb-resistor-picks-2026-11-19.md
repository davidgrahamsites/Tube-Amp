# Reverb resistor picks — 19 November 2026

Owner: delegated resistor evidence worker. One job: choose exact resistor candidates for R605/R616 and the proposed passive dry/attenuated-send revision. Inputs: current candidate register, Yageo manufacturer PDFs already saved here, TI OPA2134 datasheet, and `../../whole-amp/tools/check_reverb_headroom.py`. Output: this evidence dossier only. Parent owns register/brain integration. Human check: confirm actual circuit revision, rail limits, transformer/tank data, temperatures and purchased dimensions before assembly. No native CAD, canonical register, purchase, messaging or UI changes.

## Recommended exact choices

| Position/function | Choice | Status |
|---|---|---|
| R605,220ohm series tank driver | Yageo FMP200FRF52-220R,1%,2W,flameproof metal film; LCSC C3405818 | Electrical candidate passes the stated15V continuous stress envelope at100C; domestic stock/RMB price/MOQ not established, so not procurement selected. |
| R608/R611/R613/R614/R615,100k feedback/mixer | Yageo MFR50SFTE52-100K,1%,0.5W; C173137 | Existing mainland-stock-backed exact choice can cover these positions, conditional on<=32V continuous differential and<=100C local ambient. |
| Revised R602 and new RDRY,100k | Same MFR50SFTE52-100K | Proposed-circuit choice only; R602 changes from10M and RDRY replaces the old R612 path. Do not assign the old P079 group wholesale. |
| Revised R601 plus RWET,R609,R617,1M | Yageo MF0207FTE52-1M,1%,0.6W; C1373811 | Existing mainland-stock-backed exact choice. R601 changes100k to1M; RWET is new. Treat these as proposed-revision mapping, not a claim that native CAD already changed. |
| R616,100ohm output isolation | Keep MF0207FTE52-100R only as unresolved candidate; no new release | Typical opamp current limiting alone cannot clear an unlimited short/fault envelope. See below. |

## Manufacturer evidence and package

`Yageo-FMP.pdf` here, January13 2026 V9, gives FMP2002W at70C, linear derating to zero155C,500V maximum working voltage further limited by power. FMP200 body9.0±0.5 ×3.9±0.3mm; lead0.55±0.05mm. Flameproof coating is described as equivalent to UL94V-0; this is not a blanket product safety certification or fusible-resistor function. Proposed formed pitch15.24mm reuses existing prepared FMP200 footprint geometry; installation and courtyard still need native review.

`Yageo-MFR.pdf` and `Yageo-MF0.pdf` support MFR50S0.5W/300V and MF0207 0.6W/350V, both70C ratings derated to zero155C. Both body6.3±0.5 ×2.4±0.2mm; lead0.55±0.05mm. Existing prepared10.16mm formed-pitch footprint applies. These are manufacturer documents already inspected, not deductions from supplier titles.

Public manufacturer document access:
- Yageo FMP manufacturer sheet mirrored by LCSC: https://datasheet.lcsc.com/datasheet/pdf/80402315d1a9cd9759eecba81cac5cfa.pdf?productCode=C1384046
- TI OPA2134: https://www.ti.com/lit/ds/symlink/opa2134.pdf (saved locally as TI-OPA2134.pdf/.txt).

## Scoped calculations

At100C: FMP200 allowable2×(155−100)/(155−70)=1.2941W. R605 worst1% low resistance217.8ohm and15V across it gives225/217.8=1.0331W,79.83% of that allowance. At16V it is1.1754W,90.82%; at125C allowance0.7059W and it fails either full-rail envelope. Require local ambient<=100C, preferably substantially cooler, and recheck actual regulated-rail extremes. A5% substitute would have slightly larger stress and must be separately documented.

This is a conservative resistor stress envelope. It does NOT say the tank is driven at68mA or that the opamp can continuously deliver15V into220ohm. TI OPA2134 section6.2.5 gives approximate25C source/sink current limits36mA/−30mA, decreasing with temperature. Those are typical behavior, not a guaranteed maximum bound for all parts/faults. Illustrative36mA through220ohm is0.285W; real tank current is frequency-dependent and includes the series coupling capacitor and tank impedance. Do not rate the tank from this resistor calculation.

At32V across100k at1% low resistance, P=0.010343W. At100C MFR50S allowance0.323529W; utilization3.20%. At32V across1M at1% low resistance, P=0.001034W; MF0207 allowance0.388235W; utilization0.267%. Even50V across revised1M send resistor gives0.002525W. These calculations do not clear a failed HV coupling capacitor or arbitrary external effects-return source. HV fault isolation and safe layout are separate tasks.

R616 at15V continuously across99ohm would dissipate2.2727W. A2W resistor fails even at70C; a3W FMP at100C only allows1.9412W and also fails. A5%3W candidate would require local ambient below87.9C for the15V/95ohm bound. Thus simply upsizing the current0.6W part to2W or3W does not establish the desired fault envelope at100C. Either qualify a guaranteed current-limited system and allowed external conditions, or select a larger suitable resistor with actual stock and thermal evidence. No silent circuit change made.

## Supplier evidence checked November19

- R605 exact supplier identity: https://www.lcsc.com/product-detail/through-hole-resistors_yageo-fmp200frf52-220r_C3405818.html — catalogue confirms220ohm1%2W9×3.9mm. Direct fetch returned cache miss; search extracts and related-product pages list0 availability and reference USD0.0192. This is NOT a live mainland RMB quote/MOQ. No domestic stock claim.
- https://www.lcsc.com/de/product-detail/C3418893.html lists that same exact C3405818 alternative with0 availability. Other suffixes are not silently substituted.
- https://www.lcsc.com/product-detail/C1389546.html identifies FMP300JT-73-100R,3W5%; fetched page says Out of Stock,MOQ1,reference USD0.0517. Excluded as a ready-stock solution and insufficient for100C15V bound.
- MFR2WSFTE73-220R C173080: indexed LCSC listing says out of stock,MOQ10,USD0.0653 reference. It is a different family and does not close the requested flameproof FMP sourcing.
- 100k domestic page: https://item.szlcsc.com/184526.html fetched; exact identity confirmed but no current price/stock in extract. Retain dated November11 record: C173137 MOQ20,RMB0.1432,2820 stock. Do not relabel it November19.
- 1M domestic indexed alternative on https://item.szlcsc.com/184370.html shows MF0207FTE52-1M stock20450 andRMB0.0776, but tier is unspecified and crawl is aboutone month old. This is corroborating catalogue evidence, not a purchase price. Retain original signed-in November11 C1373811 MOQ50,RMB0.1217,19K+ stock until refreshed.

## Integration handoff

Split legacy P079 before applying revised values. Unchanged100k references are R608,R611,R613,R614,R615. New RDRY needs a permanent native reference; RWET likewise. Revised R6011M and R602100k need explicit schematic change tracking and updated coverage. R609/R617 remain1M, though R617 moves to WET_AC in proposed mix. No selected-count increase should be claimed until canonical integration owner resolves that mapping.

ICM boundary: this dossier is evidence, not a stable factory or executable module. No new code or file moves. Existing component-selection folder lacks CONTEXT.md; parent should supply its contract as the sole owner rather than this worker changing shared architecture. Checked source-to-dossier walk: task inputs, calculations, output and human check are explicit; no duplicate canonical selection register created.
