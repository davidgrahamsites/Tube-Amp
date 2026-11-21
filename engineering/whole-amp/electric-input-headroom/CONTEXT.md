# Electric input headroom
Owner: electric integration. One job: screen the original first tube stages for hot-pickup headroom.
Inputs: ../reverb-600/circuit.json, ../simulation/models/dm12ax7s.inc and prior full-amp operating-point evidence. Supply and source sweeps are explicitly assumed envelopes, not selected pickup/transformer models.
Process: tools/run.py derives preamp fixtures from the current contract; uses the existing ngspice runtime; retains decks/results/logs under results. No CAD mutation.
Outputs: scoped first-stage and preamp distortion/compression data, provenance and review. Excludes the phase inverter/output transformer/power stage/reverb.
Human check: compare actual guitar/cable waveforms, measured supply/bias and assembled noise with the modeled envelope before quoting a clean-input specification.
Task card: inspect current preamps and model; sweep supply/frequency/amplitude; check timestep sensitivity; decide whether headroom requires an input change. Root owns integration. Done when scoped results and limitations are recorded; physical validation remains required. Estimated effort one engineering pass.
