# Shared reference and logic-input interface

Owner: control-switching integration. Baseline: df749d243e9f8d8a1a15ad50ffafe130f597329b. This checkpoint combines the precision rail monitor, AC-loss detector, raw warning and delay interfaces. Estimated effort: one bounded interface review. Outputs are a candidate connection contract, reproducible calculations and independent checks; native adoption is a separate gate.

## Repair candidate and findings

Keep all comparator feedback on **RAIL_OK**. Feed U1E pin 11 through a **10 kΩ series resistor**, with **100 kΩ from the input to ground**. This limits backfeed and keeps the powered input within the logic supply. Feed U1F pin 13 through **49.9 kΩ**, keeping the delay capacitor and its discharge transistor on the original DELAY node. Retain the separate trial's 6.8 kΩ REF5 bleeder.

The first trial used 10 kΩ at both inputs. Its combined new-path backfeed bound raised an otherwise unpowered 5 V rail to 0.986 V through the existing R215 preload. Increasing the delay-input resistor reduces this bound to 0.579 V. The initial 47 kΩ sourcing candidate had zero stock, so the calculation was rerun for an available 49.9 kΩ part. Neither trial changes the native files.

The **native** audit also found C301 and C311, each 1 µF, directly connected to U1 inputs on DB_CH and DB_REV. Their existing 15 kΩ resistors are on the button side of the capacitors; they do not limit capacitor discharge into the IC's input clamp. These two paths still need explicit input current limiting and debounce/threshold verification. They are not included in the new-path phantom-supply bound. No whole-board power-off claim is made.

## Evidence

| Check | Conditional result |
|---|---:|
| Loaded RAIL_OK minimum | 4.750 V |
| Logic high minimum / powered maximum | 4.292 V / 4.586 V |
| Logic low maximum | 0.512 V |
| Passive reference-off input maximum | 0.720 V |
| Conservative reference load | 9.921 mA, below the 10 mA allocation |
| Comparator sink bound | 3.498 mA, below the 4 mA test condition |
| Delay release over 192 allocated corners | 51.882–923.566 ms |
| Minimum hold after a full 2 ms fault | 50.549 ms |
| New-path injection into the logic rail | ≤0.512 mA and ≤0.110 mA |

Four passive-network SPICE solutions independently match the matrix solutions. Six independent RC integrations agree within 7.45 ns. Three corrupted-evidence controls are rejected. All 91 previously captured native/source CAD identities are unchanged. The old brownout reserve becomes approximately 0.475 ms after allowing for the new first-input settling; it remains thin and conditional on the unverified relay/contact allocation.

The zero-drop input-clamp bound is deliberately conservative. The 0.65 V phantom-rail limit is an engineering screen, **not** a claim about HC74 outputs or MOS gate states below their operating supply. The 50 pF input-capacitance and 2% resistor allocations require layout/component verification. Reference-off analysis omits shunts that would reduce backfeed, but does not claim a complete semiconductor startup model. Physical relay closure, reference startup and every native injection path remain separate gates.

## Sources and procurement

[TI SN74HC14 datasheet](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf), sections 5 and 7.3.3, explicitly shows input clamps. The [TI REF50 datasheet](https://www.ti.com/lit/ds/symlink/ref50.pdf) supplies the reference current limit. Original TI PDFs were already retained in this module.

The retained [Yageo RT family datasheet](https://yageogroup.com/content/datasheet/asset/file/pyu-rt_1-to-0-01_rohs_l), version 17 dated February 12, 2026, documents the selected 0.1%, 25 ppm/K family and test conditions. The 2% total screen is not a blanket service-life guarantee or a sum of every separate environmental test.

November 25 Chinese LCSC observations: [10 kΩ C95204](https://item.szlcsc.com/96405.html), stock 492851; [49.9 kΩ C705780](https://item.szlcsc.com/742300.html), stock 104688; [100 kΩ C122538](https://item.szlcsc.com/123807.html), stock 1089142. Each page reports minimum-buy field 1 and conversion ratio 20. Exact manufacturer suffixes, raw fields and hashes are in source-observations.json. Domestic courier policy supplies a Shanghai purchasing route; delivered prices and stock are not reserved. No purchase or supplier message.

## Next action

Repair the two native debounce input paths, rerun their button timing and supply-collapse checks, then consolidate the candidate into a readable control schematic with explicit reset priority and exact removable carriers. Preserve the existing blocks. Adopt the complete change only with netlist, ERC, DRC and mechanical checks. All six build scopes remain incomplete.
