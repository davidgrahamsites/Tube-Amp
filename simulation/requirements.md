# 220 V / 50 Hz refactor and simulation contract

Required by the user October 4, 2026. Applies to the first working prototype and its later revisions. This document specifies work still to perform; it is not a passing simulation report.

## Revision and part identity
First capture a reconciled netlist of the [original source](../sources/original-ppt/inspection.md), with source-value/reference mapping and unresolved items. Simulate that baseline to expose its operating conditions before changing topology. Treat original Hammond parts as reference identities; the original 272FX is specified for 115 V / 60 Hz and is not an eligible direct mains choice.

Select actual build components against the complete electrical load budget, cabinet geometry, delivered Shanghai cost and available evidence. A main transformer and a separate or integrated relay/control supply must both support the required input and frequency. Added reverb heater/HV loads, bias supply, lamps and relay/logic consumption are part of the budget. Do not scale all internal voltages by the mains ratio or preserve a legacy fuse value without calculation.

For each simulated part, record manufacturer, exact part number/revision, datasheet, model origin/date/hash/license, model pin order versus actual pin numbers, tested operating region and known omissions. Manufacturer models are preferred where suitable. Tube-family models must be compared with the chosen tube's curves and ratings; a generic 12AX7/EL34 model is not automatically a validated model of every marketed version. Transformer models need winding ratio, winding resistances, current/regulation, inductance/leakage/coupling and saturation information to the extent each claim depends on them. Unknown parameters require bounds and sensitivity analysis, followed by measurement.

Resistors/capacitors need actual values, tolerances and ratings; include ESR/leakage/temperature effects where material. Check diodes, relays, drivers and logic against actual operating/stress conditions. A spring tank electrical impedance model does not establish acoustic decay, rattling, feedback or mounting performance. Where no exact model exists, document and justify a bounded surrogate; preserve the pending physical checks.

## Required analysis packages
| Package | Inputs and checks | Deliverable |
|---|---|---|
| S01: baseline | Reconciled original topology, known reference parts, supply/load assumptions, valve-half/pin mapping | Operating points and reference response, source conflicts resolved or explicitly blocked. |
| S02: mains/supplies | Selected 220 V / 50 Hz transformers and rectifiers, HV/heater/bias/control loads, filters and protection | Rectified/filter voltages and ripple, regulation, charging currents, component stress, bias range, startup/shutdown sequencing and ratings review. |
| S03: audio | Chosen tubes, bias conditions, controls and phase inverter/output transformer/load | DC operating points, AC gain/frequency response, clipping/headroom, delivered output/distortion under stated conditions and feedback/stability analysis within model limits. |
| S04: reverb | Driver/recovery tubes, matching transformer, selected tank electrical model and dry/wet interfaces | Drive limits, recovery gain/noise estimates, mix loading/polarity/headroom and reverb-off behavior; separate acoustic test plan. |
| S05: control | Chosen supply, logic, switch/input networks, relay drivers/contacts and interface rules | Bounce tests, startup/reset, jack plug/unplug, supply dips, coil/flyback stress and analog switching transients within model bandwidth/coverage. |
| S06: integrated revision | Frozen schematic/BOM/model revisions and all block interfaces | Combined load interactions, ripple coupling, startup/shutdown, intended operating corners, defects/changes/retests and release review. |

Use DC operating point, AC, transient and sensitivity/tolerance analyses as relevant. Establish numerical acceptance limits before interpreting results. Include 198/220/235.4 V at 50 Hz as normal supply-boundary/nominal cases: Article 57 of the [2024 China supply rules](https://zfxxgk.ndrc.gov.cn/wap/iteminfo.jsp?id=20347) specifies +7%/−10% normal single-phase deviation, with stated qualifications. Retain 242 V as an additional engineering high-line stress case, explicitly separate from that normal upper boundary. Declare the chosen equipment's intended operating envelope and other transient/fault cases from applicable requirements and part evidence; the supply regulation alone does not establish appliance qualification. Load states include idle, intended rated output, both channels, reverb enabled/disabled and relay transitions. Derive component tolerance/temperature corners from evidence. Simulated faults are modeled cases and do not substitute for physical protective testing.

## Reproducibility and release gate
Every run stores the native netlist and included models, input hashes, chosen-part/BOM revision, solver version/options, commands, convergence/error log, raw waveforms and extracted metrics with units. Treat a converged run separately from a circuit meeting requirements. Track all approximations and failed cases. Changes to parts, supply conditions or layout-sensitive parameters trigger affected reruns and review.

S01–S06 evidence and its limitations must be reviewed before releasing prototype PCB/fabrication files. Layout review must separately assess parasitics, grounding, creepage/clearance, heat and magnetic coupling; the bench phase must check modeled predictions. Missing model evidence can block a performance claim even while unrelated design work continues.

## Current state
Original-source intake is complete. Actual build-component selections, a native baseline netlist and matched model set are pending. KiCad's bundled shared ngspice **45.2** was qualified through its native Python on arm64: a DC divider and transient RC response agreed with analytic values. See [qualification results](qualification/result.json) and [VAL-004](../brain/records/VAL-004-ngspice-qualification.md). This qualifies the tested solver/interface route separately from the amp's simulation. No selected-component amplifier run is claimed yet.

References: [ngspice model guidance](https://ngspice.sourceforge.io/modelparams.html), [official shared-library interface](https://ngspice.sourceforge.io/shared.html), and the [Circuit Design Skill Ladder](/Users/appleadmin/.codex/skills/circuit-design-skill-ladder/SKILL.md).
