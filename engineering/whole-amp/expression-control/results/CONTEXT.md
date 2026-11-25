# Expression experiment evidence

Owner: expression-control. Inputs: ../tools/ota_screen.py and hash-pinned ../models/LM13700.MOD plus the retained TI OPAx134 model. Process: regenerate the finite candidate screen in place; keep failed cases. Outputs: ota-screen.json, ota-*.cir, ota-screen.log and ota-audit.json. These are nominal isolated gain-cell evidence, not expression-jack, native PCB, noise, sourcing or full-amp qualification.
Human check: compare waveform amplitudes, DC offsets, distortion and refinement results with the declared test range before adopting a circuit.

Supply/bias products: supply-probes.json and supply-*.cir/log retain invalid and corrected solver cases. bias-screen.json and bias-*.cir/log retain all current candidate cases, including failures. supply-bias-audit.json separates evidence integrity from circuit qualification. Source-observation JSON records public listing fields/date/hash and purchasing limits. Regenerate in place; do not interpret stale or exploratory files as additional passing cases.

VAL-044 outputs: trim-screen.json and trim-*.cir/log; bias-isolation.json and isolation-*.cir/log; continuation.json/decks/seeds/log; trim-isolation-audit.json. Source observations record the Bourns trimmer listing and visually inspected Hotone pinout. These remain experimental; the idealized-controller and fixed-base decks are diagnostic fixtures only.

VAL-045: settled-bias.json, settled-*.cir/log and settled-bias-audit.json record powered DC only. Time refinements and weak-shunt sensitivity are separate results. native-preservation-045.json compares four board bytes against the recorded Git baseline. These results do not qualify power-on, actual protection or pedal behavior.

VAL-046: sequence-* and power-sequence.json preserve eight diagnostic rail cases including two solver failures. final-wet-mute-loading.json is the passive dry-loading fixture. final-mute-integration.json and final-mute-audit.json record the bounded native two-pin repair. final-mute-drc.json, final-mute-erc.json, final-mute-schematic.pdf and final-mute-detail.png are current native evidence; final-mute-source-observation.json records the domestic relay listing and source hashes. None qualifies rail-fault timing or the complete expression feature.

VAL-049: wet-fault-transfer.json retains30 AC/120 transient cases, and wet-fault-crosscheck.json retains six bounded independent SPICE runs/decks/logs and numerical comparisons. wet-shunt-source-observation.json records exact domestic J113/MMBFJ113 fields and manufacturer hash/conditions. These do not qualify real switch timing, hot operation, purchasing or silence.

jack-domestic-source-observation.json updates the exact NMJ6HCD2 domestic listing and shipping-policy evidence used by ../pedal-port-design.md; it is not order or physical-fit approval.
