# Bottom power enclosure: electrical harness research

2026-11-26. Owner: delegated electrical-interface researcher; integration owns adoption. Inputs: [v2](v2.md), [current circuit](../../engineering/whole-amp/reverb-600/circuit.json), [grounding contract](../../engineering/whole-amp/reverb-600/grounding-contract.json), [capacitor interface evidence](../capacitor-bank-fit/interface-research.md), [heater compatibility review](../../engineering/component-selection/heater-divider-rating/interface-review.md). Process: read-only circuit/record inspection, primary manufacturer guidance and conditional arithmetic. Output: allocation consequences and qualification gates, not a selected harness or circuit change. Human check: trace each outgoing conductor and its return on the real two-module assembly, including each disconnected state.

## Finding and allocation comparison

Bottom-mounted power is electrically plausible, but it is not equivalent to moving every capacitor away from its load. Use allocation B as the first electrical comparison with the existing upper-power baseline: keep the transformer/HV rectifier/C29-C30 charging loop together below, move L1 with C26 below, and retain C12/C13/C25 and their associated stage-filter wiring above. Compare C, all four film filters below, only with an explicit remote-rail and return model. This is an engineering preference for the next comparison, not a fit or performance verdict.

| Circuit boundary | B: bulk and screen supply below | C: all four film filters below |
|---|---|---|
| Raw reservoir | Keep HV winding, D3-D6, F2, C29/C30 and CT return together; do not send rectifier charging pulses through the upper assembly | Same |
| B_MAIN / output stage | B_MAIN must reach T2 center tap if T2 stays above; keep the output-stage return path explicit | Same |
| Screen supply | B_SCREEN and controlled return go up from local L1/C26 loop | Same |
| Preamp supply | Put R35 with the upper B_PRE filters C13/C25, and R17 with upper C12; branch B_SCREEN feeds this network above | B_PRE and B_EARLY become additional remote supply nodes; R35/R17 allocation must be explicit, preferably kept with their filter network for the comparison |
| Local transient currents | Stage capacitors can supply their loads through short local loops | Stage load current traverses the cable to the remote capacitor and back; conductor resistance, inductance and common return impedance enter the supply seen by the stage |
| Change burden | Splits the present functional Power assembly physically; requires a measured reallocation/change list | Whole-Power-PCB relocation may preserve more physical clustering, but still needs the actual port map, available space and all remote-interface checks |

The authoritative topology is B_RAW → S2 → B_MAIN → L1 → B_SCREEN → R35 → B_PRE → R17 → B_EARLY; T2 CT branches before L1. C12 is 50 µF B_EARLY/GND; C13 and C25 are **two distinct 50 µF references on B_PRE/GND**; C26 is 50 µF B_SCREEN/GND. Preserve references, values, nodes and physical return intent. A node name alone does not define a physical return path.

TI documents that wiring inductance/loop area degrades bypassing and can introduce ringing and coupled noise; its source is a buck-converter layout discussion, so only the general parasitic/loop principles transfer here, not its topology-specific grounding advice or numeric expectations. [TI SSZTAL0](https://www.ti.com/document-viewer/lit/html/SSZTAL0/GUID-CF03725F-911C-4A96-9391-0E639F290409). The allocation conclusions above are circuit-specific engineering inferences from those principles and the retained node map.

## Required interface register

Use these as named interface requirements, **not final connector cavity numbers**. The upper/lower allocation of bias and auxiliary regulation is still undefined. Freeze it before quoting a harness.

| Interface | Exact current circuit nets / endpoints | Required decision or check |
|---|---|---|
| HV load feed | B_MAIN to T2.CT; B_SCREEN to R41/R42 and R35 | DC, ripple, startup/no-load/standby and fault envelope; forward and return geometry; contact DC rating and insulation |
| Remote stage feeds, C only | B_PRE, B_EARLY plus controlled returns | Load-step/source-impedance comparison with B; keep C13/C25 separate references |
| Fixed bias | BIAS_OUT is the existing grid-bias distribution node; BIAS_RAW and BIAS_FILTER are upstream filtered nodes | Decide which side owns R40/D7/C28/R39/C27/R38/RV10/R503. If adjustment remains above, enumerate its actual crossing nets. Check loss/open return or bias contact while B+ remains connected; low normal bias current does not make this an inconsequential disconnect |
| Heaters | Present HEAT_A / HEAT_B to six physical tubes and JH1 pilot | Cannot freeze final number of heater pairs or references until HD-002 is resolved; see below |
| Auxiliary rails | CTRL_RAW/NEG_RAW if regulators remain above; +15V/-15V/+12V/+5V as needed if regulators move below | Keep rectifier/reservoir loops together; keep each regulator's required input/output capacitors and protection local; qualify actual load, collapse/sequence and unplugged behavior |
| Reference / returns | HREF if split across modules; defined physical GND paths | Avoid shared pulse-current impedance in quiet references; determine which side retains reference/discharge paths when unplugged |
| Protective earth | J7.3 → dedicated JPE1; independent exposed-metal bonds represented by JPE2 | Separate safety path, mechanical retention and continuity schedule; not a spare signal-return pin |
| Controls | S1 switches L_FUSED/L_SW and MAINS_N/N_SW; S2 switches B_RAW/B_MAIN | Either locate the actual switches below or explicitly include long switched mains/HV conductors to upper controls; moving their function to a relay is a circuit redesign |

Keeping T2 above avoids gratuitously extending OT_PA/OT_PB plate leads and the secondary/feedback circuit. If a separate comparison moves T2, its primary, speaker/selector/return and feedback paths need their own parasitic and stability assessment. This report does not move it.

For every connector half record node-to-node and node-to-metal working voltage, peak/transient stress, current per contact, number of simultaneously loaded contacts, hot temperature, wire insulation/diameter, termination tooling, retention, mating cycles, wrong-mate prevention and **unmated** contact accessibility. Manufacturer rating depends on the actual configuration: Phoenix Contact, for example, explicitly specifies voltage, pollution/overvoltage conditions, wire size and temperature derating separately, and identifies different voltage limits for power and signal contacts in one mixed connector. This illustrates why a headline current or voltage cannot qualify an unspecified harness. [Phoenix Contact SH-8ESS48A9LDLSX](https://www.phoenixcontact.com/en-pc/products/coupler-connector-sh-8ess48a9ldlsx-1244440). This expensive example is guidance, not a candidate purchase.

## Heater drop and reference uncertainty

The existing source-bound nominal heater inventory is 4 × 0.3 A ECC83S + 2 × 1.5 A EL34 = **4.20 A at 6.3 V**. Existing midpoint resistors add 6.3/200 = 0.0315 A; the unselected pilot allowance adds 0.150 A: **4.3815 A**. These values are nominal/allowance only, not a maximum, cold-start surge or winding rating. [JJ ECC83S](https://www.jj-electronic.com/images/stories/product/preamplifying_tubes/pdf/ecc83s.pdf), [JJ EL34/E34L](https://www.jj-electronic.com/images/stories/product/power_tubes/pdf/el34_e34l.pdf), [local load inventory and limitations](../../engineering/whole-amp/aux-supply/load-review.md).

Conditional resistive calculation, with total loop resistance including both conductors, all contacts and terminations:

`Vdrop = I × Rloop`; `Ploop = I² × Rloop`.

At the existing 4.3815 A inventory, each **10 mΩ of loop resistance** costs **43.815 mV** and **0.192 W**. If an engineering budget of 0.10 V were later justified, it would permit only **22.82 mΩ total loop resistance** at this inventory; 0.20 V would permit **45.65 mΩ**. These are arithmetic sensitivities, **not adopted allowable drops**. The loaded transformer voltage at each mains corner, actual tube heater tolerance, conductor temperature, startup current and socket/contact drop remain inputs. Model the AC loop impedance where necessary and measure true RMS across the most distant socket. Measure cold start and hot operation in both mains modes; do not infer socket voltage from transformer terminals.

A wire-size calculation can follow once length and construction are known: `Rloop(T) = 2 × length × resistance_per_length(T) + sum(contact/termination resistances)`, adjusted for branches rather than pretending every socket draws the full group current. Use the selected wire maker's maximum resistance and actual contact specification. Do not choose gauge merely from ampacity; heater voltage drop may dominate before ampacity does.

The latest [HD-002](../../engineering/component-selection/heater-divider-rating/interface-review.md) is a blocking interface result: shared HREF has no permissible interval in 14 of 38 declared model cases; its nominal best-case DC reference resistance exceeds the reference JJ EL34 limit. Separate isolated heater groups are a candidate, not an adopted fix. Four preamp heaters nominally require 1.2 A and the two EL34s 3.0 A, before separate midpoint/pilot/startup budgets. At the same 10 mΩ loop resistance these isolated groups would lose 12 mV/30 mV and 0.0144 W/0.090 W respectively. A center tap on one continuous winding does not create two galvanically independent supplies.

Do not freeze a two-wire heater connector, adopt extra windings, or claim an isolated split solves everything: the highest modeled preamp case still fails its shared preamp reference window. Both triodes in V3 share a heater. The exact tubes and complete reference/fault envelope must be resolved first. Elevated heaters also require common-mode insulation to other harness circuits and chassis; their 6.3 V differential is not the whole insulation stress. Preserve close paired heater routing, its insulation and separation from sensitive grids; twisting does not repair insufficient voltage/current rating.

## Local bypass and lead parasitics

Remote bulk storage must not absorb existing local bypass components into the bottom box simply because all are called capacitors. TI's exact OPA2134 guidance places ceramic bypasses at each supply pin and ground with short connections; its current datasheet recommends 10 nF. That value is source guidance, **not authorization to replace the native capacitor values**. [TI OPAx134 SBOS058B, sections 7.3–7.4](https://www.ti.com/lit/ds/symlink/opa2134.pdf). Preserve the existing local control/reverb bypass and relay-clamp work, with its latest native checks; requalify regulator sockets, input/output capacitors and protection against the chosen physical allocation.

For B and C, derive or measure cable R/L and coupling using the actual route, then compare rail impedance and load transients with the same load model and capacitor ESR/ESL. `ΔV = R × ΔI + L × di/dt` is a useful local sensitivity; `f0 = 1/(2π√(LC))` identifies an idealized resonance to investigate, not an actual predicted oscillation without source/load resistance and distributed wiring. No cable inductance value has been assumed here. Include open return, one-rail disconnect, standby transition and regulator reverse-current paths. Recheck the existing reset/mute behavior using rail voltages **at the load**, because cable drop/collapse can differ from the source measurement.

Draw recharge and load-return loops separately. Run a supplied rail with its intentional return route rather than returning it through unrelated audio wiring. Multiple same-net return conductors are not automatically correct either: inventory the shared paths, including signal interconnects, tank shields and chassis bonds, so current division is explicit. PE or the enclosure must never be the normal return under the project contract.

## PE continuity and stored charge

The [grounding contract](../../engineering/whole-amp/reverb-600/grounding-contract.json) already requires J7.3 directly to a dedicated safety stud with no PCB, switch, fuse or signal harness in series. Every accessible conductive enclosure, upper chassis and decorative panel needs its own verified bond in the assembly schedule. GB1 remains the separate permanent GND/chassis bond near the quiet input; a second metal box does not authorize another GND/chassis bond. Independent rear-cover removal must not remove protective bonding. If service requires disconnecting a protective bond, the written reassembly procedure must restore and verify it before any energized test. Physical conductors, hardware, surface preparation, continuity/fault tests and applicable acceptance limits remain unqualified.

Do not assume the source side alone can be charged. The existing capacitors create independent energy stores when a cable is removed:

| State | Retained path / unresolved consequence |
|---|---|
| Mains off, S2 closed, all connected | R501/R502 shunt the raw series reservoir; downstream filters also have loads and the HREF divider path. Complete-network decay needs calculation and physical verification |
| Standby open | R501/R502 are upstream of S2. B_SCREEN still has R506 → HREF → R507 → GND when those components remain connected; C12/C13/C25 couple through R35/R17. Do not claim either instantaneous discharge or no discharge |
| Upper assembly unplugged in B | Stage filters above may lose a lower-mounted HREF discharge route; tube loading is not a guaranteed service bleeder. Bias/local auxiliary capacitors must also be inventoried |
| All filters below in C, cable unplugged | Lower contacts can remain charged. Upper local/bias capacitors can independently retain charge or backfeed contacts; both halves require assessment |
| Partial contact separation/open return | Normal return and reference paths can disappear before a live feed does. No live/unverified-charge unplugging is approved; contact order alone cannot substitute for the assessed service procedure |

Useful conditional arithmetic: C29/C30 are two nominal 220 µF capacitors in series, hence nominal effective capacitance 110 µF under equal voltage sharing. Their retained 220 kΩ bleeder per capacitor gives an isolated nominal time constant of **48.4 s**. This is not the actual full-network discharge time or a guaranteed service delay; tolerance, faults, unequal sharing and other connected stores matter. Stored energy is `½CV²`: one 50 µF capacitor at a hypothetical 400 V stores 4 J; the nominal series raw pair at a hypothetical total 400 V stores 8.8 J. These voltages are illustrative, not measured operating values. Each actual rail needs its own maximum voltage/tolerance calculation and test points.

Before accepting a removable assembly, electrical integration must specify an ordered power-isolation, discharge, voltage-verification, unplug/replug and PE-recheck procedure, with justified residual-voltage limits and retained paths on each side. Do not invent a waiting time or add an unreviewed bleeder as a packaging shortcut. Candidate capacitor charge/discharge restrictions still apply; see the [previous manufacturer-backed capacitor review](../capacitor-bank-fit/interface-research.md).

## 120/220 V controls placement

The preserved [mains decision](../../brain/records/DEC-015-switchable-mains.md) requires 120 V/60 Hz and 220 V/50 Hz, voltage-specific protection and a recessed marked selector operated only with power disconnected. The native baseline still has 220 V T1 and T3 references; it is not a dual-voltage implementation. Both mains-powered transformers must be handled by the selected arrangement, not only T1. No final fuse values follow from this packaging research.

For the lower-enclosure comparison, group inlet, protective stud, voltage selection, fuses and transformer primaries below. Locate the actual power switch there if acceptable access can be shown. If the user's upper control location is retained, explicitly count the long mains loop and its separate guarded routing/strain relief. Likewise an upper S2 sends B_RAW/B_MAIN between modules; keeping its HV switching function below may require a user-interface change or a separately reviewed remote actuation design. These costs must not disappear from the comparison.

Schurter documents selector inserts for different winding arrangements and approval only together with their matching power-entry module. Its table includes 115/230 and 120/240 two-winding markings and other tapped arrangements; none establishes this project's 120/220 supply or selects a part. [Schurter selector architecture](https://www.schurter.com/en/part/4305.0048.00). Schurter's IEC appliance-coupler guidance is for AC mains couplers with defined voltage/current/temperature conditions; it is not evidence that a familiar mains-style connector is suitable for the separate HVDC rails. [Schurter appliance-coupler guidance](https://www.schurter.com/en/knowledge/appliance-couplers).

## Next executable gates

1. Integration freezes B/C allocations for R35/R17, bias adjustment, auxiliary regulators, S1/S2 and heater-reference ownership. Mark every changed interface; preserve functional blocks and the existing values/nets.
2. Electrical owner resolves HD-002 sufficiently to specify heater group count, transformer winding isolation and reference common-mode envelope. Exact purchased tube identities, heater voltage tolerance and startup load remain missing.
3. Mechanical owner supplies min/max cable lengths, service loops and routes for each allocation, including clearance to speaker/tank, hot tubes and edges. Electrical owner applies current/drop/parasitic and insulation budgets to those paths.
4. Source exact wire/contact/connector assemblies only after those bounds; no final gauge, cavity count, connector series, price or Shanghai availability is established by this report.
5. Prove each disconnected module's discharge/test-point and PE schedule; then perform matched rail/noise/transient, physical continuity/insulation, load-temperature and service checks before adoption.

Only this research file was authored. Circuit and source inspection was read-only; no native schematic/PCB modification, new simulation, bench measurement, parts selection or fabrication release is claimed. The parent integration owner maintains shared catalogs, handoff and journal.
