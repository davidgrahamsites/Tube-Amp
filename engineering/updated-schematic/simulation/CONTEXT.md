# Preliminary reference analyses

One job: retain scoped bias/debounce calculations with explicit model limitations.

## Inputs
Draft R/C values, an ideal 50 VAC bias tap, a generic diode model, an ideal hysteretic Schmitt surrogate and ngspice 45.2 bundled with KiCad.

## Process
Run `../tools/run_explorations.py` with KiCad's native Python. Store each circuit, sampled waveform CSV, engine log, metrics and hashes. Preserve the first failed bias-range finding in `superseded-bias-attempt.json`; the first run's raw waveforms were overwritten, and that limitation is explicit.

## Outputs
`explorations.json`, `ngspice.log`, thirteen `.cir` files with CSV vectors and the superseded-attempt record. No selected-component amplifier validation is claimed.

## Human check
Qualify purchased-part models and run baseline/audio/reverb/supplies/controller/integrated S01-S06 analyses before release. These limited runs omit real transformer behavior, valve/relay/logic/tank models, thermal effects, ESD and acoustic behavior.
