# Low-voltage resistor selections — November 15

Owner: parallel resistor sourcing task. Input: current coverage register, v0.5 control circuitry and v0.4 reverb circuitry. Output: exact part selections plus reproducible scoped voltage/power checks. No shared register or native CAD changed. This three-minute work package is complete; integration owner must apply the listed coverage IDs after review.

## Select these parts

| Groups | References | Exact Yageo part | LCSC SKU |
|---|---|---|---|
| P060, P072, P092 | R301,R311,R331,R341,R607 | MF0207FTE52-1K | C513706 |
| P062, P085 | R302,R312,R321,R322,R603,R604,R610 | MF0207FTE52-10K | C513672 |
| P073 | R332,R342 | MFR50SFTE52-100K | C173137 |
| P091 | R606 | MF0207FTE52-220K | C513655 |
| P096 | R609,R617 | MF0207FTE52-1M | C1373811 |
| P114 | R508,R509 | MF0207FTE52-100R | C513679 |

Nine groups, nineteen references, six exact part numbers. Some part numbers are already selected elsewhere in the amp; use existing purchase quantities before ordering more.

Supplier evidence is the existing November11 mainland signed-in catalogue observation in candidate-register.json, not a November15 stock refresh. For example C513706: MOQ50, RMB0.1337 each,8350 observed stock; C173137: MOQ20,RMB0.1432,2820 stock; C513679: MOQ50,RMB0.1271,11K+ stock. Other URLs, dated stock and price fields remain in that register. Recheck availability at order time.

## Rating and footprint basis

Manufacturer documents already saved as evidence/Yageo-MF0.pdf and evidence/Yageo-MFR.pdf were reviewed, including power/voltage table, derating curve and body dimensions. MF0207:0.6W at70C,350V maximum; MFR50S:0.5W at70C,300V maximum. Both derate to zero at155C; working voltage is also limited by sqrt(P×R). Nominal body6.3±0.5mm by2.4±0.2mm, leads0.55±0.05mm. Prepared Yageo_MFR50S_MF0207_P10.16 footprint is suitable as the planned formed-lead geometry; this is not evidence that supplier leads arrive preformed. No PCB routing changed.

## Checks and limits

Run `python3 engineering/component-selection/check_lv_resistors_2026_11_15.py`. Machine result: lv-resistor-selection-2026-11-15.json. Nine envelope checks pass at1% low resistance and100C local ambient; maximum utilization66.61% for R607 with16V continuously applied. This is deliberately more severe than its normal feedback-node voltage. It is not a whole-amp simulation.

- Control resistors:5.5V terminal-difference bound, including a sustained gate short for the1k gate resistors. Source wiring is engineering/updated-schematic/tools/build_design.py, controller and latch/driver sheets. Cable transients, accidental external voltages and ESD remain separate.
- Reverb10k resistors:32V differential bound for nominal±15V rails, allowing±16V. R606 is grounded at one end, bounded16V; R607 likewise grounded. R609/R617 use32V bound. This exceeds the current ideal-transformer candidate mix peak13.5V, but does not qualify a failed tube coupling capacitor or arbitrary external effects return. See engineering/solid-state-reverb/tools/simulate_reverb.py for connectivity. Reverb interface revision and actual rail behavior must remain within these limits.
- Heater midpoint resistors: assumed transformer heater differential no greater than8Vrms; with1% divider mismatch, each resistor at most4.04Vrms. Conservative power calculation uses this maximum with99ohm,0.1649W. The100C allowable is0.3882W. Actual heater transformer no-load/high-line output remains to be confirmed. Common-mode elevated heater voltage does not appear across each midpoint resistor during normal operation; insulation to adjacent nets is a separate layout check.

Require local ambient at or below100C for this selection envelope. Real enclosure thermal measurements, lead forming, native footprint integration and startup/fault review remain open. Do not extrapolate this low-voltage choice to HV plate resistors.

## Deliberately not selected in this pass

P079 bundles R601 and R612 with other100k reverb resistors. Proposed send/mix revision changes or removes those references; do not select the entire stale group. R605220ohm driver isolation and R616100ohm output isolation need actual current/short/transient checks; a simple full-rail voltage bound exceeds these small-package power ratings. These are not silently approved. Exact pedal-control circuitry remains separate.
