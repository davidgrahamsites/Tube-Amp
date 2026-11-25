# Expression circuit experiment factories

Owner: expression-control. Inputs: ../models/LM13700.MOD, ../../../solid-state-reverb/simulation/models/OPAx134.LIB, ../requirements.md and ../selector-review.md.
Process: ota_screen.py owns the standalone manufacturer-model audio gain-cell experiment and bounded subprocess execution. It does not implement pedal protection or a complete control circuit. Output: ../results/ota-screen.json, retained decks and solver log. Stable tool/model inputs stay separate from generated evidence.
Human check: inspect rejected cases, model limitations and ideal bias/trim assumptions before choosing an actual component or copying a circuit into KiCad.
