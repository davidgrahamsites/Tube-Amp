# Raw auxiliary hold-up evidence
Owner: auxiliary-supply integration.
Inputs: ../../hold-up-contract.json, existing rectifier/load/preload contracts, source circuit and exact manufacturer/listing observations.
Process: ../../tools/hold_up_screen.py runs the 25 VA matrix; hold_up_comparison.py runs a limited 50 VA comparison; check_hold_up.py independently audits the outputs and native preservation. Replace named outputs, retain no full CAD copies.
Outputs: screen.json, comparison.json, simulator logs, checks.json and source-observations.json. Public interpretation: ../../hold-up-review.md.
Human check: inspect the retained low-winding failures and verify real detector/contact timing, transformer voltage under load, capacitor heat/ripple and the complete Shanghai purchase route before adoption. A hypothetical 20 ms allowance is not a qualified relay response.
