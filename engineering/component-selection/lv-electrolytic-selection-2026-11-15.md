# Low-voltage electrolytic selections — 2026-11-15

Owner: primary agent. Inputs: unchanged v0.5 circuit and November11 domestic supplier register. Select the three exact Panasonic FR-A parts below for six low-voltage decoupling positions. No capacitance changes. Engineering selection only; no procurement or native-layout release.

| MPN | References | uF / V | Body D × L mm | Pitch / lead mm | Ripple mA at100kHz105°C | Catalogue endurance hours |
|---|---|---|---|---|---|---|
| EEUFR1H470 | C616, C617, C207 | 47 /50 | 6.3 × 11.2 | 2.5 / 0.5 | 405 | 5000 |
| EEUFR1H101 | C204 | 100 /50 | 8 × 11.5 | 3.5 / 0.6 | 870 | 6000 |
| EEUFR1H100 | C211, C214 | 10 /50 | 5 × 11 | 2 / 0.5 | 250 | 5000 |

Primary sources checked November15:
- https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1H470
- https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1H100
- Exact50V rows in manufacturer FR-A catalogue: https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ast-ind-152838.pdf

Manufacturer parts are polarized, ±20%, -40..105°C. The10uF product page has an inconsistent endurance field of0; retain the specific catalogue row's5000-hour value and verify the full endurance test conditions before any service-life prediction. Listed ripple is100kHz, not50/100Hz. Nominal body sizes above are not maximum mechanical envelopes; footprint courtyard tolerances and vent clearance remain to check.

Circuit evidence: engineering/solid-state-reverb/tools/build_revision.py lines104/135 defines rails/polarity. C616 andC211 positive to+15V; C617 andC214 positive to ground, negative to-15V. C204 positive to+12V, C207 positive to+5V. Six arithmetic checks in lv-electrolytic-screen-2026-11-15.json give maximum18V/50V=36% under an assumed20% rail margin. This is not a measured or simulated startup bound. Check actual ripple, regulator stability with low-impedance capacitors, reversal on power-down, temperature and native pad mapping before release.

Domestic supply evidence remains dated November11, not refreshed stock: C40795047uF ¥1.1676 MOQ5 stock740; C178702100uF ¥1.4432 MOQ5 stock895; C17870110uF ¥1.3056 MOQ5 stock1490. Combined MOQ estimate¥19.582. Exact URLs are retained in candidate-register.json. These are economical standard industrial electrolytics; no unsupported audible-quality claim. Native boards unchanged.
