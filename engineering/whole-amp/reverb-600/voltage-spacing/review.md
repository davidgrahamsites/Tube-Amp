# Tube-interface spacing and connector review

2026-11-25, baseline `579a009`. Owner: amplifier integration. **Manufacturing remains held.** This pass corrects acceptance records and tests spacing on temporary copies; it does not change the circuit, PCB or functional blocks.

## Findings tied to the current design

The retained VAL061 passive stress fixture was checked against the current values and pin connectivity of 15 participating references. C607's voltage rating/package and R601's package changed since that run, but their electrical values did not. R619/R620 do not participate in the ideal wet-source fixture. An independent DC reduction reproduces the stored fault voltages. This is evidence reuse with explicit limits, not a new whole-amplifier simulation.

| Interface | Retained conditional C6-short result | Acceptance consequence |
|---|---:|---|
| JR1 signal to GND | 293.455 V DC | Existing 250 V XH candidate cannot cover this retained envelope |
| JR5 signal to GND | 276.844 V DC | Same; canonical “low voltage only” requirement is wrong |
| K3 wet contact to ground | 138.422 V DC | Exceeds 125 V DC maximum switching voltage; fault-time switching qualification is open |

[JST XH manufacturer data](https://www.jst.com/wp-content/uploads/2025/06/eXH.pdf) specifies 250 V AC/DC. XH is only a candidate: the native board still has generic 2.54 mm headers. This rejection applies to JR1/JR5 under the retained topology, not every low-voltage XH use.

[Omron G5V-2 data](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v_2.pdf) specifies 125 V DC maximum switching voltage. Its dielectric withstand test is a different rating and does not authorize switching 138 V. The fixture holds K3 open, so it does not prove arcing or actual contact damage; it identifies an unqualified operation if the controller changes state during that fault. Keep the selected relay on engineering hold for this use until the approved buffered-loop/protection integration limits its exposure or an appropriate alternative is qualified.

## Conditional geometry check

The existing global 0.25 mm rule reports **0 violations, 0 opens**. A temporary 2.5 mm clearance / 4 mm creepage comparison on FX_RETURN, IN_AC, MIX_OUT and WET_AC produces **72 clearance and 22 creepage reports**, with **0 opens**. There are 91 unique typed item pairs; these are not 94 independent physical defects. Five reports are pad-to-pad, 89 involve tracks or vias. The latter are routing constraints, not proof that each can be fixed by moving one trace.

The comparison is deliberately provisional. [TI SLUP421](https://www.ti.com/lit/ml/slup421/slup421.pdf), page 24, tabulates 2.5 mm for uncoated IPC-2221B conductors at 400 V. Its page 20 example uses 4 mm creepage for 400 V, pollution degree 2 and material group III. Those examples inform this engineering screen; they do not establish the amplifier's applicable safety standard, complete voltage-pair envelope, insulation class or certification. No solder-mask credit is assumed. The blanket four-net rule can overconstrain some pairs. It is **not adopted as a qualified production rule**.

Independent native-pad measurements identify fixed limits:

| Native feature | Center distance | Copper edge gap | Required next action |
|---|---:|---:|---|
| JR1 pads 1–2 | 2.54 mm | 0.84 mm | Qualified connector/footprint or proven lower voltage envelope |
| JR5 pads 1–2 | 2.54 mm | 0.84 mm | Same |
| K3 pads 13–11 | 5.08 mm | 3.28 mm | Resolve actual voltage/creepage requirement and relay operating exposure |

These gaps are planar PCB geometry, not a measurement of insulation inside a connector or relay. The candidate DRC also finds WET_AC routing close to K3's unused pad and a long FX_RETURN route close to recovery circuitry. The populated geometry and return-current paths need review together. A broad ground pour is still held until the voltage domains and rules are settled.

## Higher-voltage connector lead, not a selection

[Phoenix 1766770](https://www.phoenixcontact.com/en-us/products/pcb-header-gmstbva-25-2-g-762-1766770) with [1766990 plug](https://www.phoenixcontact.com/en-us/products/pcb-plug-gmstb-25-2-st-762-1766990?type=pdf) is a 7.62 mm pitch comparison pair. Manufacturer data specifies 630 V in its III/2 rating context. Header dimensions are 15.24 × 8.6 mm, installed height 12 mm, with 1 × 1 mm pins and a stated 1.4 mm PCB hole. Pin/hole tolerances and the mating assembly drawing must be reconciled before generating a production footprint. It has no locking feature: independent retention remains necessary. It is not intended for connection/disconnection under voltage or load.

The [Chinese LCSC plug listing C90069](https://item.szlcsc.com/91254.html) exists, but public text did not expose live stock, price or MOQ. Its description says 630 V while its attribute table says 300 V; approval contexts must remain distinct. [LCSC C3579516](https://www.lcsc.com/product-detail/C3579516.html) lists the header, but a global listing does not establish domestic Shanghai fulfilment. An indexed ICKey offer was not reproducible on the opened page and is not accepted as current stock evidence. **Neither replacement is marked purchased, selected or Shanghai-orderable.**

## Verification and next repair

`tools/run.py` runs KiCad 10.0.6 on temporary copies with resolved footprint-library paths. `tools/check.py` verifies source/report hashes, retained fixture connectivity, independent DC results and native pad geometry; four negative controls reject omitted nets, weakened rules, stale native files and a missing rule operand. All active native files remain byte-identical. See [checks](results/checks.json) and [DRC receipt](results/run.json).

Next: carry these constraints into the already approved common buffered loop/protection integration, then recompute actual connector and relay voltage envelopes. If tube-level interfaces remain, qualify an exact retained connector pair with Chinese stock/Shanghai delivery, drawings and insulated harness; then replace the footprints and reroute with net-pair rules. Do not enlarge connectors or overhaul the circuit merely to satisfy this blanket comparison. Final ground pour, all-board DRC/ERC, three-board populated chassis fit and actual tool access remain open.
