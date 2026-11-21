# Fit calculation factory
Owner: integration agent. One job: calculate screens from the canonical register.
## Inputs
`../fit-register.json`.
## Process
Run `python3 check_fit.py`; no network, supplier access or CAD mutation. Formula checks are distinct from actual assembly qualification.
## Outputs
`../review/fit-screen.json`.
## Human check
Compare assumptions and missing dimensions with actual parts before treating a result as usable fit.
