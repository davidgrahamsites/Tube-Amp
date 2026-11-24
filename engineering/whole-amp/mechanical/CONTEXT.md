# Mechanical fit module
Owner: Renegade integration agent. One job: determine cabinet fit from traceable dimensions.
## Inputs
`../board-plan.json`, current native board drafts under `../pcb-measured-r/boards/`, cabinet images under `../../solid-state-reverb/evidence/`, supplier snapshots in `evidence/`, and root handoff.
## Process
Edit `fit-register.json` as the single dimensional interface. Keep unknowns null. Run `tools/check_fit.py`; use `tools/panel_study.py` and `tools/print_panel.py` for the separate control-panel proposal; run `tools/service_study.py` for the separate removable-chassis service concept; inspect `review/fit-review.md` and generated screen. No automatic CAD mutation or fabrication release.
## Outputs
`fit-register.json` supplies dimensional facts/unknowns to electrical and mechanical design; `review/` records scoped results. Stable check code is in `tools/`; source material stays in `evidence/`.
## Human check
Confirm actual cabinet/tank identity and measure installed chassis, speaker, tube and transformer clearances before drilling or ordering.

Current user measuring instructions: [illustrated start/end guide](review/measurement-guide-2026-11-21.md). This generated picture is guidance, not dimensional evidence. Preserve the user-reported A/B/C readings until new measurements arrive.

Current received opening/height are recorded under cabinet.user_measurements (FB-073/074). Service constraints live under chassis_service_study; illustration and area checks are not dimensioned CAD or fit approval. No repeat measurement request is active.

Output-protection package and service constraints: [socket-side resistor handoff](review/output-protection-fit.md). No populated chassis/tool clearance is inferred from candidate body dimensions.

PCB envelope diagnostic: fit-register.json/pcb_envelope_study owns trial placement and allowance parameters. tools/board_fit_cad.py consumes the read-only native mechanical-inventory.json from pcb-measured-r and generates review/board-fit-diagnostic.FCStd/STEP/JSON. tools/plot_board_fit.py renders the receipt. Read review/board-fit-review.md: actual board outlines/holes are distinct from unqualified component/support/thermal/tool geometry. Drill clearance deferred by user until November25.

Socket envelope seam: component-selection/socketing/socket-envelope.json is consumed read-only by tools/check_socket_fit.py. review/socket-fit-checks.json compares provisional DIP bodies and holes with native boards; it does not establish populated chassis, retention or drill access.
