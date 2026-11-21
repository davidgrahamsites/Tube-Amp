# Electric input headroom — 21 November 2026

Keep the original electric input. The model shows progressive first-stage distortion with large signals; an added unity-gain buffer would not supply extra tube headroom. No attenuator or circuit change is selected from these assumed sine-wave tests.

## Nominal first-stage screen

B_EARLY 278 V, B_PRE 313 V, 1 kHz. Source amplitude is before the assumed 20 kΩ pickup resistance and 470 pF cable. Jack amplitude is measured in the fixture. THD includes harmonics 2–10 at the first plate, not the speaker output.

| Channel | Source V peak | Jack V peak | First-plate THD % | Gain change dB |
|---|---:|---:|---:|---:|
| clean | 0.25 | 0.2447 | 0.879 | -0.008 |
| clean | 0.5 | 0.4894 | 1.793 | -0.033 |
| clean | 1 | 0.9788 | 3.911 | -0.145 |
| clean | 1.5 | 1.4679 | 7.315 | -0.435 |
| clean | 2 | 1.9515 | 15.358 | -1.422 |
| dirty | 0.25 | 0.2450 | 0.768 | -0.015 |
| dirty | 0.5 | 0.4901 | 1.555 | -0.044 |
| dirty | 1 | 0.9801 | 3.349 | -0.143 |
| dirty | 1.5 | 1.4700 | 6.620 | -0.401 |
| dirty | 2 | 1.9598 | 16.329 | -1.282 |

## Numerical check

Completed 118 cases: 108 supply/frequency/amplitude points, eight finer-step/longer-settling comparisons and two clean-volume controls. Baselines settle at least 0.5 seconds; refinements at least 1 second. Maximum first-stage gain change on refinement is 0.01536%; maximum THD change is 0.01092 percentage points. Adjacent last-ten-period windows differ by at most 0.00309% gain and 0.00136 THD percentage points. These observed differences support the coarse amplitude brackets; no precision clipping-voltage specification is implied.

At 1 kHz, the first-stage 5% THD diagnostic is crossed between 1 and 1.5 V source peak in both channels at all three supply settings. This threshold was a diagnostic, not an agreed clean-output specification. Whole-preamp results include later-stage distortion, especially the intentional dirty channel. Lowering the post-first-stage volume does not remove distortion already produced by the first triode.

## Scope and limits

This is the unchanged generic Duncan Munro 1997 12AX7 model, not the exact purchased tube. Supplies 240/278/320 V with the second rail 35 V higher are assumed sensitivity points. Pickup inductance, actual guitar waveform, power stage, output transformer, reverb loading and hardware noise are excluded. Tone/gain controls are 0.5 electrical fraction and volume/master 0.25, not knob markings. Output load is an assumed 1 MΩ. The full-amplifier high-frequency transformer ringing remains unresolved; this isolated fixture does not claim to fix it.

The original dirty fixture omitted the tone/output sheet. That failed attempt and the later short-settling results remain archived. See [fixture correction](fixture-correction.md). Current [summary](summary.json), [numerical comparison](numerical-review.json), per-case decks/logs and sampled waveforms are generated evidence. Actual guitar/cable, selected tube spread, signal levels at each stage and assembled noise still need bench checks before a product specification or release.
