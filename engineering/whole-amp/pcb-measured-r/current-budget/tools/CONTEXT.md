# Current-budget factories
Owner: PCB integration. Inputs: parent contract and current circuit. Process: analyze.py performs passive nodal solves and emits numerical evidence; check.py independently verifies limiting-current arithmetic and freshness. Outputs: ../results/budget.json and checks.json. Human check: inspect assumptions before treating calculated currents as conductor requirements. No native CAD mutation.

check_candidate_copper.py audits the HI-008 candidate against current passive load values and declared construction, calculates track/via DC loss and inventories current active boards. It records hashes and calculation controls in ../results/candidate-copper.json. Run with KiCad Python. Thermal and fault qualification remain separate.

check_supply_copper.py reuses analyze.calculate as a pure load model after checking current electrical inputs. It checks complete rail segments/arcs and via loss against supply-copper.json, retains rejected trials, and writes results/supply-copper.json. It does not alter the historical source hash or auxiliary-supply receipt.
