# Four-board requirements audit — 21 November 2026

**Result: FAIL for fabrication release on all four active boards.** The audit is complete as an evidence and gap review. Engineering verification is not complete. No native CAD, project rule, schematic, part selection or circuit was changed by this audit. No new simulation or physical test is claimed.

Owner: PCB integration. Circuit, parts and mechanical owners close their respective findings before PCB release. Revision: electric 600R-1, starting at commit 8382b4c; exact native inputs are identified in [run manifest](requirements-run.json). Historical boards and the future acoustic design are excluded from active release; their prior results do not qualify these boards.

## Method and coverage

- Fresh KiCad 10.0.6 DRC on each active board with all severities, all track errors and zone refill.
- A second run on temporary copies enabled every ignored check and cleared exclusions. Absolute library paths were retained. Active source hashes remained unchanged. Strict reports refer to temporary paths; the manifest links them to source hashes. This did not relax active rules.
- Native inventory of every footprint, pad/net, wire interface, model presence, copper zone, rule and stackup declaration. Circuit contract: `reverb-600/circuit.json`. Historical board plan was used for ownership and terminal coverage, not as a current electrical rating authority.
- Read-only copper widths/lengths/vias and joined-segment bend screening. Pad, via and branch junctions remain separate from simple-bend screening.
- Visual inspection of fresh exports of both copper layers with front fabrication/silkscreen and board edges. Reviewed Main, Power, Control and Reverb at 1800-pixel width. These are audit views, not Gerbers or a populated assembly inspection.
- All **364 imported rules** mapped individually to the 20 established review groups, with disposition, source line/hash, evidence, closure requirement and owner. [Rule matrix](requirements-matrix.csv), [group assessments](requirements-groups.csv), [coverage manifest](requirements-coverage.json). A rule may span several groups. First lines identify rules; the original full text remains authoritative.

`FAIL` means an evidenced defect or missing required implementation. `NOT_VERIFIED` means available evidence cannot establish the whole requirement, even where a narrower check passes. `NOT_APPLICABLE` has an explicit topology reason and must reopen if topology changes. `SUPERSEDED` applies to the obsolete added-reverb-tube instruction only. No blanket pass is inferred from a clean DRC or a checklist entry.

## Board results

| Active board | Outline, mm | Circuit refs / all footprints | Native DRC violations | Unconnected items | Additional strict findings | Simple bends over 45.1 degrees |
|---|---|---|---|---|---|---|
| Main | 290 × 140 | 56 / 103 | 0 | **105** | 43 missing wire-pad courtyards | 1 |
| Power | 160 × 175 | 27 / 43 | 0 | **39** | 12 missing wire-pad courtyards | 1 |
| Control | 230 × 110 | 55 / 72 | 0 | **99** | 13 missing wire-pad courtyards | 1 |
| Reverb | 160 × 100 | 46 / 50 | 0 | 0 | 0 | 0 |

The 243 unconnected items are DRC connection items, not a count of missing nets. Sources: `*-drc.json`, `*-strict-drc.json`, [native inventory](native-requirements-facts.json), [copper inventory](copper-audit.json). All four have two copper layers and zero copper zones. Missing 3D models: Main 93, Power 33, Control 39, Reverb 31. A missing model is an assembly-evidence gap, not proof of physical interference.

## Findings and required repairs

### F01 — Routing incomplete; parity evidence narrower than release needs

Main, Power and Control remain incomplete after earlier package changes. Their sparse copper is also evident in the fresh renders. Zero spacing violations does not close 243 unrouted connections.

The exhaustive contract check finds **no pad/net errors** in 184 circuit references. All 68 one-pad wire interfaces match their planned names, pad numbers and nets. All 46 circuit references absent from the four boards are accounted as chassis/off-board parts; none is silently omitted. Four mounting holes per board are non-plated 3.2 mm holes. Repeated H1–H4 references are board-local mounting identifiers, not duplicated electrical parts.

There is no paired `.kicad_sch` beside these board files, so native schematic-to-PCB parity was **not run**. Contract mapping does not prove current exported integrated schematic parity, assembly harness continuity, component behavior or physical pin numbering on a purchased part.

Closure: reconcile the current integrated schematic export and board/interface contract; freeze placement against exact packages and assembly; route all intended connections; run native DRC and complete parity again. Preserve off-board tubes, transformers, pots and connectors in the harness/assembly register.

### F02 — Local bypass placement and loop geometry need rework

Control components are spread across rows instead of complete device/support clusters. The following are straight-line distances between the IC rail pad and the nearest 100 nF or 330 nF capacitor pad on that rail with a GND terminal. They are **lower bounds**, not routed path lengths or proof of correct return routing.

| Board / pad | Nearest qualifying capacitor | Distance, mm |
|---|---|---|
| Control U1 pin 14, +5 V | C353 | **72.928** |
| Control U2 pin 14, +5 V | C353 | 23.244 |
| Control U3 pin 6, +5 V | C353 | 23.742 |
| Control U4 pin 3, +12 V | C205 | **145.500** |
| Control U5 pin 1, +12 V | C205 | **154.893** |
| Control U6 pin 3, +15 V | C210 | 69.817 |
| Control U7 pin 3, −15 V | C213 | 43.852 |
| Reverb U10 pin 4, −15 V | C611 | 18.407 |
| Reverb U12 pin 4, −15 V | C615 | 15.412 |

U1 and U3 placement conflicts with their manufacturers' close-bypass guidance. The regulator capacitor clusters also require exact-device layout/stability review. Reverb has visible long rail/return runs and an extended recovery feedback region around U11, R607/R608 and C605. Its completed routing does not establish low inductance or noise immunity. Do not set an invented universal maximum distance; use each device's layout requirements and the complete loop.

Primary sources inspected for this audit: [TI SN74HC14, sections 8.3–8.4](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf), [TI TPS3808, section 8.4](https://www.ti.com/lit/ds/symlink/tps3808.pdf), [TI OPA2134, sections 7.3–7.4](https://www.ti.com/lit/ds/symlink/opa2134.pdf). These require nearby supply bypassing and appropriate compact layout. A capacitor value alone does not qualify its placement. The distance screen includes rail-tied logic inputs as well as supply pins in raw evidence; the table above selects supply pins deliberately.

Closure: place bypass parts at their device supply/return pins, group each regulator with its required input/output capacitors, compact op-amp feedback and recovery paths, then route the complete local loops. Recheck stability, interference and load transients. Do this before further cosmetic routing work.

### F03 — Relay suppression is remote from the coils

K1/K2 are on Main and K3 is on Reverb. D331/D341 are on Control. Therefore coil recirculation paths include inter-board wiring. The current board arrangement does not meet TRACE-044's local suppression requirement, even though diodes exist in the circuit.

Closure: design suppression at each physical coil loop, retain suitable driver protection, and verify actual coil current, clamp voltage, release time and switching pops. Any relocation/addition must update the schematic, BOM, ports and PCB together. Do not blindly add diodes without checking the shared coil topology and release behavior.

### F04 — Disabled checks concealed 68 unmodeled wire assembly envelopes

Strict DRC reveals 43 Main, 12 Power and 13 Control `missing_courtyard` warnings. Every one is a `Renegade_Whole:WirePad_1.3mm` terminal. This is not evidence that 68 component bodies collide. It shows the soldered wire, insulation, bend and strain-relief envelope has not been represented or individually waived.

Main/Power/Control ignored `missing_courtyard`, `footprint_filters_mismatch`, `footprint_type_mismatch`, `track_not_centered_on_via` and `tuning_profile_track_geometries`. Strict copies enabled all five; no additional types were reported. There were no stored DRC exclusions. Reverb had no explicit ignored checks in its project file. A persisted global ignore is not a documented per-item engineering decision.

Closure: define real wire termination envelopes and keepouts; give any deliberate courtyard exception a specific reason; review restored severities before release. Do not create arbitrary tiny courtyards merely to silence the checker.

### F05 — Trace-shape requirement remains open on three boards

Main and Power each have a remaining 90-degree joined-segment candidate, including width-transition geometry. Control has a 46.157-degree candidate on RESET_CT near C321. Reverb has no simple bends over the screen threshold following the prior chamfer pass. The exact coordinates and nets are in `copper-audit.json`.

The screen separately reports 2 / 6 / 14 / 85 junction nodes for Main / Power / Control / Reverb. These are not 107 proven violations; branches, pad entries and via entries need separate inspection. Small existing Reverb chamfers can look square in the reduced full-board view. The screen does not prove every copper edge is smooth or free of acute wedges.

Closure: use 45-degree changes or arcs in the revised routes, then inspect transitions and branch geometry at useful magnification. Keep loop area, clearance and return geometry ahead of cosmetic shape. The electron-wall explanation is not the physical reason for this layout preference.

### F06 — Current, insulation and return rules are incomplete

Track widths range from 0.30 to 0.60 mm; Reverb uses 0.30 mm. Main's +12 V routing totals approximately 160.84 mm at 0.30/0.40 mm widths. None of these numbers proves adequate current capacity.

There is no explicit native copper stackup or fabrication copper-weight/material qualification. The nominal board thickness is 1.6 mm. Main/Power/Control use generic minimum clearance 0.25 mm, track width 0.30 mm, edge clearance 1 mm and minimum connection width zero. The named HV class is unassigned, **but explicit 5.5 mm custom rules are present for listed HV nets**. Do not report that the boards have no HV rules. Those copper rules still do not establish the complete insulation requirement or creepage through components, solder, harness and metalwork.

Missing release evidence: per-path RMS/peak/inrush and fault current, duration, allowed temperature rise and voltage drop, copper thickness/layer, via/neck/pad/connector/wire limits, and a working-voltage/transient/creepage/clearance matrix. No demonstrated current-specific rules exist. No complete loop/return review establishes segregation of rectifier, heater, coil, speaker and sensitive audio currents. Zero ground zones is not automatically a fault; a deliberate traced return system must be qualified rather than accepted by net name.

Closure: complete the budgets and actual manufacturing construction; encode the resulting rules; inspect both layers, joints, thermal structures and the assembled harness; verify temperatures, hum, switching noise and RF susceptibility on the prototype. Do not reduce spacing to fit routes.

### F07 — Exact parts and physical fit are not frozen

**52 on-board circuit references lack a selected MPN**: Main 8, Power 9, Control 25, Reverb 10. The inventory lists each. Some chosen parts elsewhere are only engineering selections with stock or domestic-price evidence pending. The current library name is not proof of actual pin, lead, body or voltage fit.

Outstanding examples include C605's rejected 50 V candidate versus its 63 V minimum, the proposed 100 V C0G replacement requiring a different package, and the 2.5 mm connector candidate versus present 2.54 mm footprints. Tube sockets are required and accounted off board, but their final pin-view, pitch, body, temperature and voltage qualification is incomplete. Regulator tabs/heatsinks must be checked electrically and mechanically before chassis attachment.

The four boards total **109900 mm²**, exceeding the reported 467 × 160 mm plane's **74720 mm²** before standoffs and wiring. This rules out a single non-overlapping plane; it does not rule out a properly designed multi-plane chassis. The depth datum is still provisional. No completed populated assembly establishes such a solution.

Received cabinet constraints: P1 307–308 mm clear opening, P2 approximately 53 mm with rear cover on, P3 inside height 383 mm, speaker aperture approximately 270 mm, tank 149.5 × 60 × 36.5 mm excluding installed cables. The Celestion Seventy 80 reference calls for a 283 mm cutout, so it cannot be accepted against the unchanged 270 mm aperture without a different verified fit. No cabinet cutting is authorized here.

The current chassis-service checks have no completed access clearances. The fixed-rail/removable-cassette concept meets the intended ownership: the wooden rear cover carries no chassis mounts. It has not passed a full tool-envelope or extraction check. The 215 × 48 mm control knob screening rectangle is not proof of hand clearance, curved opening fit, underside clearance or complete assembly fit.

Closure: freeze parts and dimensions, reserve speaker/magnet/transformer/tube/socket/heat/harness volumes, arrange the four functional blocks, model fixed-structure supports and the full drill chuck/body/bit approach, and prove rear-cover removal and cassette withdrawal. Drill/deburr metal before electronics are installed. Optional visible heater glow must not compromise these constraints.

### F08 — Functional acceptance and physical tests remain open

The expression pedal interface is specified but not implemented in the current circuit/PCB. Keep heel=dry, toe=panel setting and unplugged=normal knob operation; keep audio inside the amp. Original electric tube input/no added buffer remains the decision.

Earlier simulation evidence is bounded: generic input headroom fixtures, measured-resistance reverb fixtures and incomplete full-amp model qualification. It does not close real-transformer HF ringing, actual tank maximum drive current, R40 pulse stress, supervisor/relay sequencing, or final part substitutions. No board audit can supply the tank manufacturer's unknown thermal rating.

Closure: resolve circuit/model limits, rerun affected simulations after implementation, then execute the staged unpowered and powered acceptance plan with defined loads, probes, supply conditions and limits. Check PE, discharge, insulation, temperatures, tube operating points, wet-only operation, pedal/relay transitions, hum, RF susceptibility and mechanical rattle. Do not claim formal EMC or product-safety compliance from DRC or a quiet audio test.

## Canonical user-requirement check

| Requirement | Disposition at this audit |
|---|---|
| Preserve original six-tube electric amp; no extra input buffer | Recorded architecture; board contract reference coverage passes. Final assembled behavior unverified. |
| Tube sockets on every tube | Off-board socket architecture retained; exact socket/assembly qualification open. |
| Non-tube spring reverb, constant dry plus added wet knob | Current circuit architecture retained; complete installed performance unverified. |
| Rocker pedal controls wet only | **FAIL: implementation absent**; requirements retained. |
| Actual delivered yellow tweed cabinet and received tank | Measurements retained; complete fit unverified. |
| Whole amplifier PCB coverage | Four board domains and 46 off-board circuit references accounted; **routing incomplete**. |
| Functional blocks stay intact | Board ownership retained; local IC/regulator/support placement fails F02 intent. |
| Match selected parts and pot shafts to cool knobs | Partial exact selections; whole BOM and mechanical stack not frozen. |
| China low-quantity sourcing and price | Partial dated evidence only; no complete orderable BOM or current total. |
| Chassis mounts only to fixed structure | Correct proposed interface; actual mounting assembly unverified. |
| Rear wooden cover removes independently | Required; no completed interference/extraction proof. |
| Broad support flange permits drill access | Required; full tool approach and withdrawal remain unverified. |
| Tubes visible through rear slots if practical | Optional; no proven sightline or thermal guard arrangement. |
| EMI/RFI control | **Layout defects F02/F03**; assembled return/shield/coupling/EMC tests open. |
| Trace widths adequate for current | **NOT VERIFIED**, F06. Generic DRC width does not qualify ampacity. |
| 45-degree/arc routing, no sharp bends | Three remaining simple candidates; junction review incomplete, F05. |
| Simulations, exact BOM, schematic and build plan support release | Artifacts exist as drafts; consistency, selected-model and physical release gates open. |
| Log decisions in ICM | This audit, evidence, feedback FB-076 and next work saved; catalogs/checks updated at checkpoint. |

## Repair order and audit deliverables

1. Freeze missing device packages and the complete chassis/connector/socket interfaces. Resolve required expression control and protection changes before final placement.
2. Re-place by functional stage. Put bypasses, feedback parts and relay suppression at the circuits they serve. Reserve thermal and service spaces in the common assembly.
3. Derive current/voltage/insulation rules and the complete return/harness diagram. Assign meaningful classes and explicit exceptions without weakening HV constraints.
4. Route, inspect both layers and local loops, restore documented DRC coverage, and complete all connectivity and schematic/harness parity checks.
5. Recheck populated fit, drill access, rear-cover independence and extraction; review manufacturing exports only after these pass.
6. Complete model-specific simulations and staged physical acceptance. Keep release blocked until the applicable checks close.

This turn repaired audit coverage and stale status reporting. It did not move copper or claim the identified layout defects are repaired. Moving traces before exact parts, corrected placement and assembly envelopes are fixed would not close the release gates. Stable reviewer input is `../requirements-assessment.json`; the matrix factory is `../tools/build_requirements_matrix.py`. Native and strict-check factories are separate from their generated evidence.
