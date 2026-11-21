# PCB measured-R integration boards
Owner: Renegade PCB integration. One job: Hold editable native PCB drafts.
Inputs: ../pcb historical native boards, ../reverb-600/circuit.json and ../../component-selection coverage/footprints (paths relative to module root).
Process: tools/update_boards.py replaces documented selected footprints and reconciles current reverb pad nets. Preserve original boards; remove affected copper before rerouting.
Outputs: boards/*.kicad_pcb and review/integration.json plus native DRC reports. All are drafts; no fabrication package.
Human check: inspect pads, courtyards, remaining routing, full six-tube assembly and delivered-cabinet clearance. Expression pedal is still pending.
