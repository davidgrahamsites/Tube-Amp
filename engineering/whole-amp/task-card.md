# Whole-amplifier PCB requirements audit / current task card

Owner: PCB integration; circuit, component-selection and mechanical modules own their respective inputs and corrective work.

Inputs: original six-tube Renegade architecture, current 600R-1 circuit contract, four active `pcb-measured-r/boards` projects, exact-part coverage, received-cabinet fit register, user requirements and all 364 imported design rules. Preserve the separate acoustic build and historical CAD.

Authorized operations: reversible design/file work, research, simulation, checks and repository synchronization. No purchase or fabrication upload. Mail has a separate chirp-and-immediate-confirmation requirement.

Process: inspect native settings and every board, run baseline and strict-copy DRC, check all pads and board interfaces, inspect copper previews, map requirements to observed evidence and explicit closure work. Preserve native source hashes during this audit.

Outputs: [full audit](pcb-measured-r/review/requirements-audit.md), per-rule matrix, native/strict DRC, inventory, source manifest, ICM VAL-018 and current handoff. No CAD corrections or new simulations were performed in this audit.

Current result, November 21: audit complete; all four PCBs fail fabrication release. Main/Power/Control have 105/39/99 unconnected items. Reverb connectivity passes, but its placement/return/feedback qualification is incomplete. Exact parts, local bypass and relay suppression, terminal envelopes, current/insulation rules, expression control and complete cabinet assembly require work.

Dependencies: delivered cabinet and tank are on hand. Use measured dimensions, not stale supplier-purchase questions. Resolve remaining exact magnetics, speaker, sockets, connectors and protective parts; tank AC characteristics/safe drive current, full-amplifier ringing, supervisor corners and R40 pulse qualification remain open.

Next work: component/assembly envelopes, placement and protection corrections, supported per-net rules and returns, complete routing, then repeat native/contract/visual checks and mechanical/CAM review. Preserve functional blocks, independent rear-cover removal and full drill/driver access.

Done condition for fabrication: consistent exact-part schematic/BOM/PCB/harness and verified populated fit with no applicable open release gates. Human check: inspect the complete assembly, tool/extraction paths and electrical protection before release; subsequent physical electrical/audio/thermal/EMC tests are required before claiming a working qualified amplifier.
