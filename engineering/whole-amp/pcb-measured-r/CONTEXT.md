# PCB measured-R integration module
Owner: Renegade PCB integration. One job: Own the current four-board reconciliation draft for 600R-1 and selected parts.
Inputs: ../pcb historical native boards, ../reverb-600/circuit.json and ../../component-selection coverage/footprints (paths relative to module root).
Process: tools/update_boards.py creates new drafts and refuses to overwrite them. tools/refine_drafts.py corrects placements and hides BOM metadata, then tools/route_reverb.py routes the low-voltage reverb board. tools/finish_layout.py applies documented DRC corrections. Run native CLI DRC on all four boards, then tools/check_boards.py audits current pad nets and source hashes. Do not rerun creation/refinement over later native edits.
Outputs: boards/*.kicad_pcb and review/integration.json plus native DRC reports. All are drafts; no fabrication package.
Human check: inspect pads, courtyards, remaining routing, full six-tube assembly and delivered-cabinet clearance. Expression pedal is still pending.

Current result: [measured-resistance and PCB review](../reverb-600/review/measured-resistance-results-2026-11-20.md). Reverb is routed under current rules; Main, Power and Control routing is incomplete. Zero DRC findings do not qualify unselected packages, thermal clearances or physical fit.
