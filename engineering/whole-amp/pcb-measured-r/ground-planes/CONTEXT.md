# Board ground-plane integration
Owner: PCB integration. One job: implement and verify copper-reference zones against the existing signal/earth contract.
Inputs: fixed baseline native boards and source, ../boards rules, ../../reverb-600/grounding-contract.json, and primary grounding guidance linked in ../review/ground-plane-review-2026-11-25.md.
Process: tools/build_reverb.py creates one temporary candidate using the supported KiCad API; tools/check.py independently verifies the authorized delta. Review native strict DRC, filled copper and current-loop map before adoption. No wholesale fill of mains/HV boards.
Outputs: contract.json, review.md and results evidence; active native boards are the product. Factories remain under tools; disposable board copies remain outside the project.
Done for first stage: Reverb B.Cu GND plane filled and connected, no floating islands or new strict findings, all original footprints/traces/drills/nets preserved, mounting exclusion and visual checks documented. Other boards, assembled noise, current budgets and populated fit are separate unfinished stages.
Human check: follow sensitive tank-recovery and driver/power return paths in the filled copper, inspect mounting hardware insulation and actual harnesses, and verify populated-board noise and heating before release.

Current hold: the first candidate exposed tube-level FX_RETURN/MIX_OUT paths. The blanket low-voltage classification is rejected; no candidate is adopted. See review.md. T03 logical bond work is complete; remaining physical return and voltage-domain qualification is distinct.
