# Copper current budget
Owner: PCB integration. One job: turn circuit loads into revisioned conductor requirements.
Inputs: current reverb-600/circuit.json, received tank DC resistance, declared operating bounds in contract.json, native copper audit and manufacturer source links.
Process: tools/analyze.py solves the passive loads at the six op-amp outputs, checking KCL and an independent series-RLC driver calculation. tools/check.py checks source freshness and rejects corrupted driver current, case coverage, thermal approval and source evidence. No CAD writes. Native-value and engineering-assumption ownership remain separate.
Outputs/public seam: results/budget.json and review.md. This first pass covers reverb output loads, conditional supply allocation and conductor resistance screening. It does not qualify complete mains/heater/fault currents or IPC-2152 thermal performance.
Human check: confirm real supply/output limits, tank impedance, loaded voltage drop and hot-cabinet temperature before release.
Task card: baseline f51f883; inputs above; output numerical path bounds; dependency actual stackup/thermal limits; done when declared model is independently checked and its unresolved domains explicit. One analysis pass, not six-scope completion.

CU-001: tools/check_candidate_copper.py consumes the HI-008 construction/route contract and current native files; it writes results/candidate-copper.json. copper-review.html explains the conditional track/via DC screen and fresh inventory of all four active boards. No CAD writes. Human check: obtain minimum finished foil/barrel acceptance, confirm normal input loading and complete pad/harness, thermal and protected-fault checks before release.

CU-002: supply-copper.json owns the conditional rail-current/drop/margin targets; tools/check_supply_copper.py checks current passive values and complete op-amp pin maps, recomputes the retained pure load model, and measures all candidate rail segments/arcs/vias. Outputs results/supply-copper.json and authored supply-copper-review.html. Human check: confirm hot/transient/fault currents, finished construction and assembled losses before release.
