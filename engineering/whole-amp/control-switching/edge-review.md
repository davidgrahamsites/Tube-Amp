# Reset-edge repair — November 24

U1C and U1D, two unused gates in the existing socketed SN74HC14N, now condition
the supervisor output before both HC74 clear inputs. Two inversions preserve
active-low reset. This stays inside the control functional block and adds no IC.
The original TPS3808G50 remains installed in the native draft; its replacement
and removable carrier are **not qualified**.

## Electrical evidence

R321 = 10 kΩ and a 50 pF load give a first-order 10–90% rise of 1.099 µs.
That exceeds the HC74 500 ns input-transition limit at 4.5 V. The
[SN74HC14 datasheet](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf), switching
characteristics and §8.2.1.2, permits slow input transitions and bounds the
output transition at 19 ns with 50 pF at 4.5 V over −40…85 °C. The two-gate
propagation bound is 62 ns under those test conditions. The
[SN74HC74 datasheet](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf) gives 10 pF
maximum input capacitance: two clear inputs leave a **30 pF budget** for output
trace/socket capacitance within the 50 pF test load. This is a budget, not an
extracted or measured capacitance. Qualification must cover the actual supply
range, startup, brownout, and reset release coincident with a clock edge.

The [TPS3808 datasheet](https://www.ti.com/lit/ds/symlink/tps3808.pdf) specifies
G50 nominal threshold 4.65 V. A conservative full-temperature combination of
2% threshold error and 2.5% hysteresis reaches 4.862 V, above the 4.75 V low rail.
Edge conditioning does not repair that threshold margin. The TPS389001 candidate
in review.md remains unadopted; its endurance/noise margins need further work.

## Why the manual-reset simulation failed its timing check

The original TI SLVMBN4 model hash is retained unchanged. Its `MR_OUT` gates
the output through `X_U34`, but CT charging/discharge is controlled by
`SENSE_CT`; MR does not discharge CT. The fine-step run consequently releases
RESET essentially at the MR rising edge. The
[TPS3890 datasheet](https://www.ti.com/lit/ds/symlink/tps3890.pdf), §§8.3.1–8.3.2,
requires CT discharge and a new delay after MR. This is a documented model
limitation, **not proof that the actual supervisor fails**. No vendor-model
patch or fabricated passing trace is used. The model also uses 1.19 µA CT
charging and finite switch leakage; its startup delay is not a guaranteed
datasheet corner. Fast-collapse and physical MR timing remain bench gates.

## Native change and verification

`edge-contract.json` declares six pin changes and the two existing gate-unit
sheet moves. `tools/integrate_reset_edges.py` creates the initial guarded change;
`tools/finalize_reset_edges.py` consumes the editable `edge-routes.json` and
finishes routing/presentation. Do not rerun these on the adopted revision.
`tools/check_reset_edges.py` independently compares source, exported net graph,
pad mapping, old copper and geometry, layer-aware route continuity, 45°/orthogonal
segments, minimum 0.3 mm width, ERC, DRC and Excellon drill changes.

27 new tracks and one 0.4 mm via complete five reset links. All old tracks and
component/mounting holes are preserved. Excellon rounds the new via X coordinate
27.7175 mm to 27.717 mm at its exported precision. The existing 13 Control DRC
violations remain; unconnected items fall from 84 to 79. The existing one ERC
finding remains. Missing-link, incorrect-via-drill and wrong-net negative
controls are rejected. These are scoped checks, not a complete PCB approval.

Final native PDFs show the local U3 → U1C → U1D chain and named connection to the
two latches. Raw/interstage net labels use short stubs so lettering does not sit
on wires. Power-unit labels were moved clear of pin labels. Review whole pages
and the dense reset region together; hierarchy and block identity are unchanged.

Next: qualify the supervisor and keyed carrier, reserve the measured logic load
and extraction space, and resolve the three-board populated chassis. No
fabrication release; drill-tool envelope stays deferred until November 25.
