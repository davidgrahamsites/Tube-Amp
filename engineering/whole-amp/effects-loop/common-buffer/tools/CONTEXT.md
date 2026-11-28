# Headroom comparison factories
Owner: integration. Inputs: ../contract.json and existing full-circuit fixture. Process: generate decks, bounded SPICE workers, independent metric audit. Outputs: ../results. Human check: inspect the explicit clipping equation and compare results at equal stimulus. No active CAD writes.

composite_return.py owns the CB-002 standalone experiment. It reads composite-return.json, writes bounded per-case decks/receipts, and calls the existing spice_runtime adapter. Stable parameters stay outside results. No current native circuit is synthesized from this experiment.

operating_point.py owns CB-003 numerical initialization comparisons, importing only the existing CB-002 deck factory and runtime. audit_operating_point.py independently checks saved DC/AC data; original CB-002 products stay unchanged. Read ../operating-point.json for case selection and limits.

output_heat.py owns the CB-004 ideal load/thermal calculation. Read output-heat.json; write the same-name result. It does not select components, run SPICE or mutate native CAD.

CB-007. supply_trial.py builds the pass-stage surrogate and joins the guarded return. supply_loop.py tests compensation. supply_mute.py tests startup with the manufacturer signal models. optical_mute.py tests switching feedthrough. supply_faults.py owns passive fault and thermal models. supply_detector.py uses the archived TI LM2903B model for independent hard trip. supply_sequence.py checks control priority. supply_aux.py applies both mute budgets to the existing auxiliary model. audit_supply.py checks independent limits, evidence and native preservation.

CB-008. sudden_guard.py owns the delay network and fast shunt fault fixture. guard_detector.py computes local crossings. guard_slew.py tests pin and output fall times and ripple. guard_injection.py tests gate displacement. guard_audio.py drives the integrated load. guard_handover.py and guard_sustained.py cover the longer time scales. Run audit_sudden.py after refreshing the receipts. Compare the intact circuit and failed controls before carrying a timing budget to the bench.

The cutoff guard model owns part data and its two-terminal netlist. The fault fixtures apply independent load, switching and sequencing faults. The guarded-cutoff runner writes the CB-010 receipt. The relay-margin tool checks the DC switch correction against that receipt.

CB-011. The local reservoir bounds minimum capacitance and startup. The assembled-return runner shares the protected supply with the audio macro. The two shunt studies use that fixed network to check bias and nonlinear capacitance. Run audit_gain_cutoff.py against the JSON receipts, then compare the actual pair, installed switch timing and the guarded cabinet with the report.

CB-012 uses shunt_curve.py and qualify_shunt_curve.py to convert the IXYS plot to differential charge and test the silicon mute. CB-013 uses sic_shunt.py and qualify_sic_shunt.py. Supply a local copy of the linked UnitedSiC model with the recorded hash. Run each group (audio, switching, faults) in a fresh KiCad Python process. Inspect partial transients, terminal gate voltage, gain, distortion and switching peaks.

For the revised delay network use retuned_shunt.py with audio and arrival, sic_pair_window.py and sic_audio_tolerance.py with the model path and --revised, then sic_signal_levels.py and sic_distortion_controls.py with the model path. The factories report each threshold or passive corner and tag the fixed-capacitance control. Inspect the receiver distortion and gate pulse together.

steered_bias.py and qualify_steered_bias.py add the actual divider and a behavioral steering diode to both fixtures. floating_driver_budget.py independently sweeps regulator and undervoltage thresholds. Run the electrical factories with the cached hash-checked SiC model.
