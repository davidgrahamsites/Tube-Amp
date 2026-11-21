# Acoustic Guitar Amp — new-chat handoff

Prepared 20 November 2026. Owner: the next acoustic-build chat.

## Fixed brief for the new chat

**Build a clean tube amplifier for acoustic guitar, with an op-amp input buffer and a properly matched main speaker, tweeter and crossover, inside the existing delivered yellow-tweed cabinet.** Use replaceable tube sockets. Retain the solid-state-driven spring reverb and documented wet-only controls. This is the acoustic branch; preserve the separate electric build.

The user is concerned that the project has drifted away from the starter amplifier. Begin with a controlled reuse review of the original Renegade clean channel, phase inverter, push-pull EL34 power section and supplies. Do not assume a complete new amplifier is required or promise the inherited circuit already meets acoustic targets. No specific high wattage or full-power 20Hz bandwidth has been approved.

## 1. Start here

Repository: https://github.com/davidgrahamsites/Tube-Amp

Work on **`acoustic-guitar-amp`**. The separate **`electric-guitar-amp`** branch preserves the complete electric build at commit **`6eba80905b44ba7af29efd09fbd587d7280a8521`**. This acoustic branch starts from that exact commit. The electric checkpoint is an engineering snapshot, not a finished amplifier.

Local project folder at handoff:
`/Users/appleadmin/Documents/KiCad/Projects/Renegate Tube Amp with Reverb`

The spelling `Renegate` in the folder is intentional to match the existing path. Do not rename or move the workspace casually. Git branch switching changes the same working folder: two simultaneous chats must not independently switch it. If both builds are worked on concurrently, use a separate checkout or an approved tool-created worktree and give each chat one branch. The user will create the new chat; no new chat was created for them.

Startup sequence:

1. Read root `AGENTS.md`, `BUILD_VARIANT.md`, `CONTEXT.md`, this handoff and `PROJECT_STATUS.md`.
2. Check `git status --short`, `git branch --show-current`, `git log -3 --oneline` and remotes. Preserve any later user edits. Do not force reset or overwrite the electric branch.
3. Read `Renegade_Codex_Handoff.md` for canonical requirements and `brain/records/DEC-009-separate-electric-acoustic-builds.md` for the split decision.
4. Read the exact engineering modules needed for the next task, then their evidence. Do not rerun old generators just because they exist.

## 2. What the user authorized

The user primarily plays acoustic guitar. They explicitly clarified that “off amp buffer” meant **op-amp buffer** and instructed us to continue with that, select a suitable **speaker, tweeter and crossover for acoustic guitar**, fit everything into the cabinet already owned, and log all decisions in ICM.

They then requested two separate builds and publication of everything current to this GitHub repository. Their sequencing instruction was: finish adding the current project to the electric branch first, then create the acoustic branch and extensive notes for a new chat. Accordingly, this handoff does **not** claim a new buffer design, acoustic crossover, selected acoustic drivers or acoustic-specific PCB has already been completed.

The existing electric build stays intact. For acoustic work, the tube architecture is the inherited starting point; approval for a buffer and different speaker system does not by itself authorize removing all tubes, deleting required controls, replacing the cabinet, or turning it into a wholly different commercial amp. Explain and resolve any major architecture conflict when concrete evidence makes it necessary.

The user wants action and continuing progress, not repeated shortlists or permission questions for routine research/design. They want economical, durable, low-quantity components sourced within China, with RMB purchasing options. No purchase or fabrication upload is authorized by this branch handoff.

## 3. The two guitars

The user identifies them as:

- **Night Wish 550-D**; pickup model unknown.
- **ENYA Nova Go**; exact version unknown.

One has a battery and one does not. **Which guitar has which is not confirmed.** The earlier answer “passive pickup with no battery” was followed by clarification that there are two guitars. Do not treat both as passive, assume both have pickups, assign a piezo to either from the name, or confuse the acoustic Nova Go with the Nova Go Sonic electric model.

Research is saved in `engineering/component-selection/evidence/acoustic-input-speaker-review-2026-11-20.md`. Enya manufacturer pages describe an ES1/D1 smart rechargeable Nova Go version, but that does not identify the user's specific instrument. No exact manufacturer pickup specification for the reported Night Wish 550-D was established. Next useful evidence is the actual output/control/pickup hardware, a model label, or the user's identification of which guitar is powered. Avoid repeatedly asking for facts already recorded.

## 4. Acoustic design direction and important distinctions

### Input buffer

A FET-input op-amp unity-gain buffer is an authorized design direction, not an already selected circuit. Evaluate the actual source type and a defined input resistance; approximately 10 MΩ is a possible passive-piezo starting point, not a universal requirement for every pickup. Magnetic pickups may need different loading. A high-input-impedance op-amp does not alone establish the impedance of the completed input circuit.

Define bias return, coupling capacitor, RF filtering, current-limited protection, rail decoupling, grounding, input transient handling and headroom for the battery-powered instrument. Select the exact device/package and source it. Compare noise with realistic pickup/source capacitance and cable length. Check startup/shutdown and low-voltage supply loading. Preserve the original electric input on the electric branch.

### Speaker and crossover

No acoustic speaker, tweeter or crossover part has yet been selected. No hole has been authorized or cut. The old Celestion Seventy 80 entry is a dimensional reference, not the chosen acoustic driver.

An acoustic system often benefits from a woofer plus tweeter. A tweeter does not remove an electric-guitar speaker's uneven midrange or make the inherited tube preamp neutral. Assess clean-channel response and realistic clean output/headroom along with the speaker system. Tube electronics can be retained, but the intended clean acoustic response must be demonstrated.

Select the driver pair as a system. Obtain manufacturer response/impedance and physical drawings, domestic quantity-one sourcing evidence, sensitivity and power handling. Design the crossover against actual drivers and baffle placement; a generic “8 Ω crossover” label is not sufficient. Include tweeter attenuation/protection and the complete impedance versus frequency seen by the output transformer. A nominally 8 Ω woofer paralleled with an arbitrary tweeter is not a qualified load. Any mode switching must retain a valid load on the tube amp.

The user's cabinet is open-backed and was sold as a 5E3 shell. A hi-fi woofer needing a sealed/ported alignment cannot be assumed to work as intended there. A coaxial assembly may be worth comparing if it avoids a second baffle opening, but it is only an option, not an accepted substitution or proven fit.

### Later clarification: hi-fi principles in the acoustic build

After the branch upload, the user emphasized accurate acoustic reproduction with tube circuitry and suggested a hi-fi element to the design. Preserve that direction. A tube amplifier can be engineered for low distortion and controlled response; “tube” does not automatically mean deliberate breakup. Conversely, audible warmth is not a guaranteed property of tubes or the same claim as accuracy. Retain a clean foundation and evaluate intentional tonal shaping separately.

Clean output power must follow intended listening level/distance, speaker sensitivity and transient headroom, plus transformer, thermal and cabinet limits. The user did not select a high wattage. Do not automatically enlarge the power supply or choose huge transformers from the quoted discussion. A raw pickup does not contain the same body/room information as a microphone recording; amplification cannot recover information it never received. Loading, EQ, pickup response, crossover and loudspeaker directivity all need attention. A purpose-built acoustic amp may intentionally limit sub-bass and provide feedback controls rather than reproduce the entire hi-fi bandwidth at full power.

Manufacturer example supporting tube hi-fi feasibility: [McIntosh MC275 technical brochure](https://www.mcintoshlabs.com/-/media/Files/mcintoshlabs/DocumentMaster/us/1773_MC275.pdf). This is an example, not the selected circuit or an authorized expensive-parts direction. No new hardware, simulation or acoustic performance validation is claimed by this clarification.

## 5. Fixed cabinet and physical evidence

**The yellow-tweed cabinet and reverb tank are already delivered.** Do not resume cabinet shopping, ask whether they arrived, or make Mable's unanswered datasheet requests the only path forward. The user explicitly rejected black; red tweed was mentioned and withdrawn. Keep this cabinet.

Canonical dimensions: `engineering/whole-amp/mechanical/fit-register.json`. The following are a reading guide, not a second editable dimension source:

| Item | Recorded evidence and limitation |
|---|---|
| Clear front/rear width A | User reports 467 mm at both locations. Exact height/datum and uncertainty are unverified. |
| Depth B | User reports 160 mm, interpreted as baffle rear face to cabinet rear edge under the measurement card. This is not a proven unobstructed chassis depth. |
| Opposite speaker-hole centres C1/C2 | User reports 294 mm both ways. |
| Adjacent speaker-hole centres | Top, bottom and right side each reported 210 mm. An ideal 210 mm square implies about 297 mm diagonal, not 294 mm. Preserve the discrepancy; use a printed template/trial fit for final qualification. |
| Supplier outer dimensions | 508 mm wide, 420 mm high, top/bottom depths 215/242 mm. These are not internal clearance dimensions. |
| Supplier baffle drawing | 468 × 380 mm, nominal 270 mm cutout and 312 mm bolt circle. Actual reported hole spacings conflict with this drawing. Do not drill from the 312 mm circle. |
| Supplier top opening | Straight section 312 mm, stepped width 344 mm, depth 67 mm, corner radius 31 mm; fit tolerances/support geometry unconfirmed. |

All three supplied drawings and the received-versus-drawing review are retained. Read `engineering/whole-amp/mechanical/review/received-vs-drawing.md`, `measurement-guide.md` and `repack-work-order.md`.

There is **no qualified populated whole-amp assembly model**. Final chassis supports, six tube/socket envelopes and extraction paths, transformer envelopes, control/jack bodies, tank body/mounts/cables and speaker depth clearance remain open. Board outlines are replaceable drafts. The historical two-plane board-only layout is not an accepted assembly arrangement. Do not convert 467 mm clear width into permission to build a 467 mm chassis with zero assembly tolerance.

## 6. Original amplifier and current native artifacts

Both builds explicitly require proper replaceable tube sockets. For the inherited tube lineup, that means four suitable 9-pin sockets for the 12AX7s and two 8-pin octal sockets for the EL34s. Include exact socket geometry, mounting, ratings, retention/shielding as required and tube-removal clearance. No exact socket or chassis-versus-PCB mounting choice is established by this requirement.

The original source is `Renegade Tube Amp.pptx`; inspection and as-printed BOM are under `sources/original-ppt/`. It is **four 12AX7 and two EL34 tubes**. The cabinet's 5E3 name does not make this a Fender 5E3 circuit. Earlier added tube-reverb designs are superseded; current reverb is solid-state driven.

Current native full schematic:
`engineering/whole-amp/reverb-600/cad/Renegade_220V_Reverb.kicad_sch`

Current electrical contract:
`engineering/whole-amp/reverb-600/circuit.json`

Current four-board reconciliation drafts:
`engineering/whole-amp/pcb-measured-r/boards/Renegade_{Main,Power,Control,Reverb}.kicad_pcb`

Read their module contracts before editing. The full schematic has 18 sheets, 230 references and 597 connected pins in the recorded checks. Thirteen original amp/supply/control sheets were preserved in 600R-1. ERC at that checkpoint has zero errors and one retained GND/PE alias warning. Those checks are historical evidence until affected changes are rechecked.

600R-1 changes: R601=1 MΩ and R602=100 kΩ attenuate the send; R612=100 kΩ carries passive dry from FX_RETURN to MIX_OUT; R618=1 MΩ adds wet from WET_AC after C607/R617. U12 handles wet only. Dry is independent of the reverb knob/mute but has documented fixed insertion loss. Do not say dry gain equals the original circuit's gain.

The most recent four-board draft contains 93 footprint replacements/additions. Its final native pad/net audit checks 444 numbered pads, including 10 explicit no-connect pins, with zero mismatches to the contract. It is not a full paired-assembly schematic-parity claim.

| Current draft | DRC violations | Unconnected items |
|---|---:|---:|
| Main | 0 | 103 |
| Power | 0 | 38 |
| Control | 0 | 95 |
| Reverb | 0 | 0 |

The three routing gaps result from removing copper invalidated by exact-package changes. Historical fully routed boards under `engineering/whole-amp/pcb/` do not implement all new selections/current reverb nets. Do not overwrite the current drafts with those just to obtain a clean routing count.

## 7. Received spring tank and simulation

Confirmed photographed label: **M8EB2C1B**, **R2610270015**. Front view: right white RCA marked IN, left red RCA marked OUT. Three long reverb springs are visible; the four small suspension springs are separate.

Supplier statement: input impedance 600 Ω, output 2250 Ω, medium decay, insulated input shell, grounded output shell, no transport lock, horizontal/open side down. AC test frequency/level and current ratings remain unknown; electrical shell bonding has not been measured.

User-reported DT9205A readings on the 2k range: shorted tips `000`; IN `.076` → 76 Ω DC; OUT `.235` → 235 Ω DC. No temperature, meter accuracy check or reading photographs were supplied. These are finite winding resistances, not proof of complete function or safe drive current. Do not measure input-to-output to obtain either coil resistance; each is centre contact to its own socket shell on a disconnected tank.

Six received photographs, hashes and measurement/Chinese-label instructions are under `engineering/whole-amp/mechanical/evidence/received-tank-2026-11-20/` and its linked review. Actual tank dimensions remain unmeasured; an Accutronics reference envelope is not an exact Mable measurement.

The latest measured-resistance run completed 18 AC cases, 12 coil sensitivity cases and six transient cases; eight scoped criteria pass. It still assumes seller AC impedances apply at 1 kHz and derives surrogate inductances of approximately 94.724 mH input and 356.140 mH output. These are **not measured inductances**.

Nominal surrogate drive peaks at 6.728 mA RMS around 356 Hz for a 20 V peak source behind 100 kΩ at full send trim. Maximum across all sensitivity assumptions is 7.996 mA RMS. Neither is a safe tank-current specification or approved real-tank operating setting. Copper heating uses I_RMS² times DC resistance; maximum permissible temperature and mechanical/magnetic limits are still unknown. R605's 220 Ω series resistor is not a regulated constant-current source.

The model does not simulate spring acoustic transfer, actual wet loudness, expression control, real supply/thermal faults or complete tube/output-transformer performance. Whole-amp simulations separately exhibit unresolved high-frequency ringing and timestep sensitivity with the real-transformer surrogate. The ideal-transformer result is a mathematical reference, not a measured output-power rating. Details and failures remain in `engineering/whole-amp/simulation/README.md` and `reverb-600/review/measured-resistance-results-2026-11-20.md`.

## 8. Parts, controls and cost status

Canonical reference selection: `engineering/component-selection/coverage.json`. Sourcing candidates: `candidate-register.json`. Generated selected BOM: `selected-engineering-bom.csv` and `selected-engineering-summary.json`.

At the electric checkpoint, selected coverage is 36 MPNs / 117 positions / 48 of 127 groups. The dated selected-subset MOQ estimate is RMB335.59. It excludes many parts, shipping and fabrication and is not a fresh quote or full build cost. Do not promote candidate records to selected or treat old stock observations as current.

Latest selections include KNSCHA MEB104J63V82CB0236 at 11 positions and MEB105J63V82CB0235 at C606/C607. Exact manufacturer drawings and custom footprints are retained. R605's 2 W flameproof candidate still lacks a suitable confirmed domestic low-quantity source; R616's fault rating is unresolved. Tubes/sockets, final mains/output/choke/aux magnetics, protective parts, speaker system, several pots/connectors and many other items remain open. Original Hammond names are reference identities, not approved 220 V/50 Hz build choices.

Keep the accepted pointer/chicken-head knob styling and match actual shaft diameter/type/length and panel stack. See `brain/records/CMP-013-pointer-knobs.md`. Do not treat a visual knob choice as shaft-fit verification.

Faceplate REVERB adds wet while dry stays constant. Expression-pedal requirement is confirmed but **not implemented**: passive rocker pot controls wet only, heel=dry, toe=faceplate maximum, unplugged=normal faceplate operation. Audio remains inside the amp; pedal cable carries protected low-voltage control. Preserve the separate debounced channel/reverb on-off footswitch. Pot value/taper, pinout, connector and gain-control circuit are not selected. Read `engineering/whole-amp/expression-control/requirements.md`.

## Feasibility and what actually changes

Engineering assessment at handoff: this is a feasible design-development direction using available techniques and substantial existing project work. It is not yet a proven fit or a construction-ready design. The missing evidence is specific and testable; it does not establish that the concept is out of reach. No cost, loudness or fit guarantee can be made before the remaining constraints are closed.

| Existing work | Acoustic treatment |
|---|---|
| Original Renegade clean-channel topology | Starting candidate; quantify gain, input/output headroom and frequency response before changing values. |
| Phase inverter and EL34 output pair | Starting candidate for clean tube amplification; validate operating point, distortion, stability, transformer/load and actual clean power. |
| Original dirty channel | Preserved in the source/electric build. Its role in the acoustic branch needs an explicit scope decision; do not silently remove it or force acoustic sound through intentional overdrive. |
| Mains/heater/bias/control supply work | Reuse requirements and calculations; finish exact220V/50Hz transformer/load/thermal/protection qualification. These were unresolved before the branch split. |
| Spring tank, drive/recovery and wet controls | Reuse as a starting subsystem; maintain measured resistance and uncertainty limits. Recheck loading and gain after acoustic changes; expression circuit remains unimplemented. |
| Selected general-purpose parts and libraries | Retain evidence and reuse suitable parts after checking new stresses and packaging. A shared MPN does not prove unchanged qualification. |
| Cabinet and measured mounting evidence | Fixed existing shell. Actual populated fit still needs a dimensioned assembly and template/trial-fit evidence. |
| Input interface | Add the authorized op-amp buffer and appropriate loading/protection/headroom for the actual guitars. |
| Tone shaping and clean gain allocation | Review and adjust for acoustic reproduction. A buffer alone does not undo electric-guitar voicing or prevent later-stage clipping. |
| Speaker system and output load | New acoustic selection: main driver, tweeter and crossover designed together, with open-back suitability, response, sensitivity, complex impedance and cabinet fit considered. |
| PCB drafts | Starting artifacts and reusable layout/library work. They are not finished acoustic boards; finish the acoustic block design and exact footprints before rerouting. |

There is enough information now to audit the existing clean path, develop a bounded buffer candidate, set up comparative simulations, research exact driver pairs and prepare dimensional fit templates. There is not yet enough evidence to order a complete acoustic parts kit, release a PCB/crossover or promise an assembly fits.

Critical remaining inputs/checks: intended playing level and setting (home, solo performance, band), guitar pickup interfaces, selected drivers with acoustic/impedance data, exact transformers and tube/socket envelopes, actual clearances around chassis/speaker/tank, real-transformer simulation issues and bench validation. Do not demand a perfect data sheet for every item before independent progress; use qualified measurements or bounded models where appropriate and label their limits.

The next chat should first produce a short **keep / modify / replace** review of the starter amp, an agreed clean-performance target and an updated fit budget. Then implement the smallest justified set of acoustic changes. Preserve the source, existing evidence and electric branch throughout.

## 9. Next work sequence for the acoustic chat

1. Confirm branch isolation and capture any new feedback before changing dependent artifacts.
2. Identify actual guitar interfaces as far as available evidence permits. Continue independent component/fit research meanwhile.
3. Write an acoustic task card and system targets: useful clean level, frequency response, acceptable coloration, noise, feedback control and power/load limits. Distinguish user preferences from proposed numerical limits.
4. Select and model an exact op-amp buffer with realistic source/loading, active-guitar headroom, protection, supplies and startup behavior. Reuse qualified parts where appropriate, but do not select a device solely because it is in the reverb BOM.
5. Select a documented, domestically obtainable quantity-one speaker/tweeter pair and crossover approach. Validate open-back suitability, mounting/cutout/depth and interference with the whole amp. Keep unresolved physical facts explicit; use a printable template/trial fit rather than repeated confusing tape questions.
6. Design the crossover from driver impedance/response, include tweeter level/protection and verify the complete output-transformer load. Establish whether inherited clean-channel voicing must change and document why. Obtain a user decision only for a material departure from authorized scope.
7. Update the acoustic electrical contract, native schematic, exact BOM, PCB/harness/panel and mechanical interface together. Preserve the electric commit and historical evidence. Recheck affected simulations, ERC, pad mapping and DRC; then assess populated fit.
8. Keep an explicit bench and release plan. Neither simulation nor clean DRC establishes thermal safety, physical fit, acoustic quality or a complete build-ready package.

## 10. Tools and reproducibility

Installed at handoff: KiCad CLI 10.0.6 at `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`; bundled Python at `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`. System Python does not import pcbnew. Ngspice is accessed through the existing `engineering/whole-amp/tools/spice_runtime.py` adapter; read its contract and the simulation factories before rerunning.

Noninteractive CLI DRC required approved execution outside the restricted sandbox on this Mac; the sandbox attempt crashed, while the same local CLI succeeded with escalation. This does not authorize GUI takeover. Some pcbnew SWIG objects must be retained through save/reload; the current factories preserve IO/board/removed-item wrappers. Reuse those lessons and verify actual native reload, not just process exit.

Current creation factory `pcb-measured-r/tools/update_boards.py` refuses existing outputs. `refine_drafts.py` removes Reverb routing; do not run it over later edits. `route_reverb.py` is a low-voltage grid router, not qualified for mains/HV routing. `finish_layout.py` contains revision-specific corrections. `check_boards.py` is a read-only pad-contract audit. See `pcb-measured-r/CONTEXT.md` for operation order. Preserve `NATIVE_EDIT_GUARD` files.

Project-local footprint libraries are included. Some historical tool commands and skill links are Mac-specific; inspect paths on another machine. Sources, PDFs, ZIPs, logs, raw waveforms and photographs are included in Git. macOS Finder metadata, Python bytecode, transient KiCad locks and secret env files are excluded; no project sources or simulation evidence were intentionally dropped.

## 11. ICM and communication requirements

Use Circuit Design Skill Ladder, Physical Design Agent Ladder and relevant ICM skills. Each working module has one job and a CONTEXT.md with inputs/process/outputs/human check. Keep factories separate from generated CAD, evidence and runs.

Immediately append meaningful new user feedback to `brain/feedback/events.json`, using the next free FB ID. Canonical requirements belong in the root handoff, dimensions in the mechanical register, parts in coverage/dossiers. Link facts rather than duplicating editable databases. Rebuild:

```sh
python3 brain/tools/build_index.py
python3 brain/tools/build_project_catalog.py --as-of YYYY-MM-DD
python3 /Users/appleadmin/.codex/skills/icm-check/scripts/icm_check.py . path/to/changed/module
```

Use the current client date when writing new records. The handoff date above remains historical. Scoped checks and material catalogs were clean at the checkpoint; repeat after relevant changes.

Speak in aircraft-mechanic English: plain words, exact units, clear findings and short steps. Keep the user informed during long work. They dislike being interrupted by desktop automation. **Before taking control of Mail, play a chirping sound and obtain immediate confirmation.** Prior supplier-message permissions do not override that interaction rule. Do not open Mail just to continue this handoff. Research through background tools where possible.

The user already repeatedly requested the tank datasheet from Mable. Continue with available evidence and carefully bounded tests rather than sending the same request again. The cabinet/tank procurement discussion is history; both are on hand. The user will create the acoustic chat themselves.

## 12. Suggested first message for the new chat

> Continue the Acoustic Guitar Amp build on `acoustic-guitar-amp` in davidgrahamsites/Tube-Amp. Read `ACOUSTIC_HANDOFF.md`, `BUILD_VARIANT.md` and `AGENTS.md` first. Preserve the electric branch. Design the op-amp input buffer and select an acoustic speaker, tweeter and crossover that fit my delivered yellow-tweed cabinet. Use the recorded guitar/tank/cabinet evidence, keep ICM updated, and distinguish verified results from unresolved fit and safety checks.
