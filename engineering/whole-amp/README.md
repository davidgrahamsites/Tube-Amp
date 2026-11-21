# Whole-amplifier PCB development — v0.5

**Development only. Not build-ready or released for fabrication.** The original amplifier and v0.4 files are preserved. This revision extends PCB coverage to Main, Power and Control alongside the existing Reverb board. Socket-local grid/screen resistors and cathode sense resistors remain directly at the valve sockets; transformers, valves, panel parts and protective earth remain chassis mounted.

## Current artifacts
- `integrated/Renegade_220V_Reverb.kicad_sch` and `integrated/Renegade-v0.5-development.pdf`: separate integrated development schematic; pin partitions match v0.4.
- `bom-development.csv` and `build-plan.md`: assembly register and staged build/test plan, with unresolved purchase parts explicitly marked.
- `harness-terminals.csv`: terminal-to-net list from saved boards.
- `board-plan.json`: component-to-assembly register, provisional envelopes and footprints.
- `pcb/Main`, `pcb/Power`, `pcb/Control`: editable native board projects and assembly connectivity schematics. All three are routed, with zero native DRC, unconnected and schematic parity issues in the final saved checks. The preserved Reverb project is included in `pcb/Reverb`. This is a development revision, not a fabrication release.
- `validation/pin-partition.json`: native schematic-to-board pad/net mapping checks.
- `validation/*-drc.json`: latest native reports; failures remain visible.
- `simulation/`: reproducible full signal-path and supply stress fixtures, results, models and failure logs.
- `evidence/`: manufacturer documents and supplier contact record.

## Supplier inquiry
Sent and verified in Mail Sent on November 11 at 06:22 America/Los_Angeles, from the user-selected admin@goodgaryapps.com to mable@mableaudio.com. Cabinet choice unchanged. Internal dimensions, Shanghai availability/quote and exact spring-tank documentation requested. No order, attachments or design upload.

## Engineering limits still to close
1. Engineering review of all board placements, return paths, decoupling, heat and coupling. Main/Power were regrouped by circuit section; Control in particular still needs decoupling/thermal placement review. Routing completion is not an analog layout review.
2. Repeat native checks after any engineering changes. Main/Power/Control currently have clean assembly ERC and PCB DRC/parity reports; the integrated schematic retains the documented PE/GND alias warning. Board previews were rendered and inspected.
3. Exact remaining parts, HV standby and fuse coordination, isolated LV transformer and heatsink selection; procurement evidence in China.
4. Full amplifier model qualification: generic valve/ideal magnetics assumptions, overdrive screen stress, solid-state dry-path headroom and transient convergence.
5. Supplier-confirmed internal cabinet geometry and actual component envelopes before chassis/panel fabrication drawings. Current board sizes are provisional and not fit claims.
6. Reviewed grounding, harness, test/bring-up plan and subsequent physical fit/thermal/energized measurements.

No Gerbers are released from this revision. The previous reverb-only package is also an engineering draft, not authorization to manufacture the complete amplifier.
