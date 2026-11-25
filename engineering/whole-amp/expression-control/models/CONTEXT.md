# Expression manufacturer model inputs

Owner: expression-control. Input: TI SNOM267 official ZIP; LM13700.MOD retains its copyright and redistribution notice. manifest.json records download source/date/hash and declared limitations. The single-amplifier model overestimates bandwidth and phase margin by more than twofold and does not qualify another manufacturer's nominally compatible part.
Process: use the unmodified file through ../tools/ota_screen.py; do not tune the model to obtain acceptance. Output: stable model input to standalone candidate experiments.
Human check: compare declared pin order and application limits to the current TI datasheet; bench-test stability, noise and device spread.

MMBT3906.spice.txt contains the numerical Diodes Incorporated model card transcribed from its primary web response; MMBT3906-manifest.json records acquisition, hash and limits. It is not a byte-identical download, a different vendor model, or a tolerance guarantee. bias_screen.py consumes this model; upstream disclaimer remains linked in the card/manifest.
