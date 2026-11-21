---
id: CMP-021
type: component
domain: components
status: proposed
updated: 2026-11-20
---
# Mainland low-quantity component sourcing

The user requires exact component selection before the whole-amp PCB update. The canonical working inventory is [candidate register](../../engineering/component-selection/candidate-register.json), with [coverage](../../engineering/component-selection/coverage.json) against 127 electrical groups. Candidates are not procurement release or verified operating suitability.

79 supplier records currently cover 95 groups. Evidence includes signed-in domestic LCSC stock, minimum quantities and CNY price observations dated November 11. Prices and stock can change; no purchases occurred. Read [sourcing checkpoint](../../engineering/component-selection/evidence/sourcing-checkpoint-2026-11-11.md) for rejected stock claims and mismatched manufacturer documentation.

## Filter capacitor finding

CRC FC6136, C47089333, is stocked at MOQ1, CNY29.78,156 units observed. Four cost CNY119.12 before shipping. Its exact [approval sheet](../../engineering/component-selection/evidence/CRC-FC6136.pdf) specifies50µF±10%,900VDC,57.5×50×35mm body (±1), four leads on52.5×20.3mm pattern,1.2mm lead diameter and4±1mm length. It preserves nominal filter capacitance, unlike series-electrolytic substitutions requiring extra balancing networks.

This is a mechanically substantial four-pin part, not a drop-in for a two-pin draft footprint. Confirm terminal pairing, fit, support, solderability of short leads and thermal/ripple stress before layout release. The25A current claim lacks a frequency condition. The100000h≤85°C table and generic life graph disagree; do not advertise that life as verified. The generic PP voltage derating graph still needs explicit operating-temperature interpretation.

## Evidence exclusions

The distributor's Tyohm820Ω datasheet is actually a different manufacturer's MF-series document. Official Tyohm RN data lack the listed1WS variant and warn of50V use above100kΩ. Yageo MF0207 is a better documented candidate for high-value parts, subject to actual power/working-voltage derating.

## Reservoir leakage screen

[Analytical results](../../engineering/component-selection/reservoir-balance-results.json) and independent [ngspice OP results](../../engineering/component-selection/reservoir-balance-ngspice.json) agree within6e-14V. At the existing assumed510.31V supply peak,220k±5% balancing resistors and20°C five-minute leakage bounds, AishiEHS2GM221M45OT permits463.77V across a400V capacitor: rejected for this network. NichiconLGU2G221MELB yields365.56V in the same screen; mainland stock7,MOQ1,CNY26.9192 observed. This is not hot-leakage, startup or actual-transformer validation. ManufacturerGU andHS sheets are saved. Hot operation and capacitor ripple limits remain open.

Bourns3296W-1-503LF and104LF and JSTXH headers/housings/contacts have mainland stock evidence. XH's85°C limit includes self-heating; use only in the cool low-voltage area. [Mating hardware inventory](../../engineering/component-selection/harness-hardware-candidates.json) does not yet fix cable lengths or crimp tooling.

## Resistor operating-point screen

The reproducible [DC resistor screen](../../engineering/component-selection/check_resistor_op.py) ran both channels in the existing generic-tube fixture. [Results](../../engineering/component-selection/resistor-op-results.json) include every explicitly numbered resistor present in that fixture, generated decks and logs. At 400V stiff B+ and -40V bias, R35 dissipates0.7445W, R22 dissipates0.3109W at176.32V, and R21 dissipates0.1875W. Other100k plate loads are below0.1W at this operating point. These results support assessing R22 separately from the other100k parts; they do not justify indiscriminate wattage changes or qualify any selected resistor. Supply startup, overload, signal peaks, tolerances, ambient-temperature derating and board heating still require checks. The fixture excludes the reservoir balancing resistors; their separate leakage analysis is linked above.

## Remaining work

Complete exact components and hardware, stress calculations and pin/footprint checks; then update native CAD and re-run selected-component simulations/ERC/DRC and cabinet-fit review. Mail follow-up is prepared but not sent because Mail failed to load compose windows; original Mable inquiry was already sent. Supplier dimensions and tank/transformer specifics remain pending. The design is not build-ready.

## November12 selected bias capacitors

[C27/C28 selection](../../engineering/component-selection/bias-capacitor-selection.md) fixes Samyoung NFA200VB10M8*11.5_LO,C371316. Manufacturer dimensions/life/leakage and domesticMOQ5/¥0.6858 were checked.16 scoped transient cases complete; native3.5mm-pitch footprint is prepared, reloaded and visually reviewed. Integration, hot operation and actual transformer qualification remain open. [New sourcing exclusions](../../engineering/component-selection/evidence/sourcing-checkpoint-2026-11-12.md) prevent treating the MableJJ/Alpha categories and an out-of-stock Nichicon part as verified inventory.

## November12 resistor and internal-trimmer selections

[HV100k selection](../../engineering/component-selection/hv-100k-selection.md) assigns YageoFMP200JR-52-100K to nine references;27 nominal-DC/temperature screens pass. Exact native footprint is prepared, reloaded/exported and visually reviewed, not yet integrated. [Trimmer selection](../../engineering/component-selection/trimmer-selection.md) assigns Bourns3296W-1-503LF/104LF to RV10/RV601;18 partial-track density checks and24 bias endpoint transient runs pass within stated assumptions. Exact panel pots/knobs remain separate and unresolved.

[Screen resistor evidence](../../engineering/component-selection/evidence/screen-resistor-research-2026-11-12.md) adds RESIEWWR0010J4K70T9/C349127:4.7k±5%,10W,MOQ1,¥3.94,14stock November12. Manufacturer curve/drawing reviewed;4.35W average candidate stress fits nominal derating at125°C, but high-line/pulse/actual temperature and working voltage remain open. This is a conditional circuit-change candidate, not a silent replacement of the original1k value. Supplier register now has78 rows.

Mail status clarification: cabinet/tank follow-up was sent November12 at03:23; expanded electronic-parts RFQ remains unsent. Yellow tweed and mainland RMB/WeChat Pay/Alipay with Shanghai shipment are the user's requirements. Native Mail requires a chirp and explicit confirmation before control. LCSC login was confirmed again; no further sign-in request is pending.

## November12 selection checkpoint

The [selected engineering BOM](../../engineering/component-selection/selected-engineering-bom.csv) contains25MPNs covering63references/28groups; it is explicitly a subset, not a complete procurement BOM. New dossiers: [19 signal resistors](../../engineering/component-selection/signal-resistor-selection.md), [16 film capacitors](../../engineering/component-selection/film-cap-selection.md), [four rectifiers](../../engineering/component-selection/rectifier-selection.md), [five IC positions](../../engineering/component-selection/logic-audio-ic-selection.md).57 resistor DC/temperature checks and32 capacitor DC checks pass within their documented nominal assumptions.

[Footprint integration manifest](../../engineering/component-selection/footprints/integration-manifest.json) maps54references, including two socket-local grid resistors and52PCB placements. Native four-board hashes remain unchanged. Exact local footprints for selected film capacitors,signal/HV resistors,bias caps andtrimmers have native parse/export and visual evidence. This is integration preparation; remaining exactparts, transient/thermal qualification, layout changes and supplier fit evidence are still required.

[Power-divider selections](../../engineering/component-selection/power-divider-resistor-selection.md) addFMP200220k/39k forR501/R502/R506/R507. Static screens support≤100°C local ambient; R506fails125°C. This thermal condition must be enforced by placement and physical evidence. Expanded parts RFQ remains unsent and now requests50WOT/250mAPT quote options because original magnetics ratings are not established for the simulated load; no final transformer choice or order.

[C1/C5 exact25µF selection](../../engineering/component-selection/cathode-cap-selection.md): CHCD11AT2GM250F170T,C49435383,335stock,MOQ5,¥1.0213 observedNovember12. Exact approval sheet and native footprint checked. Selection carries a proposed incoming low-voltage leakage screen; hot-life test condition remains incomplete. Eight leakage scenarios are saved. Current selected subset is25MPNs/63references, approximately¥248.55 at recorded MOQ tiers, excluding all remaining parts/shipping.

## November12 additional Mable catalogue review

[Catalogue screening](../../engineering/component-selection/evidence/mable-catalogue-review-2026-11-12.md) adds EL34 retainer and10H250mA choke leads; rejects stock3.6k JCM800 OT and500k guitar pots as direct substitutions. Exact socket/knob candidates remain conditional. Expanded RFQ now includes retainers and passive expression pedal questions; still unsent. No selected BOM or native PCB change.

## November15 parallel selection pass

[Reviewed results](../../engineering/component-selection/parts-sprint-2026-11-15.md) add32 fitted positions:19resistors,6capacitors,3relays,4diodes. Current total34selectedMPNs/95references/44groups. MOQ subset estimateRMB324.47; dated inventory retained. Exact operating envelopes and remaining qualification/fit checks are documented. Native boards unchanged; no procurement release.

## November19 received-tank resistor integration

Canonical coverage now follows600R-1: R601 moves to1M/P096; R602 becomes100k/P080; R612 becomes passive dry; R618 is new1Mwet mixing. MFR50SFTE52-100K selects7positions and MF0207FTE52-1M4positions (2already selected), adding9positions. Total104selected refs/34MPNs/46groups. Stock/prices retainNovember11 dates. [Dossier](../../engineering/component-selection/evidence/reverb-resistor-picks-2026-11-19.md) retains R605flameproof candidate and R616fault-envelope gap. [VAL-013](VAL-013-received-tank-revision.md) records native/simulation scope.
