# Auxiliary supply factories
Owner: Renegade integration. Inputs: current source/native CAD and a pinned Git baseline.
Process: correct_c212.py --apply refuses changed baseline source files and makes only its declared C212 fields. Verification is a separate read-only step. No automatic regeneration of hand-edited sheets or layouts.
Outputs: ../results evidence and the explicitly authorized native correction.
Human check: inspect all changed fields and retained release holds before accepting the checkpoint.

Current envelope route: screen_envelope.py reads ../envelope-contract.json and guarded circuit topology, runs the existing ngspice adapter and writes conditional raw-supply results. check_envelope.py audits evidence and rejects corruptions; screen_bleeder.py reruns three candidate cases through that same model. Run with the native KiCad Python; no native CAD mutation.

Preload route: integrate_preload.py is a one-time baseline-guarded native addition; check_preload.py independently verifies delta, package and bounds. screen_adopted_preload.py reuses only the raw-model evaluate interface, writes ../results/preload and includes the R215 current. Original envelope remains immutable historical evidence; its generator refuses a source that includes R215. Shared syntax inspection comes from ../../tools/native_sexpr.py.
