> Current electrical work: [v0.4 solid-state spring reverb package](../../engineering/solid-state-reverb/README.md). This supersedes the earlier tube-reverb architecture; remaining release gates are in its build plan.

# One working Renegade prototype

Updated October 4, 2026. This is the active first-stage plan following the user's scope correction.

## Goal and completion
Build **one functioning 220 V / 50 Hz combo that fits the chosen box**, with its speaker, original channel functions, added solid-state-driven real spring reverb and debounced channel/reverb pedal. The yellow-tweed Mable5E3 cabinet is delivered and fixed. Select parts and redesign internal mechanical/PCB arrangements to fit the actual cabinet. The original amplifier is the electrical starting point; a 5E3-looking cabinet does not select a 5E3 circuit.

Completion means the actual assembled amp fits, can be serviced, and passes agreed electrical, audio, switching and thermal checks in its cabinet. Deliver editable design files, the actual BOM/cost ledger, wiring and assembly instructions, measured test results, and a record of remaining limitations. A CAD fit or functioning open-chassis amp alone does not finish this milestone.

The [handoff](../../Renegade_Codex_Handoff.md) remains canonical for requirements. The [five-unit plan](../renegade-five-unit-build/final.md) is retained for later production and sales planning. Buyer research, four repeat builds, sales launch, production cosmetics and repeat-unit cost optimization are outside this first milestone.

Use the [design-imperative review](<../../Design Imperatives/review/REVIEW.md>) and its [consolidated checks](<../../Design Imperatives/review/prototype-checks.csv>) throughout P01–P08, especially before P04/P05 design release. Record actual applicability, numerical limits, revisions and evidence; all initial checks are pending evidence. These references supplement the handoff rather than selecting components or changing the circuit topology.

## First inputs

The user subsequently requested the updated schematic itself. An [editable source baseline and v0.3 wired revised draft](../../engineering/updated-schematic/README.md) are created with scoped native checks and limited bias/debounce reference analyses. This is progress on P01/P04 draft work while packaging and build-part/model evidence remain pending; it does not satisfy P03 fit review or P04's selected-component simulation/release gate. See [VAL-009](../../brain/records/VAL-009-updated-schematic-draft.md).
The original `Renegade Tube Amp.pptx` was received and visually inspected October 4, 2026. [Source intake](../../sources/original-ppt/inspection.md) and the as-printed BOM now support faithful baseline capture, with reference/value conflicts retained for reconciliation. The installed KiCad starter contains preview symbols, not the complete circuit.

November 11: exact-product manufacturer drawings now establish external dimensions and a 312mm control opening; see engineering/solid-state-reverb/evidence/cabinet-research.md. Usable assembled chassis/tank/speaker space remains unverified; carton dimensions cannot establish fit. Obtain a dimensioned drawing or measurements of a representative shell: interior, chassis opening and supports, baffle/cutout/bolt pattern, speaker depth, tank mounting area and access. Keep drawing revisions and measurement uncertainty explicit. See the [shell dossier](../../brain/records/CMP-001-mable-5e3-shell.md).

Output power, budget, exact bench resources and speaker voicing remain open. The user confirmed that main operating controls belong on the **top or front**; either orientation is acceptable. Compare a top-facing layout in the preferred 5E3-style shell with a front-facing cabinet/chassis layout against fit, visibility, knob access and quantity-one cost. A top-facing panel near the rear edge still qualifies as top-mounted. Final orientation and hole positions remain to be selected from dimensional evidence. The source BOM resolves the original tube count to four 12AX7s and two EL34s; the November 11 reverb revision adds no tubes. It supplies no measured output-power specification. Do not borrow hypothetical counts from the five-unit cost scenarios.

## Delegable sequence
Each package receives a task card naming exact inputs/revisions, dependencies, outputs, owner, automated checks and human review. Roles below can be delegated when work begins; this plan does not dispatch agents or authorize orders.

| Step | Role and dependencies | Work and evidence needed to finish |
|---|---|---|
| P01 | Source/electrical reviewer; in progress | Source receipt, three-image visual inspection and as-printed BOM transcription complete. Next reconcile ambiguous references/connectivity, complete starter audit and establish prototype targets. No replacement circuit invented from the summary. |
| P02 | Physical designer; parallel with P01 | Establish actual shell geometry, chassis/control constraints for top-facing or front-facing controls, usable panel length/depth, knob access, speaker and tank space, mounting datums and ventilation. Identify whether drawings suffice or a sample must be measured; cost any sample before purchase. |
| P03 | Electrical + physical designers; P01/P02 | Build an envelope layout using dimensioned candidate magnetics, tubes/sockets, speaker, tank and controls. Check speaker magnet, tank, chassis, transformer and tube interference, wiring space, heat and service access. Freeze the packaging concept only after fit review. |
| P04 | Circuit designer + component researcher; P03 packaging concept | Capture and simulate the reconciled original baseline, then refactor all mains supplies for 220 V / 50 Hz and add reverb/switching. Calculate complete heater/HV/bias/control loads, ratings and operating points. Select traceable parts and qualify matched models; simulate each block and the integrated revision with load/tolerance/startup tests. Return changed component envelopes to P03. Deliver schematic, BOM, model provenance, netlists, logs/results and unresolved limits. |
| P05 | PCB + mechanical designers; reviewed P03/P04 including simulation evidence | Choose PCB, modular or hybrid construction against quantity-one cost, noise, heat and serviceability. Produce prototype board/chassis/panel geometry and a full-size paper fit check. Review routing, grounding, insulation spacing, mounting and drill data. Inspect native files, renders and relevant ERC/DRC findings. |
| P06 | Sourcing coordinator + owner; reviewed P05 | Prepare a quantity-one purchasing list and Shanghai delivered quotes. Include unavoidable board MOQ/extras, setup, drilling, shipping, tax and correction allowance. Match exact part and drawing revisions; review cost and manufacturing package before ordering. |
| P07 | Builder + competent tube-amp reviewer; parts inspected, P06 | Inspect received dimensions and ratings, perform an unpowered dry assembly in the box, then build to documented wiring/assembly instructions. Complete the electrical review before energizing. Test supplies and control functions, then dry channels, then reverb and mixing in stages. |
| P08 | Builder + reviewer; P07 | Install and test the complete combo in its normal orientation. Record actual fit, access, vibration/rattle, hum, temperature, audio performance and switching behavior. Correct defects and repeat affected checks until acceptance; archive the as-built revision and costs. |

P03–P05 form an iteration loop: component selection and circuit requirements can change the layout. Approve the fit again after changes. When a candidate or draft layout conflicts with the cabinet, change the part or internal arrangement. Do not drop features, change the original amplifier or replace the delivered cabinet without a new user decision.

## Prototype construction and tool choices
Use KiCad for electrical capture/layout, FreeCAD for a dimensioned assembly and chassis, and Inkscape for a simple legible panel overlay or decal. Use a shared parameter/interface register with units, datums, coordinate transforms, part identifiers and revisions so PCB mounts, chassis holes and artwork agree. Follow the [Circuit Design Skill Ladder](/Users/appleadmin/.codex/skills/circuit-design-skill-ladder/SKILL.md) and [Physical Design Agent Ladder](/Users/appleadmin/.codex/skills/physical-design-agent-ladder/SKILL.md).

Automate supported exports, checks, BOM generation and drawing generation; inspect native files and rendered outputs. A script-generated file is not proof of connectivity, fit or safe operation. Supplier drawings and physical measurements remain required evidence.

Favor an economical serviceable prototype chassis, standard hardware and clear temporary labels. Check control spacing and hole positions at full scale before machining. Keep the sleek-panel direction, but defer elaborate artwork/finishing until the layout works. Where PCBs are used, order fabricated boards with drilled holes and review the vendor's required plated/nonplated drill and slot package. Cabinet and panel holes require separate mechanical fabrication instructions.

## Acceptance and correction loop
The user's October 4 requirement makes selected-component simulation part of P04. Follow [simulation requirements](../../simulation/requirements.md): establish source topology and exact parts, qualify models against manufacturer evidence, simulate blocks and integrated behavior, then review results before board release. Keep baseline reference models distinct from build selections. A missing supplier model requires a documented equivalent or measured parameter model with bounds; no blank or idealized model can count as an exact-component pass.

Before testing, the reviewer sets numerical limits and methods from the actual circuit, component ratings and intended use. Record supply conditions, load, instruments, settings, warm-up and duration alongside each result. Include protective earth, fuse/mains wiring, discharge provisions, component stress, supply behavior, output power, stability, noise, reverb range, startup/shutdown, pedal reset/debounce and switching pops. Clean ERC/DRC is only one part of this evidence.

For final in-box acceptance, verify all mounting and wiring clearances against the actual parts; check controls and pedal access, speaker/tank operation, ventilation, hot-part proximity and safe service access. Run the agreed sustained operating tests in the closed/normal-use assembly, since packaging can change heat, hum and vibration. Log and repair each failure; revise affected electrical/mechanical files and retest rather than accepting a known defect to end the phase.

## Budget and next action
Price this prototype directly at quantity one. The five-unit budget divided by five is not a reliable prototype estimate: sample prices, minimum board quantities, tooling, freight and rework differ. Prepare a costed minimum build plus a correction allowance once source and dimensions establish the required parts. Existing sourcing leads are leads to recheck, not purchase approvals.

Continue P01 and P02 together. The original source is available; next produce the reconciled circuit brief and actual box dimension sheet, then a reviewed fit layout. Procurement and supplier messages require the owner's authorization; this planning correction does not place orders.
