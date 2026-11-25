# Expression circuit experiment factories

Owner: expression-control. Inputs: ../models/LM13700.MOD, ../../../solid-state-reverb/simulation/models/OPAx134.LIB, ../requirements.md and ../selector-review.md.
Process: ota_screen.py owns the standalone manufacturer-model audio gain-cell experiment and bounded subprocess execution. It does not implement pedal protection or a complete control circuit. Output: ../results/ota-screen.json, retained decks and solver log. Stable tool/model inputs stay separate from generated evidence.
Human check: inspect rejected cases, model limitations and ideal bias/trim assumptions before choosing an actual component or copying a circuit into KiCad.

Additional factories: supply_probe.py diagnoses the old low-supply timeout without changing physical components. bias_screen.py replaces ideal currents with a PNP/servo/current-mirror candidate using the primary Diodes card; audit_supply_bias.py owns integrity and bounded numeric checks, reporting unresolved cases separately from evidence success. Public seam is the JSON case/deck/report format; the original ota_screen.py stays unchanged for VAL-042 provenance.

VAL-044 factories: trim_screen.py consumes bias_screen.deck/measure through bounded child processes and writes trim-* evidence. bias_continuation.py derives solver hints only; bias_isolation.py owns five causal fixture/substitution checks. audit_trim_isolation.py checks retained hashes and numeric evidence, preserving failed cases and distinguishing diagnostic substitutes from real hardware.

VAL-045: settled_bias.py consumes bias_screen.deck and adds a DC-only stimulus plus explicit two-stage settling. It writes settled-* decks/logs and settled-bias.json. audit_settled_bias.py owns independent metric/integrity acceptance and false-success controls. Neither changes native CAD or earlier evidence.

VAL-046: power_sequence.py writes sequence-* diagnostics and power-sequence.json. final_mute_loading.py writes the passive dry-loading calculation. integrate_final_mute.py is the only native-writing adapter here: explicit --apply, immutable baseline guard, three-file scope, receipt, no full-project regeneration. audit_final_mute.py accepts fresh before/after XML/ERC and after DRC paths, checks exact pin deltas and preserves failed simulations. It writes final-mute-audit.json without changing CAD.

VAL-049: wet_fault_transfer.py reads ../wet-fault-contract.json and ../../reverb-600/circuit.json via the declared relative path, then writes ../results/wet-fault-transfer.json. check_wet_fault.py uses a separately specified passive SPICE network and the shared spice_runtime adapter, comparing retained analytical outputs and writing wet-fault-crosscheck.json. Native topology guards and the review delimit scope; neither tool changes CAD.
