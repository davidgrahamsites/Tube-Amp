# Reverb current allocation and copper resistance screen

Owner: PCB integration. Date2026-11-25. Baseline f51f883bc0f1349bf8eb49079920280bc89a8f6e. This is a conditional load model and supply-planning correction, not an ampacity or tank-current approval. Native boards/schematics and functional blocks are unchanged.

## Inputs and method

The editable contract binds actual reverb-600 circuit values and pins, all three OPA2134PA packages and the reported76ohm tank input winding. Circuit and contract are SHA-bound; the canonical tank electrical-measurement object is hashed separately from unrelated cabinet dimensions. The six op-amp outputs are independently bounded ideal sine sources at10Vpeak, with an18Vpeak diagnostic comparison. The latter is not an achievable linear output specification. The150Vpeak FX_RETURN envelope is retained from VAL-067; it is not the rating of an external effects pedal.

The calculation includes send-pot loading, driver feedback and series-RLC tank loading, recovery feedback/filtering, wet-pot loading, steady mute loading, summing feedback, and the output coupling/mixer network. A two-node complex solve covers independent output/dry-source phases, with and without an additional1Mohm resistive phase-inverter load. This does not model nonlinear grid conduction. Output peak-current magnitudes are summed conservatively rather than assuming simultaneous phase cancellation or applying a half-wave average discount.

The seller's480/600/720ohm sensitivity cases at an assumed1kHz generate inductance surrogates; these are not measured coil inductances. C603 uses±5%; ordinary resistors use a2% low-value screen, R616 uses the retained93.8125ohm corner and pots80kohm. Tank DC resistance is reduced10% as an engineering sensitivity, not a measured cold rating. Sweep20Hz–20kHz with241 logarithmic points plus exact series resonance. Manufacturer quiescent allowance is6×5mA per rail under the [TI OPA2134 table conditions](https://www.ti.com/lit/ds/symlink/opa2134.pdf),25°C and±15V. It is not a guaranteed hot/startup/fault allowance.

## Results and design consequence

| Conditional output envelope | Each-rail allocation including R619/R620 | Excluding those separately budgeted rail loads | Driver output peak-load bound |
| --- | ---: | ---: | ---: |
| 10Vpeak | 69.725mA | 67.888mA | 35.721mA |
| 18Vpeak diagnostic | 99.925mA | 98.088mA | 64.299mA |

The old50mA working reserve is below this conservative10Vpeak screen. The auxiliary planning contract now allocates70mA per rail, with R619/R620 added separately. Its100mA expansion case covers the diagnostic load sum under these assumptions. Neither allocation is a verified maximum supply current over temperature or faults.

The forced ideal-source model produces tank-current bounds of24.898 and44.817mArms respectively near series resonance. **These are neither actual operating predictions nor permissible tank drive levels.** They cannot authorize raising the reverb send. Driver clipping/current limiting, magnetic behavior, recovery distortion and sample endurance are absent. R605 sine dissipation reaches0.134/0.433W in those cases; exact part selection, faults and thermal derating remain required. [Tank test plan](../../mechanical/review/tank-characterization-plan.md) owns the physical qualification.

All12 corners pass the independent resonance-current formula, source freshness, case coverage, current summation and wet-node allocation checks. The largest nodal residual is1.94e-18A/V. Four intentional corruptions are rejected. The computed wet-node bounds remain below20V for the linear clamp-off screen. Mute-contact capacitor-discharge pulses remain covered only by the separate VAL-067 assumptions; this model does not replace that pulse check.

## Auxiliary-supply rerun

The updated72-case raw-supply sweep and four half-step refinements complete. Its checker retains the immutable historical comparison and explicitly permits only the additional20mA working-profile allocation plus the previously documented cold-coil/R619/R620 deltas. It also verifies the70/100mA allocations against this current-budget artifact. Nine existing negative controls pass.

| Profile | Maximum half-winding RMS | Maximum conditional regulator heat | Cases with unresolved flags |
| --- | ---: | ---: | ---: |
| Idle | 0.11836A | 2.1262W | 12/24 |
| Working reserve | 0.24366A | 3.6297W | 6/24 |
| Expansion stress | 0.29678A | 4.2868W | 24/24 |

There are42 flagged cases overall. Fewer flags than the previous44 does not mean higher current improved the whole supply: increased load can reduce an excessive raw-voltage corner while increasing winding demand and heat. No transformer, regulator cooling, mains fuse or fabrication release is established. Current evidence is in [auxiliary results](../../aux-supply/results/loads/raw-screen.json) and its checks.json; older transformer/hold-up analyses remain historical and require refresh before adoption.

## Copper screen and remaining interface

At hypothetical minimum30micrometre finished copper,20% width loss and70°C copper, calculated drop per100mm at100mA is28.65mV for0.3mm drawn width,21.49mV for0.4mm,14.32mV for0.6mm and8.595mV for1.0mm. The material constants are linked in contract.json. These are R=ρL/A comparisons, not thermal-current ratings; they do not include actual routed lengths, necks, vias, zones or current sharing.

Next: qualify finished copper/thermal conditions, extend budgets to mains/heaters/HV/output/logic and new FX/expression circuitry, and apply widths with complete path/clearance checks. Scope also excludes hot IC current, decoupling pulses, short-circuit clearing and hardware tank limits. All-board current qualification, final three-board layout, populated cabinet fit and complete drill access remain open.

## Reproduction and human check

Run `python3 engineering/whole-amp/pcb-measured-r/current-budget/tools/analyze.py`, then its tools/check.py. Rerun `engineering/whole-amp/aux-supply/tools/screen_cold_loads.py` and tools/check_loads.py after changing the auxiliary contract. Generated evidence lives only in results/. Review the stated assumptions, actual current waveforms and hot-board voltage/temperature measurements before treating these allocations as manufacturing requirements.
