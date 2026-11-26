# Reverb rail-load integration — 25 November 2026

R619 and R620 now provide a defined 10 kΩ load from each local audio rail to ground. This adopts the narrow correction selected in [VAL-063's injection screen](../input-clamps/review.md). The audio signal path, functional blocks and external interfaces are unchanged. R601 remains 1 MΩ; its selected part, rating and footprint now agree in the source, schematic and PCB.

## Parts and native change

R619/R620 use Yageo MF0207FTE52-10K, domestic LCSC SKU C513672. The [Chinese listing](https://item.szlcsc.com/528499.html) matches the exact identity; its public page did not establish fresh stock or a delivered Shanghai order. The prior 11 November stock/MOQ/price observation remains dated evidence, not a current quote. Both references share the existing selected 10 kΩ purchase group. No purchase or supplier message was made.

The [manufacturer MF0 datasheet hosted by LCSC](https://atta.szlcsc.com/upload/public/pdf/source/20241025/0CD0A2F58C0737235B910632046DA29F.pdf) specifies MF0207 at 0.6 W through 70°C, derating to zero at 155°C, and a 350 V working limit subject also to √(P×R). R601 is MF0207FTE52-1M. Body dimensions are 6.3 ±0.5 mm × 2.4 ±0.2 mm; round leads are 0.55 ±0.05 mm. The 52 suffix describes axial tape spacing, not a preformed 10.16 mm board pitch. Assembly requires forming the axial leads without stressing the body.

The existing exact-family footprint supplies 10.16 mm pitch, 0.8 mm round plated holes and 1.6 mm pads. Under a **provisional**, unconfirmed ±0.1 mm finished-hole tolerance, the smallest hole is 0.7 mm versus a 0.6 mm maximum lead: 0.1 mm diametral insertion allowance. R601's original pad positions and holes are unchanged. This is a package-fit screen, not acceptance of a fabricator's process.

R619 is +15V–GND and R620 is GND–−15V. Ten new 0.3 mm, horizontal/vertical/45° trace segments connect them beside C616/C617, returning to the local supply-capacitor ground. Existing 411 segments, arcs, vias, board settings, mounting holes and all other footprints are preserved. The JR6 pin-order legend moved to remain readable. These added low-current branches do not establish current capacity or voltage spacing for the rest of the board.

## Checks and readable drawing

[Native checks](results/checks.json) compare the captured ba3c80d baseline with fresh KiCad exports:

- 236 existing component identities and all 144 net partitions preserved, apart from exactly the four added resistor endpoints. Source-to-native parity independently maps 238 components and 617 connected pins.
- ERC retains one existing GND/PE bond-label finding; Reverb reports zero DRC findings and zero unconnected items **under its existing rules**. This does not approve its high-voltage interface clearances.
- All 138 prior drill hits are unchanged; exactly four 0.8 mm round PTH hits were added.
- Seventeen schematic pages are pixel-identical. Page 13 and its local supply detail were inspected: direct parallel supply branches, clear resistor references and no new label/wire collision. R601's page changes only hidden metadata.
- The declared ground/earth connection still passes an independent cut-wire negative control. It is logical topology evidence, not a physical bonding test.

The first two trial route DRC reports are retained as failures. The final route resolves those new collisions. Other three boards are byte-identical to the baseline. No copper zone has been adopted.

## Added load and supply regression

Each resistor takes 1.5 mA / 22.5 mW at 15 V. The explicit 18 V, −2% resistance allocation is 1.836735 mA / 33.061 mW each; it is included in the canonical [load contract](../../aux-supply/load-contract.json), cold-load screen and future hold-up factory. The 2% allowance combines initial tolerance and an engineering drift allocation; it is not an arbitrary claim of every-temperature performance.

The current 72-case supply screen plus four half-step repeats complete. Independent current accounting, deck hashes and nine corruption controls pass. **44/72 cases retain unresolved engineering flags.** These are conditional winding/regulator-range failures, not simulator failures:

| Load profile | Maximum half-winding RMS | Maximum conditional regulator heat |
|---|---:|---:|
| Idle | 0.11836 A | 2.1262 W |
| Working reserve | 0.21381 A | 3.3000 W |
| Expansion stress | 0.29678 A | 4.2868 W |

These values belong to the existing generic cold-load envelope, not the separate 50 VA candidate's complete thermal rating. Both remain unqualified supplies.

The separate [32-case loaded brownout regression](results/supply-regression.json) reuses VAL-054's unadopted 50 VA/6800 µF source and fast-clamp/monitor candidate. It adds only the new resistor allocation to the retained decks, avoiding double-counting prior loads. All sampled conditional timing/healthy-enable checks pass: minimum timing reserve **0.38320 ms**, minimum healthy-enable margin **150.324 mV**. Repeating the limiting case at half timestep changes reserve by about 1.1 ps. [Independent checks](results/supply-checks.json) validate case identity, load insertion, reserve arithmetic, deck/source hashes and corruption controls.

The small timing reserve is not a guaranteed mechanical relay margin. Source-only supply models, assumed contact latency, reference/logic validity and constant extra current until first headroom loss remain assumptions. The constant-current approximation is not physical after dropout. Native protection/control still does not contain that candidate. Earlier raw/hold-up results remain historical and must not be represented as current-source runs.

## Remaining gate and next action

Next derive and implement voltage-domain rules and connector constraints for the tube-level JR1/JR5 interfaces before any broad ground pour. Actual clamp behavior, capacitor discharge/inrush, full supply sequencing, exact transformers, socket/contact heat, Shanghai checkout, populated three-board fit and complete drill-body/bit access remain open. All six build scopes remain incomplete; this correction is not a fabrication release.

For future block datasheets, record the extra current separately from IC operating load, include the conditional injection envelope and distinguish simulation from measured fault behavior. Preserve this narrow change when the physical boards are repacked.
