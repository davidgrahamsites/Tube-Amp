# Expression experiment evidence

Owner: expression-control. Inputs: ../tools/ota_screen.py and hash-pinned ../models/LM13700.MOD plus the retained TI OPAx134 model. Process: regenerate the finite candidate screen in place; keep failed cases. Outputs: ota-screen.json, ota-*.cir, ota-screen.log and ota-audit.json. These are nominal isolated gain-cell evidence, not expression-jack, native PCB, noise, sourcing or full-amp qualification.
Human check: compare waveform amplitudes, DC offsets, distortion and refinement results with the declared test range before adopting a circuit.
