# Through-chassis execution card

Owner: Renegade integration. Updated 2026-11-24. Authority: FB-114–116 and the canonical handoff. This card interprets the six requested scopes; it does not replace the ordered [task queue](tasks.md).

## Inputs and process

Use the active `reverb-600/circuit.json`, current `pcb-measured-r` boards, exact component coverage and the measured cabinet contract. Use the latest verified package checkpoint (VAL-025 follows3efa8d9); preserve unrelated in-progress edits. Select available parts before freezing dependent values, footprints or geometry. A substitute reopens its affected electrical and mechanical checks.

All six tubes require sockets. IC sockets remain the default; FB-117 permits a documented device-specific exception if socketing materially harms operation. No exception is currently adopted. Include regulators, the supervisor and any future effects-loop IC. Surface-mount adapters are only candidates until their contacts, pin map, spacing, retention, bypass placement and thermal path are qualified. Never equate a DIP footprint with an installed socket. Include socket height and extraction space in the populated assembly.

## Six scopes and closure evidence

| Scope | Queue | Remaining evidence |
|---|---|---|
| 1. Transformer/output stage | T04/T08 | Exact available transformer; winding/DC/current/frequency evidence; feedback, treble and load-corner qualification; approximately 25 W reported against distortion. Generic parameter sweeps remain experiments. |
| 2. Effects SEND/RETURN | T05 | Available socketed implementation at the existing interfaces; resolve 20 kHz failures; loading, headroom, overload/recovery and supply requirements. |
| 3. Power/protection | T06/T07 | Both 120 V/60 Hz and 220 V/50 Hz modes; supply/load/heat budget, startup/brownout/shutdown, protection, local bypass and spring-driver limits. |
| 4. Exact parts/footprints | T08/T12/T13 | Manufacturer identities, drawings, pin maps, round/rectangular-lead and slot tolerances, readable schematic and native parity. Chinese purchase route, quantity/MOQ, dated stock and Shanghai delivery basis for every purchase item. |
| 5. Harnesses | T09 | Headers AND mates AND contacts, insulated wire, shielding, crimp method, strain relief, cable ties, service loops and mating/extraction envelopes. |
| 6. Populated three-board chassis | T10/T11 | Audio/power/reverb physical boards with all functional blocks preserved; six tubes/sockets, magnetics, speaker, tank, heat shields, wiring and fasteners. Independent rear removal, chassis extraction and actual drill access. |

Outputs are checked engineering artifacts in their modules, linked evidence and current handoff/catalogs. The design is not build-ready merely because a simulation finishes. Fabrication packages and physical commissioning remain T15–T18 gates.

## Current next actions

1. Inventory socket requirements against every active IC/tube reference, including parts whose package must change; retain pending qualification explicitly.
2. Resolve component constraints in parallel with necessary circuit calculations: regulator contact/heat budget, transformer and capacitor geometry, speaker fit and exact connector mating sets. Work sequentially within each owned module; no independent-worker delegation implied.
3. Rerun affected simulations with traceable inputs. Carry adopted parts into readable CAD only after pin/function and package evidence agree.
4. Repack the populated assembly, then route the three physical boards and rerun electrical/mechanical checks.

## Physical dependencies and human check

Actual drill envelope remains deferred until November 25. Cabinet depth datum, actual speaker fit and 1:1 assembly checks remain open; do not replace them with inferred measurements. Domestic shipping policy establishes a supplier route, not an exact delivered price or accepted order. No purchase, supplier contact or fabrication upload is authorized by this card. At review, trace one part from stock/datasheet through schematic pin, socket/contact, PCB hole and assembly clearance.

## Auxiliary-supply checkpoint — November24
[VAL-026](../../brain/records/VAL-026-auxiliary-supply-envelope.md) adds72raw-supply cases,4refinement runs and3unadopted820Ωpreload comparisons. Evidence checks pass;48base cases have engineering flags. Raw-winding/thermal assumptions remain unqualified. Contact screening has not selected a regulator socket. Native CAD unchanged; exact auxiliary magnetics, preload integration, startup/reset, socket/heatsink and all populated-fit gates remain open.

## R215 checkpoint — 24 November 2026

[VAL-027](../../brain/records/VAL-027-preload-native-integration.md):5V preload integrated and native delta/holes checked;72raw-supply runs plus2refinements complete. Minimum-load defect fixed within declared bounds; no new ERC/DRC findings. Transformer range/current, reset release, socket implementation and populated chassis remain open. Current native source hash is recorded in the preload checks, superseding prior byte-preservation claims only for the declared R215 addition. Next: use the existing supervisor/relay-chain candidate review, select exact socket-compatible parts and close brownout behavior; then exact auxiliary transformer and heatsink/contacts. No Chinese purchase-readiness or fabrication claim.

## Control switching checkpoint — November 24

[VAL-028](../../brain/records/VAL-028-control-driver-reset-checkpoint.md) integrates logic-level relay drivers/local clamps with native preservation and drill-delta checks. 55 simulation runs have retained provenance and explicit limits; supervisor/carrier/rail-collapse qualification remains open. Current Control has 84 unconnected items and 13 existing DRC findings. Functional blocks and fixed mounting holes are preserved. No three-board fit or fabrication release is implied.

## Reset-edge and socket-envelope checkpoint — November 24

[VAL-029](../../brain/records/VAL-029-reset-edges-and-socket-fit.md) adopts U1C/D edge conditioning with exact native/route/drill preservation checks. Control79 unconnected/13 existing DRC; no new ERC/DRC finding. G50 release margin, replacement carrier, physical MR/brownout and clock coincidence remain open. TE socket candidates have domestic stock and dimensional evidence; current five DIP footprints need 1.0 mm holes and larger courtyards. The 10.38 mm assembly height and provisional extraction reserve are consumed read-only by the mechanical screen; populated three-board fit and drill access remain unqualified. Next: exact supervisor/carrier and socket footprint qualification, then populated placement.

## November24 socket and partial-tool checkpoint

[VAL-030](../../brain/records/VAL-030-sockets-brownout-tool-measurement.md): five DIP socket drafts corrected with52 larger holes and C352 clearance repair; no new native findings. Brownout runs complete but threshold/clock/collapse qualification remains open. User supplied46mm chuck diameter; earlier deferral is superseded only for that dimension. Body/bit reach and actual access still pending. Existing board support trial fails; no populated chassis release.

## November24 U12 routing follow-up

[VAL-031](../../brain/records/VAL-031-u12-corner-and-copper-coverage.md) repairs the reported U12 square T and enlarges eight chamfers, with fresh exact native/drill/DRC/socket checks. Eleven further outside-pad/via branch candidates remain. Copper inventory now covers all134 board/net entries, including wholly unrouted nets. Current capacity and populated three-board fit remain unqualified.

## November24 branch and divider checkpoint

[VAL-032](../../brain/records/VAL-032-reverb-branches-divider-stability.md) adopts seven additional rounded Reverb forks with zero native DRC/open connections and unchanged widths/drills. Four other-board branch candidates remain. A separate divider comparison improves shorter endurance margins but retains failed extended screens and incomplete exact Chinese stock evidence. Supervisor/carrier, current-path qualification and populated three-board fit remain open; complete drill access is still pending after the46mm chuck measurement.

## November 25 RETURN supply diagnosis

[VAL-040](../../brain/records/VAL-040-return-supply-diagnostics.md) adds eight causal cases and twelve follow-up cases. A 50 Ω rail-isolation candidate retains 100 nF bypass and completes both 20 kHz conditions with numerical refinement checks. It remains outside native CAD/BOM; no integrated wet-mix, actual supply, socket, thermal or Shanghai-purchasing qualification. Continue T04/T05 envelope and costed discrete recovery comparison; all six scopes remain open.

November 25 expression follow-up (VAL-043): nine causal cases diagnose the earlier ±12V timeout as an impossible model operating point; corrected starts agree across seeds and timestep refinement. Practical PNP/mirror bias candidate:24cases,17complete and7failed OP cases retained; nominal1kHz THD about0.05901%, control ramp reaches off.133evidence checks pass; low-current direct solves, trim margin, thermal offsets, protected pedal, sockets and native integration remain open. Exact Diodes candidate has Chinese LCSC608stock/MOQ1; marketplace alternatives now included by FB-126. Native boards and functional blocks unchanged. All six scopes remain active.

November25 expression follow-up (VAL-044): nominal trim range improved in a separate candidate; seven operating-point failures remain. Causal isolation found an unsettled transient-fallback OP despite reported solver success.152 evidence checks pass with qualification false. China-sourceable Bourns trim candidate and manufacturer pedal wiring evidence recorded; exact purchase/footprint/control-port/native integration remain open. All six scopes remain active.

November25 stationary-controller checkpoint: [VAL-045](../../brain/records/VAL-045-expression-stationary-dc.md) resolves the sampled direct-OP failures with explicit settling:24cases and107evidence checks pass. Time refinements agree; weak-shunt dry-end ABC sensitivity27.071µV remains explicit. Cold-start, protected pedal, integration, socketed parts, Shanghai purchase and populated fit remain open. Four native boards unchanged; no six-scope completion or manufacturing release.

### 2026-11-25 — VAL-046 final wet mute

K3 spare NC contact now grounds WET_AC when deenergized. Native circuit/schematic/reverb-board delta is exactly K3.11 and K3.13; no new BOM part or moved footprint/mounting hole. Fresh reverb DRC0/opens0, ERC existing1 unchanged; 39/39 scoped evidence checks pass. Eight expression rail-sequence diagnostics retain two solver failures and large fault excursions: automatic analog-rail inhibit and quiet startup remain open. Exact China C128021 listing reports stock/minimum buy1; Shanghai checkout is not verified. See engineering/whole-amp/expression-control/final-mute-review.md and brain/records/VAL-046-final-wet-mute.md. All six scopes remain active; not build-ready. Next: protected rail monitor/control interface, then expression native integration and populated fit.

### 2026-11-25 — analog-rail monitor candidate

The follow-on LM393P rail-inhibit budget enumerates10,240 endpoint cases;4/7 screens pass, with three threshold failures retained. It is not adopted. TI SLCJ016 contains an LM2903B model despite its LM393 download label, so no classic-part transient qualification was inferred. C5209 domestic listing has minimum buy1, with differing raw stock fields retained. See engineering/whole-amp/control-switching/rail-monitor-review.md. Next: improve the reference/ratio budget using exact China-sourceable parts, prove gate loading and fault timing, then integrate only after native gates.

### 2026-11-25 — corrected rail limits and buffered candidate

The earlier rail-monitor calculation used25°C bias/output-low limits; corrected full-temperature limits reduce it from4/7 to3/7. A reduced-impedance candidate reusing spareU1E passes11/11 conditional static checks with2,004 independent nodal comparisons. No schematic/PCB change. Exact resistor stock, clamp temperature behavior, startup/release timing and NPN selection remain open. See engineering/whole-amp/control-switching/rail-monitor-buffered-review.md. All six scopes remain active; manufacturing held. Next: source or requalify the precision resistor set, then qualify the complete fault-inhibit interface before native integration.

### 2026-11-25 — rail-inhibit delay candidate

[VAL-047](../../brain/records/VAL-047-rail-inhibit-delay.md) adds192 conditional timing corners and384 independent branch-current comparisons. Ten calculation screens pass, while the separate brief-fault hold screen fails:0.1–1ms pulses may not restart50ms inhibit. The direct fault path does not establish mechanical contact timing or quiet audio. KNSCHA82CL0117 domestic listing reports356/minimum1;33k TNPW candidate reports zero stock. Hot limits, full-circuit timing, exact Chinese purchasing and Shanghai delivery remain open. No native change; all six scopes remain active. Next: establish audio fault-width/contact response before adding further timing complexity, then exact parts and populated chassis checks.

### 2026-11-25 — K3 coil latency and native resistor boundary

[VAL-048](../../brain/records/VAL-048-relay-latency-boundary.md) corrects candidate R3414.7k versus native1k in all three representations. The native value fails the proposed inhibit-base allocation; no CAD change adopted.48 conditional coil cases and refined turn-off simulations prevent crediting K3 as instantaneous muting. Restore diagnostics retain numerical failures. Next: quantify the audio disturbance before contact motion, then qualify the complete supply/reset/mute interface; all six scopes and China/Shanghai sourcing/populated fit remain open.

### 2026-11-25 — passive wet-fault boundary

[VAL-049](../../brain/records/VAL-049-wet-fault-transfer.md) independently checks the passive fault calculation with six completed SPICE runs. The47kΩ/fast-shunt candidate preserves sampled dry/treble behavior but leaves the initial spike; it remains unadopted. Chinese J113/MMBFJ113 listings found, sales units and Shanghai checkout pending. Next: rail-warning lead time versus valid audio headroom, then actual gate/control qualification. No native change; all six scopes remain active.

### 2026-11-25 — audio headroom and precision monitor

[VAL-050](../../brain/records/VAL-050-rail-headroom-precision.md) rejects the former monitor against the retained10Vpeak target. A separate REF5050AIDR/LM393BIDR candidate passes14 conditional static screens with2,000 independent nodal comparisons; exact domestic stock supports small quantities. Minimum warning margin about0.27V gives only0.123ms in the isolated100mA capacitor screen. Full reference/logic sequencing, actual mute response, resistor/socket sourcing and Shanghai checkout remain open. Native boards/blocks/fit unchanged; all six scopes remain active. Next: complete startup/power-down mute interface and exact removable parts before native adoption.
