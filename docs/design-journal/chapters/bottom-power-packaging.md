# Lower power enclosure: research priorities, interfaces, and untested protocols

**Source checkpoint:** 26 November 2026; FB-146 and FB-147

**State label:** four five-pass review cycles complete; conditional comparison and acceptance gates only; no lower allocation adopted

**Baseline:** native boards and functional blocks unchanged; cabinet and tool envelopes remain incomplete

## The question and authority

The user asked whether power transformers, rectifiers, capacitors, and related equipment could share a metal enclosure mounted at the cabinet bottom, with cabling to the tube/audio assembly, and requested a Five Times Skill Plus pass, Alien Method alternatives, and a synthesis (FB-146/147). This is a design investigation request, not adoption of a lower enclosure or a circuit/layout change. The capacitor-bank fit sequence and combined FB-147 five-pass synthesis are complete; both leave the candidate distributions conditional and unadopted.

## Conditional hybrid to compare first

The lower-enclosure review gives hybrid B the first comparison priority, not a recommendation to build it. In that allocation, lower hardware includes power generation/magnetics, rectification, the C29/C30 raw reservoir, choke L1, and C26 on B_SCREEN; upper stage filtering retains C12 on B_EARLY and C13/C25 as separate references on the shared B_PRE node. The proposed allocation does not change values or nodes. The output transformer T2 stays upper for the initial comparison; its relocation is a separate question because it adds output and feedback wiring. Choke placement must be checked against its real current loop and compared separately within the distribution study.

The earlier three-board intention is not a statement that a three-board implementation currently exists. The native design still has four incomplete boards. A lower enclosure could reduce upper mass or reclaim populated board area, but also uses the cabinet floor that must accommodate the spring tank and speaker, and adds a second module, connectorized cables, structural support, service, and safety interfaces. Exact cabinet datums and occupied volumes are not established; unmeasured volume remains unknown, not spare.

## Functional and service boundaries

The split must preserve supply and return identities, local filtering, and the power functional block. No chassis metal is a normal supply return. Permanent protective-earth bonds remain independent of the signal harness, and GB1 remains the one deliberate signal/chassis bond. Every connector needs a pin map, ratings for its actual domain, strain relief, wrong-mate prevention, retention, and touch protection when either half is unmated.

Both modules can retain charge. Service review must cover charged, powered-off, standby-open, partly disconnected, and removed states; specify accessible test points, residual-voltage limits, measurement points, and a safe sequence for discharge, verification, disconnect, reconnect, and re-energization. The R501/R502 path is upstream of standby; downstream R506/R507 paths remain in the current source, but a disconnected capacitor bank may lose paths. No safe service time has been established, and this study does not add a bleeder.

Bias/contact or return loss while B+ remains energized is a blocking fault condition. Heater winding, grouping, and reference cannot be frozen while the VAL-076 heater-reference issue remains unresolved. At the existing nominal-plus-pilot 4.3815 A heater inventory, a hypothetical 10 mΩ full-loop resistance would drop 43.815 mV; this is a sensitivity calculation, not wire sizing or an accepted voltage drop. Cable voltage/current, startup, local decoupling, load-end reset/mute timing, and both mains modes need exact inputs.

## Mechanical, magnetic, and acoustic risks

The tank remains horizontal and open-side-down. Its received body envelope alone does not include plugs, mounts, cable bends, bag, spring movement, or extraction. A lower power box competes with tank and speaker space and must have a structural load path into fixed cabinet structure; transformer mass cannot ride on PCB standoffs or the removable wooden rear cover. The upper tube/audio module and lower power module each need independent support, accessible fasteners, lid access, and a removal path that does not require a live-connected harness to be removed first. Carry/transport load cases, floor-panel strength, joints, feet, and fasteners remain to establish.

An ordinary metal box is not credited with 50/60 Hz magnetic attenuation. Electric-field screening, direct transformer magnetic pickup into the tank or input stages, conducted noise, and mechanical buzz are separate paths. A floor-mounted transformer can mechanically excite the tank even if magnetic coupling falls. Low-frequency magnetic compatibility needs a matched, loaded test with fixed tank orientation/load/recovery gain and controlled cable routing. Movement happens only de-energized after discharge verification; any mains/field fixture must be closed and reviewed. No hum level, acoustic response, or tank immunity has been measured here.

Moving the power enclosure may warm the upper assembly through natural convection. Thermal limits depend on exact parts, covers, loads, and ambient. Ventilation, touch protection, structural retention, harness routes, and tank/speaker/radiation clearances all remain open. No vent dimension, shielding thickness, or spacing is selected.

## Alien Method comparison and bounded protocols

The Alien study froze six balanced cards: three conventional concepts (upper-power reference, lower floor plinth with reserved tank corridor, and supported upper capacitor bank) and three recombined concepts (lower bulk supply with local stage filtering; more-complete lower power with all four film filters below; and a supported vertical lower power card). They use the same mechanism catalogue and rubric. The method is qualitative; the six-card desk sample proves no novelty, superiority, or real-world advantage. Unknowns remain conditional, hard failures eliminate, and no aggregate score or novelty bonus is used.

The research retains K1/K4 as conditional comparison priorities, K2 as a diagnostic upper reference, K6 as a fallback rather than a third experiment, and defers K3/K5 detailed modelling until geometry is known. These labels prioritize information, not architectures. K2 itself is unfinished and has known provisional width/depth deficits; it is not a qualified or safe baseline.

At most two protocols are drafted, neither executed. P1 compares K2/K1/K4 in a common populated model and inert service trial, recording every coupled change in walls, mounts, support, connectors, wiring, capacitor allocation, cable length, and tank movement. It does not isolate capacitor location as a single cause and cannot establish thermal, retention, or electrical safety. Unknown dimensions, insulation, or tool envelopes that could reverse the result stop dependent modelling.

P2 is conditional on P1: a low-voltage passive filter/harness comparison between K1 and K4, only if both lower options remain credible and K4 provides a measurable whole-assembly benefit beyond dimensional uncertainty. It requires exact cable/contact route R/L/C, representative terminations, loads/steps, bandwidth, source impedance, absolute rail-disturbance limits, and instrument uncertainty. It cannot prove high-voltage insulation, heater behavior, transformer ripple, active tube loading, or full-amplifier noise/stability. If tank pickup becomes the decisive question, a bounded closed-source magnetic protocol replaces P2; it does not create a third protocol. Any full amplifier comparison remains later and gated by electrical safety and heater/bias/PE/discharge qualification.

## Phase status and decision boundary

The capacitor-bank plan, lower-power enclosure review, Alien Method review, and combined FB-147 synthesis each completed their five-pass sequence and saved review evidence. The lower hybrid is a conditional research priority only. No capacitor, transformer, connector, enclosure, or module allocation is selected; no native CAD or functional block is changed; no physical fit, hum, thermal, structural, transport, or service test has passed; and no fabrication release follows.

## Next evidence

Build one common populated cassette/cabinet comparison with speaker, actual tank and extraction path, magnetics, control openings, supports, connector mating faces, both module withdrawal paths, and the real tool envelope. Resolve exact transformer and connector choices, heater reference, bias fault response, node voltages/currents, insulation, discharge, mass/retention, heat, tank pickup, and quantity-one delivered China cost before detailed native placement. The deferred drill/driver dimensions remain required; a 46 mm chuck alone is insufficient. Use inert mock-ups and closed reviewed fixtures before any energized prototype evidence.

## Physical-build placeholder

Record actual cabinet/floor datums, tank and speaker clearances, transformer mass and mounting stack, carry/transport assumptions, connector/harness routes and ratings, module extraction, charged-state measurements, covers-on temperatures, tank pickup/noise, and acoustic/mechanical buzz only when measured on identified hardware with a documented method. None is established by these plans.

## Reusable lesson

Separating physical power and audio modules can preserve functional ownership, but it creates electrical, safety, service, thermal, magnetic, structural, and acoustic seams. Compare complete assemblies and service states rather than detached board dimensions. A source-backed ideation method can structure alternatives; it does not establish novelty, prove the winning concept, or substitute for unexecuted experiments.

## Sources

- [Current step-by-step calculations](../calculations/current-power-packaging.md)
- [Combined five-pass synthesis](../../../plans/power-packaging-synthesis/final.md)
- [Synthesis review receipts](../../../plans/power-packaging-synthesis/evidence.md)
- [Acceptance gates](../../../plans/power-packaging-synthesis/acceptance.md)
- [Proposed interface table](../../../plans/power-packaging-synthesis/interface-table.md)
- [FB-146/147 lower enclosure contract](../../../plans/bottom-power-enclosure/CONTEXT.md)
- [Bottom power enclosure final plan](../../../plans/bottom-power-enclosure/final.md)
- [Mechanical research](../../../plans/bottom-power-enclosure/mechanical-research.md)
- [Harness research](../../../plans/bottom-power-enclosure/harness-research.md)
- [Magnetic research](../../../plans/bottom-power-enclosure/magnetic-research.md)
- [Alien Method plan contract](../../../plans/power-packaging-alien/CONTEXT.md)
- [Alien Method final comparison and protocols](../../../plans/power-packaging-alien/final.md)
- [Alien Method research](../../../plans/power-packaging-alien/research.md)
- [Alien Method review receipts](../../../plans/power-packaging-alien/evidence.md)
- [Completed capacitor-bank fit plan](../../../plans/capacitor-bank-fit/final.md)
- [Combined synthesis contract](../../../plans/power-packaging-synthesis/CONTEXT.md)
- [Feedback entries FB-146/147](../../../brain/feedback/events.json)
