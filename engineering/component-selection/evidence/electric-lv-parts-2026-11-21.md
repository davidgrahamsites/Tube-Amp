# Electric build: low-voltage parts qualification, 21 November 2026

Owner: remaining-parts delegated worker. Integration owner: root engineering agent.
Inputs: current `engineering/whole-amp/reverb-600/circuit.json`, component coverage and candidate register, previous semiconductor/relay evidence, manufacturer drawings and dated supplier observations.
Process: check exact identities, ratings against actual circuit loads, and pad functions. Separate part selection from system release.
Output: this evidence dossier only. No circuit, footprint, BOM or shared register changed.
Human check: inspect each cited drawing beside the proposed symbol/footprint, then review voltage, reset and temperature corners before accepting the integration.

## Result

C321 and C602 are exact engineering selections ready for integration review. Four BAT54HT1G clamps are viable substitutions within the passive footswitch contract, with protection qualification still open. U3 and Q1/Q2 have real worst-case qualification gaps; do not close them by nominal ratings. C605 remains held against its existing voltage requirement. Alternative supervisor and MOSFET proposals below are candidates, not applied changes.

## Selections and dated purchasing evidence

All RMB observations in this table come from the existing **11 November 2026** register. They are not new stock checks. Public pages checked on 21 November corroborate identities; they did not expose fresh signed-in domestic quotes.

| Ref | Exact manufacturer / MPN | Domestic SKU and page | Recorded RMB/unit; MOQ; stock | Disposition |
|---|---|---|---|---|
| C321 | KNSCHA 82CL0120 | [C5359301](https://item.szlcsc.com/6172077.html) | 0.2784; 10; 3340 | Select 47 nF, 5%, 63 V polyester; explicit timing bounds below |
| C602 | KYET KP223J2J1001 | [C390074](https://item.szlcsc.com/366157.html) | 0.293; 10; 29520 | Select 22 nF, 5%, 630 V polypropylene; change provisional 5 mm pitch to 10 mm |
| D301/D302/D311/D312 | onsemi BAT54HT1G | [C21107](https://item.szlcsc.com/21819.html) | 0.2047; 20; 151K+ | Conditional engineering substitution for BAT43; SOD-323 replaces axial footprint |
| Q1/Q2 | onsemi 2N7000 | [C232838](https://item.szlcsc.com/232636.html) | 2.3594; 5; 1115 | Hold gate-drive/hot qualification |
| U3 | TI TPS3808G50DBVR | [C134123, global](https://www.lcsc.com/product-detail/C134123.html) | Register says 8.39; 1; 1539, but source is global and domestic currency/stock were unverified | Hold reset-release corner |
| C605 | FH 1206CG331J500NT | [C1907](https://item.szlcsc.com/2259.html) | 0.234608; 20; 1720 | Hold: 50 V does not meet unchanged 63 V requirement |

### C321: use KNSCHA 82CL0120

Exact manufacturer approval, 30 January 2023 V1.0: [PDF supplied through the domestic listing](https://atta.szlcsc.com/upload/public/pdf/source/20230221/6E41F153EF974EA71CF5BDBCAC91035B.pdf). Drawing page 2 was visually inspected. Body W7.2 × H6.5 × T2.5 mm, each ±0.5; lead pitch 5 ±0.5 mm; lead diameter 0.5 ±0.05 mm. Use 0.9 mm finished holes and 1.8 mm pads, with body maximum 7.7 × 3.0 mm and maximum height 7.0 mm. Polarity: none. Maintain local temperature at or below 85°C; manufacturer voltage derating applies above that.

C321 connects RESET_CT to ground. The 63 V rating has ample margin against this low-voltage node. Minimum specified insulation resistance is 3 GΩ under the stated room-temperature test. At the nominal 1.23 V timing threshold, an ideal resistance extrapolation gives 0.41 nA leakage, about 0.19% of the nominal 220 nA charging current. This is not a guaranteed hot leakage figure.

Calculated nominal reset delay: 47/175 + 0.0005 = **0.2691 s**. Capacitor tolerance alone gives **0.2556–0.2825 s**. IC timing tolerance must also be included. The TPS3808 table gives roughly ±40% limits at its tabulated timing-capacitor test points; applying that fraction as a planning estimate gives about **0.153–0.396 s**, not a manufacturer-guaranteed interpolated 47 nF bound. Bench-check startup/reset delay. No simulated or measured timing is claimed here.

### C602: reuse the exact KYET 22 nF part

Primary evidence already retained: `KYET-KP223J2J1001.pdf` and `.txt` in this evidence folder; selection rationale in `../film-cap-selection.md`. Nominal body 12 × 10 × 4.5 mm; each dimension ±1 mm, so reserve 13 × 11 × 5.5 mm. Pitch 10 ±0.5 mm; lead diameter 0.6 ±0.05 mm; use existing exact KYET footprint with 0.9 mm finished holes. Temperature −40 to 100°C.

C602 is SEND_BUF to SEND_TOP. Its original 63 V minimum is satisfied. Keep 22 nF; changing to the known part does not change the intended filter value. The benefit is a previously qualified, low-cost domestic part, not an assertion that a higher voltage marking improves sound. It is physically larger than the provisional 5 mm pitch part: rerun clearance and routing checks.

## Clamp substitution: four BAT54HT1G

[onsemi BAT54HT1/D Rev.9, November 2024](https://www.onsemi.com/pdf/datasheet/bat54ht1-d.pdf), including visually inspected case-477 drawing: **pad 1 cathode, pad 2 anode**. Maximum body 1.8 × 1.35 × 1.0 mm; maximum terminal span 2.7 mm. Use the manufacturer's SOD-323 land pattern and verify assembly cathode marking. Ratings: 30 V reverse, 200 mA maximum, 200 mW at 25°C with 1.6 mW/°C derating. At 25°C, maximum forward drops are 0.32 V at 1 mA and 0.40 V at 10 mA; reverse leakage maximum is 2 µA at 25 V. No guaranteed high-temperature leakage table was found.

| Ref | Pad 1, cathode | Pad 2, anode |
|---|---|---|
| D301 | +5V | BTN_CH |
| D302 | BTN_CH | GND |
| D311 | +5V | BTN_REV |
| D312 | BTN_REV | GND |

Existing schottky symbol pad functions agree. This is a footprint change, not a pad-number reversal. Normal passive-switch operation gives about 0.455 V at the pressed button node from the 10 kΩ pull-up and 1 kΩ cable resistor. A conservative 2 µA leakage calculation moves the open level only 20 mV through 10 kΩ at room temperature. The 15 kΩ resistor between button and HC14 input remains required.

An accidental +12 V connection could inject about 6.6 mA through the upper clamp into +5 V. That diode current is modest, but the regulator may not sink it. Therefore this substitution **does not qualify powered pedals, back-powering, IEC ESD or cable surge protection**. Verify hot leakage/noise margin and transient rail behavior before system release. Parent may select the exact physical clamp while retaining these system holds, or retain candidate status until those checks close.

## U3: exact pins are correct; reset release is not closed

[TI TPS3808 datasheet Rev.N, August 2026](https://www.ti.com/lit/ds/symlink/tps3808.pdf): DBV pin functions are 1 RESET, 2 GND, 3 MR, 4 CT, 5 SENSE, 6 VDD. Recommended supply is 1.7–6.5 V. G50 threshold is nominally 4.65 V, ±2% over full temperature, with up to 2.5% hysteresis. A 10 kΩ RESET pull-up is within TI's recommended range. Maximum RESET low is 0.4 V at 1 mA for VDD≥1.8 V; maximum output leakage is 300 nA. TI calls for local 100 nF ceramic supply bypass. G01 has 0.405 V nominal adjustable threshold, ±2%, maximum 3% hysteresis, ±25 nA sense current. Same DBV pin mapping applies.

Current net mapping agrees: 1 RESET_N, 2 GND, 3 MR_N, 4 RESET_CT, 5 +5V, 6 +5V. Existing pull-up load is about 0.5 mA, inside the stated low-level test. The pad identity is not the blocker.

Our worst-corner calculation for G50 is 4.65 × 1.02 × 1.025 = **4.8616 V** maximum rising release. Even using the tighter below-85°C threshold tolerance gives 4.8377 V. A +5 V rail allowed down to 4.75 V therefore cannot guarantee reset release. Do not erase this with a nominal 5 V simulation. First obtain the actual regulator minimum including load, line and temperature. If it exceeds the complete rising threshold plus noise margin, keeping G50 remains possible.

### Concrete supervisor candidate

**TI TPS3808G01DBVR**, [LCSC C19653](https://www.lcsc.com/product-detail/C19653.html), retains CT/MR and the same SOT-23-6 pin assignment. Proposed divider: upper 98.6 kΩ and lower 10.0 kΩ, both 0.1%, for 4.3983 V nominal falling threshold. This is a proposed circuit change: SENSE must leave +5V and connect to the divider midpoint. Exact divider resistor procurement has not been selected.

With resistor ratios, ±2% reference, ±25 nA sense current and 3% hysteresis included, calculated falling threshold is approximately **4.300–4.497 V** and maximum rising threshold approximately **4.632 V**. This clears a 4.75 V rail by about 118 mV at the static corner. It protects against collapse below the HC family's 2 V minimum operating supply, but **does not itself guarantee the existing HC74 output-drive specification tabulated at 4.5 V during brownout**. Close the gate chain over 4.30–4.50 V or choose a different reset/logic arrangement before adoption. Domestic price, MOQ and stock for this TI variant remain unverified; the public global listing proves identity, not a mainland quote. No clone with the same base marking is approved.

## Q1/Q2: exact onsemi pinout and actual load

[onsemi NDS7002A/D Rev.11, March 2025](https://www.onsemi.com/pdf/datasheet/nds7002a-d.pdf) includes exact **2N7000** ordering, as well as differently packed variants. TO-92 functions: **1 source, 2 gate, 3 drain**; these match current circuit pins. Its 60 V drain and ±20 V gate ratings are sufficient for nominal 12 V relay operation. RDS(on) maximum is 5.3 Ω at VGS=4.5 V, ID=75 mA, 25°C. No equivalent guaranteed hot 4.5 V limit is given. Full dimensional/lead-form footprint inspection remains open; do not use a generic transistor drawing to close it.

Current relay load uses G5V-2-H1 DC12, 960 Ω ±10% at 23°C: two coils on Q1 and one on Q2. At 12.6 V/minimum resistance, Q1 carries **29.17 mA**, Q2 **14.58 mA**. At 5.3 Ω, Q1 loses only **4.51 mW**, dropping **0.155 V**. These calculations show that power is not the primary unresolved issue.

The TI SN74HC74 data retained in `TI-SN74HC74.pdf` guarantees VOH≥3.84 V at VCC=4.5 V and −4 mA over −40…85°C. The 100 kΩ gate pull-down draws roughly 50 µA at nominal rail, so the −20 µA/4.4 V guarantee cannot simply be used. With a worst-case 1 kΩ/100 kΩ divider (1% tolerances), the conservative gate bound is **3.801 V**, below the MOSFET's 4.5 V guaranteed-resistance test. Gate threshold is not a full-on guarantee. Keep 2N7000 held.

### Concrete MOSFET candidate

**Alpha & Omega Semiconductor AO3400A**, [domestic C20917](https://item.szlcsc.com/21629.html). Specify AOS; other manufacturers sell the same-looking part number. Public domestic identity was rechecked 21 November; fresh RMB quote/MOQ/stock were not returned. Existing public global retail evidence has a five-piece tier, but it is not a new domestic stock observation.

[Manufacturer product page](https://www.aosmd.com/products/mosfets/low-voltage-mosfets-12v-30v/ao3400a), [datasheet Rev.3.1 July 2023](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf): maximum RDS(on) 48 mΩ at 2.5 V gate/3 A/25°C, 30 V drain, ±12 V gate. Thus the existing 3.801 V gate bound at VCC=4.5 V exceeds its guaranteed 2.5 V test voltage. The 25°C Q1 conduction estimate is only 41 µW and 1.4 mV. This addresses the existing nominal-supply gate-drive gap. Hot operation and the proposed lower reset threshold still require separate chain checks; typical transfer curves do not close them.

**Replacement mapping: pad 1 GATE, pad 2 SOURCE, pad 3 DRAIN.** This swaps the current 2N7000 pad-1/pad-2 functions and changes TO-92 to SOT-23. Verify that mapping against the manufacturer top/bottom-view drawing during integration; the 2N7000 symbol cannot be reused unchanged. [AOS package PO-00001N](https://www.aosmd.com/sites/default/files/res/package/SOT23.pdf) gives maximum body 3.10 × 1.80 mm, terminal span 3.00 mm, height 1.25 mm, 0.95 mm pitch; manufacturer lands are 0.8 mm squares with 2.4 mm row spacing. Pin functions are read from the device view; numbering must agree with the footprint orientation.

Nominal drain clamp estimate is about 12.6 V + flyback forward drop. The 30 V part has less overshoot margin than 2N7000. Keep flyback diodes at the coils and verify peak drain voltage under switching; use **24 V maximum as an engineering acceptance target**, not a manufacturer claim. Candidate only: no circuit or footprint changed.

## C605 remains held

The [FH manufacturer table](https://fhcomp.com/en/product_page/?code=010100&page=487) indexes exact **1206CG331J500NT**, 330 pF, 5%, C0G, 50 V, body 3.20 ±0.30 × 1.60 ±0.30 × 0.80 ±0.20 mm. The public table was available in search indexing; direct page retrieval timed out. The LCSC-hosted PDF retrieval was blocked. Preserve that evidence limit.

This part would replace a through-hole provisional footprint with 1206 SMD, but it **does not satisfy the current 63 V minimum**. Do not change that requirement implicitly. C605 is REC_OUT to REC_FB, across R608=100 kΩ. Its nominal RC pole is 4.823 kHz. A full ±16 V rail envelope suggests a 32 V differential ceiling only if both nodes are demonstrably bounded during startup, overload and faults. That proof has not been completed here. Retain the existing requirement, or explicitly approve the differential qualification before using a 50 V candidate.

## Integration handoff

1. Integrate C321 and C602 with the dimensional changes above; retain reset timing and system fit checks.
2. Decide clamp selection status separately from transient/ESD qualification; preserve exact cathode/anode mapping.
3. Resolve the +5 V regulator corner before choosing G50 retention versus G01 redesign. Do not choose a lower threshold without checking brownout logic and relay state.
4. If AO3400A is adopted, change symbol pins and footprint together, and verify startup, dropout, coil temperature and drain overshoot.
5. Keep C605 at its existing voltage requirement until a separate stress decision is recorded.
6. Root owns ICM decision/register/BOM integration, scoped checks and catalog rebuild. This delegated evidence-only change neither claims simulations rerun nor build readiness.
