# Panel connector migration — 24 November 2026

The ten panel pots now have a reproducible, circuit-derived migration schedule covering all thirty terminals. Nine stay with Main and one with Reverb. This closes the mapping audit, not physical connector integration. The existing Main board still uses individual wire pads; JR4 remains a generic three-pin header. Neither implements the proposed ten locking connectors.

Two existing circuit nets, `CL_TREBLE_W` and `DR_TREBLE_W`, occur only between panel pots and have no Main-board pad. If each pot is to have its own PCB plug, the board needs to carry these two connections. They are not new circuit functions or proof that the original off-board circuit was disconnected. Preserve RV2/RV6 terminal 1–2 links and RV7/RV9 terminal 2–3 ground links. Do not discard a terminal merely because its net repeats.

`results/pot-connectors.csv` is the handoff to schematic/PCB integration. Its cavity assignment is electrical intent, not a verified mating-face drawing. Cavity 4 remains unassigned. The other Main wire pads serve many unrelated interfaces and must not be removed wholesale. Integration must replace the relevant wire interfaces, add explicit connector symbols and restore endpoint/netlist parity before routing; no direct field-wire-to-PCB-pad soldering is accepted for the finished build.

## Candidate geometry and assembly

The [Molex family drawing, SD-43045-001 H1](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/430/43045/430450400_sd.pdf) includes the gold 430450402 variant. Its nominal pattern agrees with the installed KiCad horizontal footprint: four round 1.02 mm plated holes on a 3 mm grid and a round 3 mm nonplated locator hole. Both hole diameters have a drawing tolerance of ±0.05 mm. The drawing also limits placement relative to the board edge to avoid interference with the mate. Those are finished-hole/placement requirements, not permission to accept the fabricator's default tolerance. A round hole can be appropriate for a non-round lead when the manufacturer specifies it; changing it to a slot merely because the pin is square would be wrong.

This pass read drawing text and inspected native library dimensions. PDF visual retrieval failed; the exact edge datum, full pin tolerance, component-side numbering, mate/extraction space and fabricator capability still need confirmation. No footprint was adopted, no drilling files released, and no inferred 3D envelope used. The [housing drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/430/43025/430250400_sd.pdf) identifies its cavity-1 marking and requires fully seated contact lances. Physical harness inspection must verify these.

## Wire and crimp correction

The [Molex tooling specification ATS-638190000 revision G](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/638/63819/ATS-638190000-001.pdf) explicitly includes loose gold contact 430300008 and tool 638190000. For this contact/tool combination, insulation diameter is **1.42–1.85 mm**, not simply “at most 1.85 mm.” Its 20/22/24 AWG scope and 2.54–2.92 mm strip range must also match the actual wire. For 24 AWG, the reference conductor crimp-height range is 0.83–0.93 mm and the pull-force threshold is 22.2 N, excluding insulation-crimp contribution; the document requires exceeding that minimum. Reference geometry alone does not qualify a particular strand construction or insulation hardness.

This resolves published tool applicability, while actual wire, tooling availability and sample qualification remain open. The earlier nominal 1.60 mm FEP wire lead is only a candidate until its OD limits and exact construction are known. Do not substitute thin 24 AWG wire on gauge alone, or add solder to rescue an unsuitable crimp. High-impedance runs also need cable capacitance/length checks to protect the requested treble response.

## China procurement evidence

The complete proposed gold set remains header 430450402, housing 430250400 and contact 430300008. Ten harnesses need ten headers, ten housings and thirty signal contacts before spares; no shield contacts are yet assigned. Existing catalogue references remain candidates, not stock guarantees.

The [domestic tin-header listing](https://item.szlcsc.com/123682.html) identifies 430450400/C122413. The [domestic housing page](https://item.szlcsc.com/123686.html) returned an anti-bot response. The [LCSC tin-contact listing](https://www.lcsc.com/product-detail/Line-Pressing-Terminals_MOLEX-430300007_C293530.html) identifies C293530 and a five-piece order multiple, but the search crawl is two months old. This adds the exact contact source lead for the tin alternative, without proving current mainland stock or Shanghai delivery. Never mix that contact into the gold set as an unreviewed substitution.

No order was placed. Current domestic quantity, exact wire, acceptable crimp service/tooling, delivered RMB price and Shanghai dispatch remain purchasing gates. The generic “custom cables MOQ 1” advertisement is not a quote for this harness.

## Checks and next action

KiCad native read: ten pots/thirty assignments match the circuit; two existing off-board-only nets identified; all four native board hashes unchanged. Five candidate footprint holes match nominal shape/type/position. Three mapping negative controls reject a swapped net, an implicit shield ground and an omitted repeated-net terminal; wire controls reject insulation below/above the tool range and an unsupported gauge. These are scoped engineering checks, not ERC/DRC or physical assembly tests.

Next: choose the exact insulated cable and obtain full drawing/cavity/mating-envelope evidence; then integrate the connectors into readable schematics and the populated three-board layout. Keep maximum fault voltage, wrong-plug prevention, clamp positions, rear-panel independence and the 46 mm chuck plus still-missing body/bit envelope in that review. No additional drill measurement is inferred from its photo.
