# tools
Owner: electric integration.
Inputs: source circuit contract or RENEGADE_LOOP_INPUT snapshot, retained tube and TI OPAx134 models.
Process: fixture.py owns source-derived deck generation; run.py owns bounded AC/transient execution through ../../tools/spice_runtime.py; send_isolation.py screens integrated ideal-branch loading; solver_review.py diagnoses model convergence and compares its optional domain guard; send_driver.py screens the standalone manufacturer SEND model; return_driver.py owns the separate hash-pinned OPA462 RETURN headroom experiment, bounded per case with explicit failures; return_diagnostics.py owns bounded solver-only substitutions without replacing acceptance cases; audit.py checks retained evidence consistency.
Outputs: ../results. Public interfaces: fixture.deck/fingerprint, run.bounded_case/stats and documented command-line factories. No native CAD mutation.
Human check: inspect substitutes, failed/timeout cases and voltage scales before interpreting the aggregate audit. A completed solver case is not a hardware pass.

power_target.py owns the bounded target-drive sweep and separate near-target timestep comparison. audit_power_target.py verifies retained deck/source/result consistency and numerical sensitivity. Their outputs are power-target-* under results; neither selects components nor changes native CAD.
