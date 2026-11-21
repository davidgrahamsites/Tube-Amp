# Electric amplifier resistor evidence — 21 November 2026

Owner: delegated resistor worker. Scope: proposed exact replacements and scoped stress screen only. No shared BOM, coverage, circuit or footprint was changed. Sources accessed 21 November; indexed inventory is not a reserved stock or mainland RMB quote.

## Recommended exact parts

| Circuit | Exact Yageo part | Source and purchase evidence | Disposition |
|---|---|---|---|
| R303/R313, 15k control timing | MF0207FTE52-15K | LCSC C1374127; [LCSC alternative table](https://www.lcsc.com/de/product-detail/C1746241.html) shows 750 pcs, quantity50, USD0.018; another indexed page shows500. | Engineering pick, 0.6W1%, domestic quote pending. |
| R6,15k clean tone | MF0207FTE52-15K | Same part. [Manufacturer MF0 sheet](https://www.mouser.com/datasheet/2/447/YAGEO_MF0_datasheet_2024v3-3461483.pdf). | Proposed exact part; signal stress not yet bounded. Keep separate from control qualification. |
| R20,820Ω cathode | MFR50SFTE52-820R | [LCSC C1374618](https://www.lcsc.com/product-detail/C1374618.html), exact0.5W1% catalogue; stock/MOQ not exposed. | Candidate only: below previous1W requirement. Do not silently substitute. |
| R26,470Ω cathode | MF0207FTE52-470R | [LCSC C1374787](https://www.lcsc.com/es/product-detail/C1374787.html?lcsc_vid=FQJdX1YCRAJaUFRVRwBZAQFWTlENVVZTRAcPXlwAEVExVlNRT1JZVlZWR1ddVjtW), indexed8250pcs,MOQ50,USD0.018 each. | Candidate only:0.6W below previous1W. |
| R503,33k bias stop | FMP100JR-52-33K | [LCSC C1741915](https://www.lcsc.com/product-detail/C1741915.html), [stock/price](https://www.lcsc.com/product-image/C1741915.html?whichImg=0):8700pcs,20+USD0.0379. | Engineering pick:1W5%, consistent with existing bias screen using5% fixed resistors. |
| R23,33k dirty tone slope | FMP100JR-52-33K | Same part. | Prefer flameproof1W over smaller0.5W candidate, but signal and tolerance review still open. Do not group its qualification with R503. |
| R39,4.7k bias filter | FMP100JT-52-4K7 | C1378593; [domestic listing](https://item.szlcsc.com/1468882.html). Existing11Nov observation MOQ10,RMB0.2558,4290pcs; not refreshed. | Engineering pick1W5%; new transient screen below. |
| R40,1k bias rectifier series | FMP100JT-52-1K | [LCSC C1378757](https://www.lcsc.com/product-detail/C1378757.html), exact1W5% catalogue. DomesticMOQ/stock unavailable in retrieved page. | Candidate: repetitive/startup pulse rating still requires closure. |

Alternative R26 FMP100JT-52-470R/C1378607 preserves1W but changes tolerance to5%. [LCSC](https://www.lcsc.com/product-detail/C1378607.html) currently indexed OUT OF STOCK,MOQ20,referenceUSD0.0306. Do not count as available. FMP100JT-52-820R is real but [DigiKey](https://www.digikey.com/en/products/detail/yageo/FMP100JT-52-820R/9107519) lists factory order105000; not a sensible one-amplifier purchase. The unsupported Tyohm RN1WS family remains unqualified; its mismatched PDF cannot support selection.

## Manufacturer ratings and mechanical match

Existing manufacturer evidence `Yageo-MF0.pdf`, `Yageo-MFR.pdf`, and `Yageo-FMP.pdf` controls dimensions, not generic reseller images. FMP sheet13Jan2026V9 is also [available here](https://datasheet.lcsc.com/datasheet/pdf/80402315d1a9cd9759eecba81cac5cfa.pdf?productCode=C1384046).

MF0207:0.6W at70°C,350V maximum. MFR50S:0.5W at70°C,300V maximum. FMP100:1W at70°C,350V maximum. All linearly derate to zero at155°C. At100°C allow0.38824W,0.32353W and0.64706W respectively. Rated voltage is also limited by sqrt(P×R); a350V label does not allow350V across a1k resistor continuously.

These three sizes share manufacturer axial body6.3±0.5mm long,2.4±0.2mm diameter,0.55±0.05mm leads. Existing `Renegade_Selected:Yageo_MFR50S_MF0207_P10.16` has the corresponding envelope and can supply the geometry basis for an explicitly named FMP100 footprint after review.10.16mm pitch is the assembly forming choice, not a factory promise. Match lead bend radius, body clearance and actual incoming parts. Low-noise metal film is appropriate for audio; no listening claim is made. FMP flameproof coating is not a fusible-resistor rating.

## Electrical screen and limits

R303/R313 control bound5.5V across14.85k gives2.037mW, well below388mW at100°C. This does not cover higher-voltage miswiring or externally injected faults.

Original saved400V stiff-B+ nominal tube OP shows R20=1.122874V/1.538mW and R26=0.944220V/1.897mW. These show nominal margin only. They do not justify reducing the original1W requirement before high-line, signal and tube-fault review. At100°C the proposed0.5W820Ω part permits16.21Vrms and0.6W470Ω permits13.44Vrms at1%lowR. R6 nominal zero DC says nothing about tone-stack signal dissipation. R23 is directly fed from cathode follower DR_CF through33k to DR_TONE: do not infer zero working voltage from its near-zero nominal DC drop. The1W5%33k choice permits142.43Vrms across31.35k at100°C; determine actual transient signal differential before release.

For R503, deliberately assume the entire78V bias bound across its minimum31.35k:0.19407W, below0.64706W at100°C. This conservative screen also avoids relying on the series22k/pot divider.78V remains a scoped assumed supply bound from the saved bias investigation, not measured hardware.

### New16-case bias transient screen

Reused all16 existing `bias-cap-screen/*.cir` decks without editing them. Loaded the existing project ngspice runtime and ran `tran 50u 2 0 50u`. Computed instantaneous resistor power from node differential squared divided by resistance, trapezoidal mean over1.9–2.0s, maximum over0–2s and integrated energy over first100ms. Inputs:198/235.4VAC mains;50VAC nominal bias source;1/1.12 secondary regulation multiplier;1Ω/50k pot;0/65µA leakage;8µF each capacitor. Fixed resistors nominal. Source begins at zero phase.

| Part | Maximum settled average | Maximum instantaneous | Maximum first100ms energy |
|---|---:|---:|---:|
| R39,4.7k |0.007698762W|0.247042201W|0.008805156J|
| R40,1k |0.012501422W|3.741564165W|0.031644299J|

R39 maximum instantaneous is already below100°C continuous allowance0.64706W in this screen; support its engineering pick. R40 settled power is small, but its startup peak exceeds1W. Require the manufacturer pulse graph, duration, repetition and hot derating check before selection. Average power alone does not close this item. These runs do not include worst switch-on phase, resistance tolerance,12µF maximum capacitors, hot leakage, real transformer impedance/regulation, repeated fast cycling or fault conditions. No claim of hardware validation or full bias release.

## Human check before release

Confirm domestic RMB price, MOQ and stock for each exact suffix. Preserve1W requirements until a documented circuit-level change is accepted. Check incoming dimensions and resistor location temperature; complete tube-stage signal/fault stress and R40 pulse checks. Parent owns canonical selection/register and brain updates. This dossier makes no fabrication release.

## Reproducible run supplement

Factory, contracts, complete per-case decks and structured results are saved in [bias-resistor-screen](bias-resistor-screen/CONTEXT.md). Run `python3 engineering/component-selection/evidence/bias-resistor-screen/factory/run.py`. [Results](bias-resistor-screen/runs/results.json) include source/runtime/factory SHA256 values; [ngspice log](bias-resistor-screen/runs/ngspice.log) includes version and diagnostics. The original16 results reproduce the values above exactly.

Added128 high-source corners: each R39/R40 at±5%, each capacitor8/12µF, phase0/90/180/270°, trimmer1Ω/55k, R38/R503 at−5%,65µA leakage. Source peak84.739676657V is the earlier235.4V/12%regulation assumption. Corner decks use discharged capacitors and UIC so nonzero phase represents switch-on, not a charged DC operating point.

R39 maximum settled power0.008774256W; maximum instantaneous0.303609534W; maximum differential38.099927V; maximum first100ms energy0.013301415J. Even the instantaneous peak is below100°C derated continuous0.64706W. This strengthens the scoped R39 choice; it does not cover arbitrary fault or hot leakage. R40 maximum settled0.013792924W but instantaneous7.419263188W,83.960064V,first100ms0.045474786J. Keep R40 pulse qualification open. Maxima need not come from the same corner.

Validation:144 completed decks, matching saved deck hashes, matching factory hash and finite nonnegative metrics. Scoped ICM checker reports clean. Remaining limitations: actual transformer regulation/impedance, mains beyond assumed bound, hot leakage, fast restart with residual charge, faults and local component temperature.

Runtime: ngspice45.2 shared library. Log contains `can't find the initialization file spinit`; the project runtime explicitly loads its KiCad code-model modules and sets compatibility behavior. These decks use native sources, resistors, capacitors, diode and behavioral leakage sources. All144 transients reached2s; no convergence failure was reported. The missing optional startup file is recorded rather than hidden.
