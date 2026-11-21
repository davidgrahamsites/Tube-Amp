# PCB measured-R integration tools
Owner: Renegade PCB integration. One job: Reconcile existing boards without modifying historical originals.
Inputs: ../pcb historical native boards, ../reverb-600/circuit.json and ../../component-selection coverage/footprints (paths relative to module root).
Process: use the ordered operation list in ../CONTEXT.md. Creation, placement refinement, routing, DRC correction and read-only audit are separate scripts. Creation refuses overwriting existing drafts; refinement removes Reverb routing and must not be rerun over later edits. Execute with KiCad bundled Python. Native CLI DRC remains authoritative for copper connectivity and spacing.
Outputs: boards/*.kicad_pcb and review/integration.json plus native DRC reports. All are drafts; no fabrication package.
Human check: inspect pads, courtyards, remaining routing, full six-tube assembly and delivered-cabinet clearance. Expression pedal is still pending.
