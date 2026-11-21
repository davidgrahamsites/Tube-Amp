# Mechanical fit module
Owner: Renegade integration agent. One job: determine cabinet fit from traceable dimensions.
## Inputs
`../board-plan.json`, current native board drafts under `../pcb-measured-r/boards/`, cabinet images under `../../solid-state-reverb/evidence/`, supplier snapshots in `evidence/`, and root handoff.
## Process
Edit `fit-register.json` as the single dimensional interface. Keep unknowns null. Run `tools/check_fit.py`; use `tools/panel_study.py` and `tools/print_panel.py` for the separate control-panel proposal; inspect `review/fit-review.md` and generated screen. No automatic CAD mutation or fabrication release.
## Outputs
`fit-register.json` supplies dimensional facts/unknowns to electrical and mechanical design; `review/` records scoped results. Stable check code is in `tools/`; source material stays in `evidence/`.
## Human check
Confirm actual cabinet/tank identity and measure installed chassis, speaker, tube and transformer clearances before drilling or ordering.

Current user measuring instructions: [illustrated start/end guide](review/measurement-guide-2026-11-21.md). This generated picture is guidance, not dimensional evidence. Preserve the user-reported A/B/C readings until new measurements arrive.
