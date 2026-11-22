# PCB measured-R integration review
Owner: Renegade PCB integration. One job: Hold pad-map, DRC, source hashes and review outputs.
Inputs: ../pcb historical native boards, ../reverb-600/circuit.json and ../../component-selection coverage/footprints (paths relative to module root).
Process: tools/update_boards.py replaces documented selected footprints and reconciles current reverb pad nets. Preserve original boards; remove affected copper before rerouting.
Outputs: boards/*.kicad_pcb and review/integration.json plus native DRC reports. All are drafts; no fabrication package.
Human check: inspect pads, courtyards, remaining routing, full six-tube assembly and delivered-cabinet clearance. Expression pedal is still pending.

November21 copper workflow: `tools/audit_copper.py` reads current boards and writes `review/copper-audit.json`; it does not establish current capacity. `tools/chamfer_candidates.py OUTPUT_DIR` writes non-overwriting temporary candidates only. Adoption requires native DRC, pad-map and visual review under unchanged project rules. Only Reverb was adopted in `review/chamfer-integration.json`; Main/Power/Control candidates were discarded. See `routing-requirements.md` and [VAL-017](../../../../brain/records/VAL-017-copper-and-component-review.md). Human check: inspect junctions/width transitions and verify current, voltage-drop and return paths before release.
