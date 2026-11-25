# Expression experiment evidence

Owner: expression-control. Inputs: ../tools/ota_screen.py and hash-pinned ../models/LM13700.MOD plus the retained TI OPAx134 model. Process: regenerate the finite candidate screen in place; keep failed cases. Outputs: ota-screen.json, ota-*.cir, ota-screen.log and ota-audit.json. These are nominal isolated gain-cell evidence, not expression-jack, native PCB, noise, sourcing or full-amp qualification.
Human check: compare waveform amplitudes, DC offsets, distortion and refinement results with the declared test range before adopting a circuit.

Supply/bias products: supply-probes.json and supply-*.cir/log retain invalid and corrected solver cases. bias-screen.json and bias-*.cir/log retain all current candidate cases, including failures. supply-bias-audit.json separates evidence integrity from circuit qualification. Source-observation JSON records public listing fields/date/hash and purchasing limits. Regenerate in place; do not interpret stale or exploratory files as additional passing cases.

VAL-044 outputs: trim-screen.json and trim-*.cir/log; bias-isolation.json and isolation-*.cir/log; continuation.json/decks/seeds/log; trim-isolation-audit.json. Source observations record the Bourns trimmer listing and visually inspected Hotone pinout. These remain experimental; the idealized-controller and fixed-base decks are diagnostic fixtures only.
