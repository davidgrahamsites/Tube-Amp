# Full-amplifier screen resistor sensitivity

2026-11-12. `tools/check_screen_tradeoffs.py`: dirty channel,200mVpeak1kHz,400V stiff supply,-40V bias, same generic valve and TI op-amp models,80ms transient,1µs maximum step. Only R41/R42 values are varied. Initial transient runs completed but the first measurement extractor failed on an unavailable internal current vector. Failure logs retained; corrected measurement uses the model's exact Ba conduction equation. Corrected runs all complete.

|R41/R42 each|Screen A/B, last10ms W|Resistor A/B, last10ms W|Ideal load W|
|---|---|---|---|
|1k|16.668/16.782|7.747/7.853|61.898|
|2.2k|8.622/8.656|6.268/6.295|56.368|
|4.7k|4.163/4.179|4.350/4.344|46.404|

**2.2k is rejected as a solution in this fixture.** The1k original also exceeds the5W resistor rating. **4.7k is the next design candidate**, with at least10W nominal resistance hardware plus manufacturer thermal/pulse qualification. Its5W version is unsuitable for reasonable thermal margin here. No native circuit change is made yet.

Longer observation exposes worse stress than the previous40ms reports. The last20ms and last10ms means differ, so these runs do not establish a fully settled worst case. Need extended/transient envelope, high-line and tolerances, actual magnetics and selected tubes. The screen resistor change does not resolve the predicted output-transformer overload or the low-voltage dry-path clipping. No claim of actual46W or construction readiness.

The `write` raw-data export attempt failed because of spaces in the absolute filename; JSON results and simulator logs are retained, but no raw trace is claimed for these three runs. Future raw export must use a simple filename within the output directory. Corrected measurement code did not modify model parameters.
