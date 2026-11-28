# Headroom comparison factories
Owner: integration. Inputs: ../contract.json and existing full-circuit fixture. Process: generate decks, bounded SPICE workers, independent metric audit. Outputs: ../results. Human check: inspect the explicit clipping equation and compare results at equal stimulus. No active CAD writes.

composite_return.py owns the CB-002 standalone experiment. It reads composite-return.json, writes bounded per-case decks/receipts, and calls the existing spice_runtime adapter. Stable parameters stay outside results. No current native circuit is synthesized from this experiment.

operating_point.py owns CB-003 numerical initialization comparisons, importing only the existing CB-002 deck factory and runtime. audit_operating_point.py independently checks saved DC/AC data; original CB-002 products stay unchanged. Read ../operating-point.json for case selection and limits.

output_heat.py owns the CB-004 ideal load/thermal calculation. Read output-heat.json; write the same-name result. It does not select components, run SPICE or mutate native CAD.

CB-007. supply_trial.py builds the pass-stage surrogate and joins the guarded return. supply_loop.py tests compensation. supply_mute.py tests startup with the manufacturer signal models. optical_mute.py tests switching feedthrough. supply_faults.py owns passive fault and thermal models. supply_detector.py uses the archived TI LM2903B model for independent hard trip. supply_sequence.py checks control priority. supply_aux.py applies both mute budgets to the existing auxiliary model. audit_supply.py checks independent limits, evidence and native preservation.
