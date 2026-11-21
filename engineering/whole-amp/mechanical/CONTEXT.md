# Mechanical fit module
Owner: Renegade integration agent. One job: determine cabinet fit from traceable dimensions.
## Inputs
`../board-plan.json`, existing native boards under `../pcb/`, cabinet images under `../../solid-state-reverb/evidence/`, supplier snapshots in `evidence/`, and root handoff.
## Process
Edit `fit-register.json` as the single dimensional interface. Keep unknowns null. Run `tools/check_fit.py`; inspect `review/fit-review.md` and generated screen. No automatic CAD mutation or fabrication release.
## Outputs
`fit-register.json` supplies dimensional facts/unknowns to electrical and mechanical design; `review/` records scoped results. Stable check code is in `tools/`; source material stays in `evidence/`.
## Human check
Confirm actual cabinet/tank identity and measure installed chassis, speaker, tube and transformer clearances before drilling or ordering.
