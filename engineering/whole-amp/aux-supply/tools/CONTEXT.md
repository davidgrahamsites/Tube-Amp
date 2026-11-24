# Auxiliary supply factories
Owner: Renegade integration. Inputs: current source/native CAD and a pinned Git baseline.
Process: correct_c212.py --apply refuses changed baseline source files and makes only its declared C212 fields. Verification is a separate read-only step. No automatic regeneration of hand-edited sheets or layouts.
Outputs: ../results evidence and the explicitly authorized native correction.
Human check: inspect all changed fields and retained release holds before accepting the checkpoint.

Current envelope route: screen_envelope.py reads ../envelope-contract.json and guarded circuit topology, runs the existing ngspice adapter and writes conditional raw-supply results. check_envelope.py audits evidence and rejects corruptions; screen_bleeder.py reruns three candidate cases through that same model. Run with the native KiCad Python; no native CAD mutation.
