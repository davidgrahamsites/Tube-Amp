# Solver history — 23 November 2026

Initial integrated fixture failed at 0.0131362 s. Smaller steps alone did not resolve it. The ideal-transformer feedback sign was then checked with feedback disabled, each polarity enabled, and a small-signal return stimulus. The corrected sign reduces gain. This applies to the fixture, not a transformer lead-colour assignment.

After that correction, four nominal-supply 1 kHz cases and two timestep refinements completed. Final settings: Gear order 2, reltol 0.001, abstol 1 nA, vntol 10 µV, gmin 1e-10, rshunt 1e12, cshunt 1e-14. Actual maximum timestep is 10.4167 µs for baseline 1 kHz cases and 5.2083 µs for refinements. Retained-window settling and amplitude/THD sensitivity are in audit.json.

A separate heavy-overdrive case (clean, B_EARLY 240 V, 1 kHz, 1 V peak) still fails at 48.387 µs, with a timestep-too-small report at INPUT. The fresh reproducer deck, log and failure result are overdrive-coverage.*. A prior 1 µs attempt exceeded a 45 second diagnostic limit and was terminated without a passing result. Do not conflate the corrected feedback polarity with resolution of this remaining numerical failure.

The failed case supplies no clipping/headroom result. Native hardware is unchanged. No bench validation or fabrication acceptance follows from solver completion.
