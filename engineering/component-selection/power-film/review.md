# Four power capacitors: sourcing and insertion review

24 November 2026. Scope: P057, C12/C13/C25/C26. No native part, hole, track, circuit or placement changed. Both options remain candidates.

## Available alternative

[RS China 204-8479](https://www.rsonline.cn/web/p/film-capacitors/2048479) returned the exact **Panasonic EZPV60506MTC**, one-piece sale, 116 displayed available from other locations, RMB91.90 excluding tax / RMB103.85 including tax at quantities 1–37. Four cost RMB415.40 including tax. Public [RS delivery policy](https://www.rsonline.cn/web/content/support/all-articles/delivery) covers individual customers, free delivery above RMB198 and Shanghai collection. This supports a Chinese purchasing route; it does not establish local stock, an exact Shanghai address acceptance, a promised date or an order. Retained page-text receipts and raw-response hashes distinguish this observation from a search snippet. The web-search tool could not retrieve RS; Python urllib successfully fetched HTTP200 public pages. No login or basket was used.

This is a higher-cost fallback to the historically quoted CRC FC6136. That CRC quote remains dated November11; its current public [LCSC page](https://item.szlcsc.com/49276969.html) establishes identity but did not expose stock/price in the retrieved content. Do not refresh the old numbers to today's date. Panasonic is **not selected simply because the draft already uses its name**.

## Manufacturer geometry and native result

[Panasonic specification R9](https://industrial.panasonic.com/content/data/CP/PDF/ezpv_je.pdf), pages2–3, was downloaded and its drawing visually reviewed. Exact suffix C uses the 52.5 ×10.2 mm four-lead grid; body57 ×25 ×40 mm, each ±1; both pitches ±1; round lead1.2 ±0.2; exposed length4 ±2 mm. These are not the CRC dimensions. The supplier's generic automotive claim is not adopted: Panasonic's exact product page identifies this suffix as general-purpose.

The native grid matches nominal Panasonic pitch on all four footprints. However, an allowed rigid rectangle53.5 ×11.2 mm with1.4 mm leads cannot enter nominal1.8 mm holes: its opposite-lead distance exceeds the board's maximum hole-centre distance plus available diametral play. Translation or rotation cannot cure that witness. This proves the nominal check alone is insufficient, not that every purchased part fails. A centered rectangular-grid calculation yields2.814214 mm holes **before** PCB tolerance or insertion allowance; this is an explanatory geometry result, not a recommendation to enlarge holes. Solder fill, positional tolerance, pad copper, seating and permitted lead forming need their own assembly specification. Do not force short leads.

Centered maximum Panasonic bodies have four9.05 mm neighbor gaps and no mutual overlap; R9 recommends10 mm spacing to neighboring components. CRC maximum bodies still collide in two pairs. These are four-capacitor projections only: body-to-pin offset, nearby components, support, wiring and chassis are excluded. Panasonic's minimum exposed lead length also needs checking against board thickness and actual seating/support.

## Electrical and implementation boundary

The alternative preserves50 uF ±10% and the600 V baseline. Its19.1 A rating is specified at70°C/10 kHz with self-heating limits; it is not a blanket mains-ripple rating. The600 V part requires temperature-dependent voltage derating above85°C and peak/ripple checks against the eventual transformer. Reuse of the name in CAD does not close these checks. Active source symbols are polarized placeholders; an adopted film choice must be represented consistently in readable schematics as well as PCB/BOM.

CRC's exact approval still omits maximum lead diameter and explicit terminal grouping. A different CRC FC5064 document found in this search has a diameter tolerance, but that number was deliberately not transferred to FC6136. No unresolved dimension is filled with a guess.

Next: resolve an insertion/terminal/support specification for the selected candidate, then repack the four filters with the rest of the power block and check its hot components. Preserve node ownership and the three-board architecture. Current board-hole geometry is not released, and this sourcing fallback does not close populated chassis or drill access.

## Verification

`tools/check_packages.py` reads the current native Power board using KiCad Python. All four references are present with the expected library identity and grid; six independent control checks pass, including deliberately failing pitch, non-failing nominal and generous-hole examples, touching/overlapping boxes and native hash preservation. Results record input/script hashes. No DRC rerun is claimed: no native file changed. The scoped ICM audit is run after this module is saved.
