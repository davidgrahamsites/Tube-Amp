# Passive dry-path topology experiment

`tools/check_passive_mix.py` keeps the original tube sections, supplies and transformer surrogate, removes the low-voltage reverb block and compares a direct dry connection with a100k dry /1M wet passive summing interface. It adds a1M/100k attenuated send,100n AC coupling. Wet source is an ideal zero-ohm source, not a tank or recovery model.

Six AC cases complete (clean/dirty ×direct/passive-dry/passive-wet). At1kHz the passive interface reduces dry gain1.584dB clean and3.480dB dirty versus direct. Over the three inspected82Hz/1kHz/5kHz points the gain-change spread is0.157dB clean and0.042dB dirty. This establishes approximately flat attenuation at these test points, not full-band transparency. Input impedance changes and wet backfeed are real tradeoffs; they must not be hidden as unchanged original behavior.

A separate full TI-model candidate in `../reverb-headroom/` tests the attenuated send and passive dry path with wet zero. Its actual coupling/bleed loading differs slightly from the ideal wet source used here. Neither experiment has been applied to native schematic/PCB. Required next: nonzero wet/mute sweeps, tank output/drive limits, startup/off-rail behavior, tolerances and integrated high-line/transient qualification. Fixed dry gain should remain independent of the front REVERB setting; no dry/wet crossfade is introduced.
