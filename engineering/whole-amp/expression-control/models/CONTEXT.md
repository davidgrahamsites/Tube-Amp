# Expression manufacturer model inputs

Owner: expression-control. Input: TI SNOM267 official ZIP; LM13700.MOD retains its copyright and redistribution notice. manifest.json records download source/date/hash and declared limitations. The single-amplifier model overestimates bandwidth and phase margin by more than twofold and does not qualify another manufacturer's nominally compatible part.
Process: use the unmodified file through ../tools/ota_screen.py; do not tune the model to obtain acceptance. Output: stable model input to standalone candidate experiments.
Human check: compare declared pin order and application limits to the current TI datasheet; bench-test stability, noise and device spread.
