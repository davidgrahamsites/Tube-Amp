# Acoustic Guitar Amp

Active branch: `acoustic-guitar-amp`.

Start the new chat with [ACOUSTIC_HANDOFF.md](ACOUSTIC_HANDOFF.md). It records the current engineering state, confirmed requirements, unresolved interfaces, exact artifact paths and the next work sequence.

This separate build starts from verified electric checkpoint `6eba80905b44ba7af29efd09fbd587d7280a8521` on `electric-guitar-amp`. The electric branch remains preserved. This branch currently adds handoff/scope records only: inherited native circuits, PCB drafts, BOM and simulations are unchanged from that checkpoint and are not yet qualified as an acoustic amplifier.

Design brief: a clean tube amplifier for acoustic guitar. Authorized acoustic work: develop an op-amp input buffer and select/design an acoustic speaker, tweeter and crossover to fit the already-delivered yellow-tweed cabinet; retain the spring tank and documented controls. Both builds require proper replaceable tube sockets, with socket/retainer and tube-removal clearances in the physical design. The user will begin implementation in a new chat.

The original four12AX7/twoEL34 amplifier is the inherited starting point. No wholesale architecture change, purchase, supplier contact or fabrication upload is implied. Canonical requirements live in [Renegade_Codex_Handoff.md](Renegade_Codex_Handoff.md).

Current release state: **engineering draft; not build-ready**. See [PROJECT_STATUS.md](PROJECT_STATUS.md). Keep branch-specific design changes separate and update ICM continuously.
