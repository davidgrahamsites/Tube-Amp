# Screen-resistor candidate research

R41/R42=4.7k emerged as a simulation-only candidate. Full-amplifier80ms reference predicts up to4.35W average per resistor;5W nominal does not provide appropriate hot-enclosure margin. Need >=10W nominal and actual manufacturer's derating/pulse review before selection.

- TE ROX5SSJ4K7 /LCSC C3466251: international indexed supplier listing says out of stock,MOQ1;5W is inadequate margin anyway. https://www.lcsc.com/product-detail/C3466251.html
- TE ROX5SSJ2K2 /C3567335: international indexed page says16 stock,MOQ1,$0.3475; not a mainland RMB quote.2.2k fails full-amplifier screen-rating comparison, so not selected. https://www.lcsc.com/es/product-detail/C3567335.html?is_substitute=1&original_product_code=C1397090&original_unit_price=0.1359
- Yageo SQP10AJB-4K7 /C1403087:10W,5%,48×9.5mm body listing. Candidate only; indexed page did not expose current stock, actual one-piece price or domestic delivery. https://www.lcsc.com/product-detail/through-hole-resistors_yageo-sqp10ajb-4k7_C1403087.html

Direct web opens of TE pages failed. Mainland LCSC background search redirected to login. No current stock/price confirmation, selected MPN, or PCB footprint change is claimed from these search results.

## Subsequent live mainland checks — November 12
Catalogue access resumed; the current page now shows a signed-in account. No further login is required.

- RESI **EWWR0010J4K70T9**, C349127: **14 stocked, MOQ1, ¥3.94 each**; two cost ¥7.88 before shipping. https://item.szlcsc.com/325584.html
- TE C104K7JL, C1369644: 15 stocked, MOQ1, ¥26.98 each. https://item.szlcsc.com/1459933.html
- Yageo SQP10AJB-4K7, C1403087: zero stock; preorder price ¥0.7074, MOQ1. https://item.szlcsc.com/1493379.html
- TE ROX5SSJ2K2, C3567335: 16 stocked, MOQ1, ¥2.18; value rejected by the full-amp stress comparison. https://item.szlcsc.com/4134044.html

RESI manufacturer specification C05005 V4 (2022-09-14), saved as RESI-EWWR.pdf and visually inspected: 10W at70°C; solid derating line reaches58.5% at155°C. Do not extrapolate the dashed extension beyond155°C or use the below70°C overload extension. At125°C interpolation permits7.315W. The candidate's4.350W simulated average is59.5% of that allowance, before high-line/tolerance/long-duration checks. This is a conditional candidate, not a final qualified circuit change.

Dimensions: body36.5±1 by9±1mm, axial leads27±2mm each, diameter0.75±0.05mm. The700V entry is **effective insulation voltage**, not a guaranteed continuous working-voltage rating. The10×rated-power/5s overload test is not a repetitive pulse rating. Thermal placement, working-voltage interpretation, pulse duty and real enclosure temperature remain open.

Public manufacturer PDF served by distributor:
https://atta.szlcsc.com/upload/public/pdf/source/20230201/1B3D2D7E42CE9D2055BF95E570A62506.pdf
