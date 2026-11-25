# Debounce capacitor input-current repair — VAL-056

R304/R314 (10 kΩ) are now between C301/C311 and U1 inputs 1/3. The 15 kΩ debounce resistors remain before the capacitors. This changes only the controller input interface; the functional blocks, sockets, other components and mounting holes stay intact. The two added output traces use 0.30 mm copper and 45-degree bends. The capacitor-to-resistor routes remain among the existing unfinished connections; this is not a routed-board release.

## Evidence and scope

Native baseline: `9f4b43c40dd317c6ee52940cebd228ac4af1d28c`. The guarded factory `tools/integrate_debounce_inputs.py` owns this bounded repair; do not regenerate the native sheets from an older whole-project generator. The source circuit, one schematic sheet and Control PCB change together. Its retained local IPC nominal footprint has two 0.80 × 0.95 mm surface-mount lands on 1.65 mm centers; no drill holes are added. Manufacturer body envelope is 1.60 ±0.10 ×0.80 ±0.10 ×0.45 ±0.10 mm. The footprint is an IPC nominal selection, not a claim that Yageo specified this exact land pattern. Assembly process and populated fit still need review.

Native XML comparison checks the complete pin partitions and all prior component metadata. Exactly two old capacitor/input nets are split by the new resistors. Twenty other native files are byte-preserved; all prior Control footprints, copper, vias, outline and holes are preserved except the declared U1 input net names. Native ERC remains the same one existing finding; Control DRC remains the same 13 existing findings and 79 opens. Initial trial had six minimum-width findings and one clock-trace clearance finding; the final 0.30 mm routing removes all seven new findings. No historical validator is silently rewritten to accept new CAD hashes.

The full changed sheet and both enlarged input regions were inspected after the final annotations. The local paths are visibly connected, labels and notes clear. Other sheets were not rearranged and their hashes are unchanged. This is a scoped visual gate, not a new all-project readability signoff. Final artifacts are in `results/debounce-input`.

## Electrical screen

[TI SN74HC14 Rev L](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf) specifies ±20 mA input-clamp and ±50 mA VCC/GND absolute-maximum currents. With an initially 5.25 V capacitor, zero clamp voltage and a 9.8 kΩ minimum series resistor, each path is bounded by 0.536 mA; the two together by 1.072 mA. Resistor dissipation is at most 2.813 mW. These are bounds under the stated supply assumption, not an ESD or cable-surge rating. Operating below 2 V is not guaranteed by the logic datasheet.

The 1,536 passive timing cases cover local and pedal contacts, 4.75/5.25 V, existing resistors ±1%, 1 µF ±20%, series resistors ±2%, 10/50 pF input capacitance including socket/trace, ±1 µA leakage, and the conservative 4.5/6 V datasheet threshold envelope. Maximum response-time change is 0.5953 ms. Eight independent ngspice transient witnesses (four cases at two timesteps) agree with the exact two-pole calculation within 0.040 ns. This tests the passive network; it does not model bounce, HC14 below-rail behavior or prove the original debounce guarantees. The ±20% capacitor and ±2% series-resistor ranges are engineering screening allocations, not newly guaranteed lifetime limits.

The previous candidate reference/timer backfeed bound of 0.579 V covers only those new paths. Adding these two native capacitor paths gives a loose simultaneous bound of 1.576 V with the existing worst-case preload. Therefore the 0.65 V engineering screen is not met for the combined network. Whole-board power sequencing remains unqualified. The series resistors repair the unbounded direct capacitor-to-input paths; they do not prevent phantom power.

## Exact sourcing

R304/R314: Yageo **RT0603BRD0710KL**, Chinese LCSC **C95204**, [exact listing](https://item.szlcsc.com/96405.html). The November25 VAL-055 observation records stock492851, minimum-buy field1 and conversion field20; these fields are retained without claiming a one-piece delivered quote. The listing identity/specification was rechecked for this repair. Manufacturer evidence is the retained `evidence/Yageo-RT-2026.pdf`, version17, February12,2026. The existing domestic courier route supports Shanghai; checkout, final quantity/price and stock reservation are not verified. No purchase/contact/upload occurred.

## Remaining work

C301/C311 already differ between native schematic (generic 3.5 mm radial footprint), source circuit (empty footprint), and board (KNSCHA 5 mm film footprint). This repair preserves that pre-existing mismatch and makes it an explicit next reconciliation task. Confirm exact capacitor BOM/datasheet and synchronize those artifacts before fabrication. Complete reference/logic/relay power sequencing, exact removable parts, remaining routing, three-board integration and populated chassis/tool access. All six through-chassis scopes remain open.

Human check: scope C301/C311, U1 inputs, +5 V and relay gates during abrupt power loss, slow brownout and held/released buttons; verify no unwanted toggles or relay pickup. Verify 50 pF input and thermal assumptions on the socketed assembly.
