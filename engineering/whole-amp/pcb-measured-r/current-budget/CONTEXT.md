# Copper current budget
Owner: PCB integration. One job: turn circuit loads into revisioned conductor requirements.
Inputs: current reverb-600/circuit.json, received tank DC resistance, declared operating bounds in contract.json, native copper audit and manufacturer source links.
Process: tools/analyze.py solves the passive loads at the six op-amp outputs, checking KCL and an independent series-RLC driver calculation. tools/check.py checks source freshness and rejects corrupted driver current, case coverage, thermal approval and source evidence. No CAD writes. Native-value and engineering-assumption ownership remain separate.
Outputs/public seam: results/budget.json and review.md. This first pass covers reverb output loads, conditional supply allocation and conductor resistance screening. It does not qualify complete mains/heater/fault currents or IPC-2152 thermal performance.
Human check: confirm real supply/output limits, tank impedance, loaded voltage drop and hot-cabinet temperature before release.
Task card: baseline f51f883; inputs above; output numerical path bounds; dependency actual stackup/thermal limits; done when declared model is independently checked and its unresolved domains explicit. One analysis pass, not six-scope completion.
