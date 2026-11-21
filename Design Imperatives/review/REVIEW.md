# Review of the seven design-imperative files

Reviewed October 4, 2026 against the [handoff](../../Renegade_Codex_Handoff.md), [prototype plan](../../plans/renegade-working-prototype/plan.md), [original source](../../sources/original-ppt/inspection.md) and [simulation contract](../../simulation/requirements.md).

**Assessment:** these form a useful, broadly consistent reference set. The strongest guidance is to design complete current loops, derive ratings from real conditions, preserve safety isolation/earth, and verify the physical amplifier. No project-stopping contradiction was found in this document-level review. They are principles and review prompts; they do not yet define the numerical rules, chosen parts or acceptance evidence for this amplifier.

All seven originals were read in full and retained unchanged. [inventory.json](inventory.json) records their identities, hashes and numbered-rule counts. External verification was targeted at consequential China supply/standards claims, arithmetic examples, tube data, grid-resistor evidence and KiCad creepage support. Every citation was not independently audited, and no circuit, layout or hardware is approved by this review.

## Coverage
| File | Numbered rules | Assessment |
|---|---:|---|
| [Tube amplifier](../audio_tube_amplifier_design_imperatives.txt) | 60 | Most directly applicable: operating points, bias, screens, output load, heaters, reverb and footswitch isolation. |
| [China 220 V supplies](../China_220V_Power_Supply_Design_Imperatives.txt) | 40 | Directly relevant; numerical supply envelope and cited standards checked, with scope qualifications below. |
| [Power circuits](../power_circuit_design_imperatives.txt) | 28 | Relevant supply/ratings/return-path and physical commissioning prompts. |
| [Audio circuits](../Audio_Circuit_Design_Imperatives.txt) | 50 | Relevant interfaces/headroom/noise/switching; some op-amp/balanced/BTL advice is conditional. |
| [Audio PCB problems](../Audio_Amplifier_PCB_Problems_to_Avoid.txt) | 52 | Useful failure checklist covering tube hardware and generic solid-state stages. |
| [PCB layout](../PCB_Layout_Design_Imperatives.txt) | 66 | Useful placement/DFM/return-path/insulation guidance; not a numerical design-rule file. |
| [Trace placement](../PCB_Trace_Placement_Design_Imperatives.txt) | 68 | Strong explanation of parasitics, return paths and isolation exceptions; device-specific examples require scoping. |

There are 364 numbered items, with substantial overlap. Use [prototype-checks.csv](prototype-checks.csv) to group the work into 20 evidence areas. Do not treat overlap as 364 independent hardware tests or claim any check passed merely because a rule was read.

Tracker references use the inventory prefixes `TUBE`, `CN`, `PWR`, `AUD`, `APCB`, `LAY` and `TRACE` plus the original item number. Ranges are inclusive. `PROJECT-*` labels refer to handoff/simulation requirements that supplement these imports. Fill the initially blank responsible owner, method, numerical acceptance limit, evidence path and revision fields as design work proceeds; explain any not-applicable result.

## Findings and recommended treatment

### 1. China supply limits: verified, with scope
China file items 1–2 correctly distinguish 220 V single-phase supply from 380 V line-to-line supply. The 2024 supply rules specify 50 Hz and 220 V single phase in Articles 6–7, and +7%/−10% normal single-phase voltage deviation in Article 57. That gives **198–235.4 V** by arithmetic. The regulation also discusses abnormal conditions and a power-factor qualification; these numbers do not define every transient or an appliance's required operating range. The original Ministry of Justice URL returned a redirect-loop error in this check; an accessible [NDRC primary text](https://zfxxgk.ndrc.gov.cn/wap/iteminfo.jsp?id=20347) supports the claim.

Keep the supply envelope separate from the engineering test envelope. The [simulation contract](../../simulation/requirements.md) now includes 198/220/235.4 V as normal-boundary/nominal cases and retains 242 V as additional high-line engineering stress. This updates the planned cases only; no new amplifier simulation was run. Review actual transformer, heater, bias and capacitor conditions at those cases before selecting a rated input range.

### 2. Standards: current records confirmed, applicability still needs review
The SAMR record lists [GB 1002-2024](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=F8C9E208891B7BB5AF1B3E64933693C2) as current, effective August 1, 2025. Its scope concerns plug/socket types, parameters and dimensions; it alone does not establish a complete cord set's suitability or whole-product conformity. China file item 10 should retain the requirement to verify the actual cord/inlet assembly.

[GB 4943.1-2022](https://std.samr.gov.cn/gb/search/gbDetailed?id=Y8G8ELIiFZ0%3D&mode=p) is listed as current and replaces GB 8898-2011 and GB 4943.1-2011. China file item 40 is a useful starting reference. This review checked the standard record, not its full requirements or the finished product's classification. Determine the applicable clauses/insulation requirements with the responsible reviewer. Keep later commercial certification/EMC work separate from the one-prototype milestone, while preserving its engineering safety checks.

### 3. Grounding advice is compatible when scoped to real current paths
The files support continuous references within non-isolated domains, deliberate audio star/bus arrangements where suitable, and local stage returns. These are compatible choices, not three mandatory competing ground topologies. Derive one whole-amplifier return diagram including boards, reservoir currents, sockets, heater reference, control supply, jacks, shields and chassis bonds.

Trace items 9 and 60 correctly prevent ground stitching across an isolation barrier. Apply that exception to PCB-layout item 16 as well. Keep protective earth distinct from signal/noise design. A full copper pour is not an automatic solution for high-impedance tube nodes, mains boundaries or low-frequency magnetic pickup; the documents already contain the relevant qualifications.

### 4. One tube-specific citation needs replacement
Audio-circuit item 41 correctly distinguishes a grid stopper from a grid DC-return resistor, but cites [ADI AN-937](https://www.analog.com/en/resources/app-notes/an-937.html). AN-937 concerns op-amp/instrumentation-amplifier bias paths; it is useful for item 6 but does not directly establish tube grid-stopper behavior. For item 41, use the tube-specific [Aiken grid-resistor explanation](https://www.aikenamps.com/index.php/grid-resistors-why-are-they-used) and [Valve Wizard grid-stopper reference](https://www.valvewizard.co.uk/gridstopper.html), plus the selected tube's datasheet for resistance limits. Keep actual values and socket placement subject to the circuit review.

### 5. Add the missing second datasheet to the heater example
China item 32's **0.6 A at 6.3 V** addition is consistent with the cited JJ equivalents: [ECC81](https://www.jj-electronic.com/images/stories/product/preamplifying_tubes/pdf/ecc81.pdf) and [ECC83S](https://www.jj-electronic.com/images/stories/product/preamplifying_tubes/pdf/ecc83s.pdf) each specify 300 mA at 6.3 V. The current reference [17] points only to ECC81; add ECC83S to substantiate both tubes. This example does not select JJ parts or finish the total heater budget; use the actual chosen versions and add the original tubes, lamp and other loads.

The China file's rectifier warning is also correct as an ideal no-load example: 290–0–290 V is 580 V end-to-end and a bridge across the full winding approaches `580*sqrt(2) ≈ 820.24 V` before losses. Loaded voltage/regulation and winding RMS current require the actual topology/model. [Hammond's rectifier guide](https://www.hammfg.com/files/products/700/hammond-recitifier-guide.pdf) explicitly distinguishes centre-tapped and bridge arrangements.

### 6. KiCad creepage support is real, but does not choose the safety requirement
Trace item 66 correctly says KiCad 10 supports creepage constraints. The [KiCad manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#custom_design_rules) documents a `creepage` constraint and DRC creepage violations. Its example numbers are examples, not approved limits for our circuit. DRC needs derived inputs and accurate geometry; it does not inspect all assembled off-board wires, component insulation, fasteners or chassis surfaces. Validate the proposed rules on this installation and retain manual assembly review.

### 7. Conditional rules must not silently change the product
Op-amp noise gain, BTL speaker connections, class-D output routing, controlled impedance, differential pairs, SMPS hot loops and exposed-pad cooling apply when those devices/topologies exist. They do not require adding them to the tube signal path or mechanically applying RF layout techniques to every audio trace. They may apply to a control supply, supporting instrument or a future buffer. Record applicability by actual block and exact device.

Several sources are broad portals, videos or examples for unrelated parts: ADIN1300/1200, TPS715, LM3886, Alpha 400 and some general vendor catalog links. These can explain principles but do not replace the eventual chosen part's datasheet, layout, insulation and thermal requirements. Further claim-by-claim citation review remains pending beyond the checks named here.

### 8. Convert qualitative prompts into project evidence
The main missing layer is implementation: selected-part ratings, actual clearances/creepage and trace sizes, declared current/thermal limits, and numerical audio/switching acceptance criteria. The seven documents also do not fully specify our recent selected-component simulation requirement, actual cabinet/speaker/tank geometry or top/front control arrangement. Those already live in the handoff and prototype plan; preserve them alongside these references.

Before PCB release, populate the consolidated checks with exact circuit/BOM/model revisions, owner, limit/calculation source, method and evidence. A check can be pending, evidenced, failed or reasoned not-applicable. Simulation, native CAD checks, manual layout review and physical tests provide different evidence; one cannot substitute for all the others. Initial CSV rows are **pending evidence**, not claims that the prototype passes.

## Prototype integration
Use these references during P01/P04 for source reconciliation, requirements, chosen parts and simulation; P02/P03 for cabinet/part-envelope fit; P05 for rules/layout/drill/assembly review; and P07/P08 for staged electrical and in-box validation. Keep quantity-one cost and serviceability in the decision, with commercial work retained for later. The imports do not authorize purchases, supplier messages or electrical energizing.
