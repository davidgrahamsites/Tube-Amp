# Expression circuit experiment factories

Owner: expression-control. Inputs: ../models/LM13700.MOD, ../../../solid-state-reverb/simulation/models/OPAx134.LIB, ../requirements.md and ../selector-review.md.
Process: ota_screen.py owns the standalone manufacturer-model audio gain-cell experiment and bounded subprocess execution. It does not implement pedal protection or a complete control circuit. Output: ../results/ota-screen.json, retained decks and solver log. Stable tool/model inputs stay separate from generated evidence.
Human check: inspect rejected cases, model limitations and ideal bias/trim assumptions before choosing an actual component or copying a circuit into KiCad.

Additional factories: supply_probe.py diagnoses the old low-supply timeout without changing physical components. bias_screen.py replaces ideal currents with a PNP/servo/current-mirror candidate using the primary Diodes card; audit_supply_bias.py owns integrity and bounded numeric checks, reporting unresolved cases separately from evidence success. Public seam is the JSON case/deck/report format; the original ota_screen.py stays unchanged for VAL-042 provenance.

VAL-044 factories: trim_screen.py consumes bias_screen.deck/measure through bounded child processes and writes trim-* evidence. bias_continuation.py derives solver hints only; bias_isolation.py owns five causal fixture/substitution checks. audit_trim_isolation.py checks retained hashes and numeric evidence, preserving failed cases and distinguishing diagnostic substitutes from real hardware.

VAL-045: settled_bias.py consumes bias_screen.deck and adds a DC-only stimulus plus explicit two-stage settling. It writes settled-* decks/logs and settled-bias.json. audit_settled_bias.py owns independent metric/integrity acceptance and false-success controls. Neither changes native CAD or earlier evidence.
