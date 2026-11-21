# Headroom factories
Owner: electric integration. One job: derive and evaluate the isolated preamp test fixture.
Inputs: ../../reverb-600/circuit.json and ../../simulation/models/dm12ax7s.inc; shared ../../tools/spice_runtime.py adapter.
Process: run.py executes supply/frequency/amplitude sweeps, refinement and control cases. review.py reads saved results and checks source hashes, numerical stability and coarse diagnostic crossings. Neither mutates the design.
Outputs: ../results/ decks, logs, summary, samples and scoped review.
Human check: compare fixture endpoints and control fractions with the native schematic; review actual guitar/tube behavior before using a clean-input specification.
