# Reverb input clamp contract
Owner: electrical integration. One job: Bound input-clamp current and rail injection; select a passive rail-load correction without changing signal interfaces.
Inputs: ../circuit.json, exact TI/onsemi/Yageo evidence and contract.json. Process: tools/analyze.py calculates current/rail bounds; tools/simulate.py exercises the declared ideal-clamp envelope. Outputs: review.md, results; native edits require a separate preservation check. Human check: measure actual powered/unpowered rail and input behavior with selected parts; the bounded model is not physical qualification.

VAL-063 is a historical, hash-bound pre-integration screen. R619/R620 are adopted in [../rail-load-integration/review.md](../rail-load-integration/review.md), VAL-064, with new native/source hashes and supply regression. Replay this original screen against its captured baseline; do not update its hashes to disguise changed inputs.
