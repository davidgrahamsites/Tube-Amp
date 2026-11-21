# Electric amplifier controls — 21 November 2026

Owner: delegated control-parts researcher. Scope: ten faceplate pots and matching black pointer knobs for `electric-guitar-amp`. Inputs: BUILD_VARIANT.md, coverage.json, previous knobs-and-controls.md and current manufacturer/supplier sources. Output: this dossier only. Parent owns canonical choices, panel CAD and BOM. No purchases or supplier messages. Human check: compare purchased shaft/bushing/knob stack and shaft rotation against a paper panel before drilling. Received yellow cabinet remains the fit constraint.

## Coherent exact pot family — recommend for engineering selection

Use Taiwan Alpha RV24AF-10 solder-lug, single-gang pots, with the same 15R1 smooth6.35mm shaft throughout. These are proven listed suffixes, not invented order codes. They permit panel mounting and a serviceable wire harness without making the PCB carry knob loads.

| Reference | Quantity | Requirement | Full exact MPN |
|---|---:|---|---|
| RV1,RV5 | 2 |250kohm linear treble | RV24AF-10-15R1-B250K-3LA |
| RV2,RV6,RV3,RV4,RV8 | 5 |1Mohm audio: bass, volume, gain, master | RV24AF-10-15R1-A1M-3LA |
| RV7,RV9 | 2 |25kohm linear mid/presence | RV24AF-10-15R1-B25K-3LA |
| RV602 | 1 |100kohm audio reverb | RV24AF-10-15R1-A100K-3LA |

RV10 bias and RV601 send remain the already selected Bourns internal trimmers. Expression pedal is separate. Do not order ten of each pot value.

**Status:** engineering recommendation; domestic-dispatch supplier and delivered RMB quote still required. This does not establish current mainland inventory. The values are unchanged. RV60224mm body is a deliberate mechanical-family proposal replacing its earlier16mm candidate; check space before canonical adoption.

### Price and low-quantity evidence

Mouser product/catalogue results checked November21 list all four variants at MOQ1/multiple1. USD reference prices: B250K1.94; B25K1.94; A100K1.94; A1M2.27. Ten fitted pots totalUSD21.05 before shipping/tax. Indexed quantities differ with crawl date; no live checkout was performed. This proves a practical low-quantity sourcing fallback, **not domestic Chinese dispatch**. China country-of-origin is not warehouse location.

Sources:
- B250K: https://www.mouser.com/en/c/passive-components/resistors/variable-resistors/?resistance=250+kOhms&termination+style=Solder+Lug
- B25K exact product: https://www.mouser.com/en/ProductDetail/Alpha-Taiwan/RV24AF-10-15R1-B25K-3LA?qs=8%252Br4Hz5Xir%2FYzcd3lltzPA%3D%3D
- A100K exact product: https://www.mouser.com/en/ProductDetail/Alpha-Taiwan/RV24AF-10-15R1-A100K-3LA?qs=8%252Br4Hz5Xir%2FnhQ6fMCb03g%3D%3D
- A1M: https://www.mouser.com/en/c/passive-components/potentiometers-trimmers-rheostats/potentiometers/?mounting+style=Panel+Mount&number+of+gangs=1+Gang&resistance=1+MOhms&termination+style=Solder+Lug

## Manufacturer geometry and electrical limits

[Alpha primary drawing](https://www.taiwanalpha.com/downloads?id=104&target=products), pages2/4 visually inspected from downloaded PDF. RV24AF-10:24mm body,11.5mm body depth, three solder lugs; centre wiper is terminal2. Terminal1/3 are ends. Drawing shows1-left/2-centre/3-right in its face view with full-CCW shaft; verify incoming resistance sweep before harness termination. R1 is6.35mm round; R is6mm round; F is6mm D-flat. 15R1 means L=15mm from mounting datum, **not15mm free beyond the bushing**. Standard bushing M8×0.75,6.5mm long; D2 is different. Rotation300±5degrees;15,000cycles; maximum operating250VAC;500VAC/one minute is dielectric test only. Lug edge reaches18.8mm from shaft centre. Do not reuse PCB-type22/30/40 hole patterns for type10.

[Alpha exact-family appendix](https://www.mouser.com/datasheet/2/13/V24AF-1522303.pdf) includes the listed suffixes. [Manufacturer customer sheet for A1M-3](https://cdnimages.opentip.com/Docs/CED/r-va1ma_specification_sheet.pdf) states0.25W at0–50C,250V working,±30% resistance, midpoint10–25% and−10..70C usable. Distributor tables state±20%; retain this conflict until exact supplied suffix acceptance data. Do not claim250VAC as a proven250VDC service rating. Check circuit DC, partial-track power and coupling-fault conditions separately.

## Knob choice and matching

Retain Mable **MAKP0437S black/white pointer, explicitly6.4mm bore** for the6.35mmR1 shafts. Supplier drawing already saved as `knob-MAKP0437S-dimensions.jpg`, visually reviewed again:25.95mm base diameter,25mm top width,16.50mm height; illustrated rear radius12.97mm. It offers6mm/6.4mm holes but also sketchesR3.05, so it does not establish a tolerance for the requested6.4mm variant. Require supplied-variant confirmation. Catalogue priceUSD1.65 each at10; stock/RMB price unconfirmed.

Sources: https://www.mableaudio.com/en/productview.asp?sid=10588 and https://www.mableaudio.com/uploadFile/Picture_small/202206231513104017.jpg

Genuine Sato **K-2195-S** is the fallback for a **6mm shaft**, not a6.35mmR1. Sato specifies phenolic black body and twoM3.5 set screws,0.5Nm torque,1.5mm hex key. Do not apply that screw specification to an unconfirmed Mable reproduction. Source: https://www.satoparts.co.jp/ENG/products/search/K/K-2195 and its dimension tab. A coherent6mm alternative is the listed15F-LA family (B250K/B25K/A1M/A100K); the D-flat shaft can take an appropriate setscrew knob, but changes the interface and pointer indexing. Prefer one shaft standard, not a mixed purchase.

## Paper-panel envelope and cutout guidance

Use **26mm knob swept circles** for the present paper study, subject to incoming physical check. At32mm centres, ten in one row need314mm including end radii, before end margins. The documented312mm cabinet opening is not enough to assume that layout. Two rows of five at32mm pitch occupy154mm width of knob sweeps; vertical pitch32mm gives58mm combined sweep height. These are calculated study envelopes, not a chosen panel or a fit claim. Labels, fingers, jacks, switch boots, lug harness and chassis structure add space.

For the standardM8 bushing, an **8.2mm finished hole is a proposed manufacturing clearance**, not an Alpha-specified cutout. Confirm actual bushing diameter/tolerance before release. Preserve the antirotation tab: its drawing shows1.2×2.8mm tab and11.6mm location dimension; do not convert that to a drilling coordinate without datum/orientation review and exact sample. The solder-lug fan extends beyond the circular24mm body; allow its18.8mm reach and wire bend/insulation clearance. No PCB footprint is needed for the pot itself if wired off-board; connector/harness pin numbering still requires verification.

Panel stack must satisfy: panel+faceplate+washers+nut engagement <=6.5mm threaded length, with assembly margin. Available shaft above front panel is15mm minus thickness between the mounting datum and panel front. **Blind bore depth, setscrew height and internal nut recess are missing from the Mable drawing.** Therefore neither knob seating height nor maximum panel thickness is verified. Do not assume the16.5mm-high knob can accept the entire shaft. Resolve using a sample or supplied section drawing; no fabricated stack dimensions introduced.

## China sourcing next step — draft only, not sent

New useful Mable lead: **MAPT0371 ten-piece R24B250K pack,USD6.80** appears in its indexed current catalogue: https://www.mableaudio.com/en/products.asp and https://mableaudio.com/en/spe_pro.asp?act=new . Maker, shaft and exact count-price convention need confirmation. It is not automatically the Alpha part above. Alibaba listings for “Alpha24 B25K/B250K/A1M” likewise lack complete MPNs and credible matching drawings, so they do not close selection.

Prepared query for Mable: “Please quote2×RV24AF-10-15R1-B250K-3LA,5×RV24AF-10-15R1-A1M-3LA,2×RV24AF-10-15R1-B25K-3LA,1×RV24AF-10-15R1-A100K-3LA, and10×MAKP0437S with6.4mm bore. We need genuine Alpha or separately identified substitutes, all smooth6.35mm shafts. Please confirm mainland stock, loose quantities, RMB/WeChat/Alipay and Shanghai shipping. Send exact pot drawing, resistance tolerance/taper, supplied nut/washer thickness, and knob bore depth/setscrew height. Is MAPT0371 this exactB250K part? Do not substitute20k for25k or change audio/linear taper.”

## Scope check

No structural/code changes: evidence stays in its owned folder; shared register/CAD unchanged. All ten electrical roles have exact-family candidates. Local China availability, full supplied shaft/knob stack, exact taper/tolerance acceptance and actual panel fit remain open. Parent should record this as engineering selection with these explicit procurement/fit dependencies, not as another generic-family shortlist.
