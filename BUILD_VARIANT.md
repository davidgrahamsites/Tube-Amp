# Electric Guitar Amp

Active branch: `electric-guitar-amp`.

Mains scope, updated November 24: **switchable 120 V / 220 V**, with validation planned at 120 V/60 Hz and 220 V/50 Hz. [DEC-015](brain/records/DEC-015-switchable-mains.md) supersedes the former deferral. Existing native files retain their 220 V baseline names and circuit until the mains redesign is checked; selectable operation is not yet implemented or qualified.

This build preserves the original six-tube Renegade amplifier with solid-state-driven spring reverb, constant dry signal and the existing yellow-tweed cabinet requirements. Current schematic, board drafts, selected BOM, simulation evidence, received-hardware photographs, source documents and ICM history are included.

This is an engineering checkpoint, not a fabrication release. Start with [PROJECT_STATUS.md](PROJECT_STATUS.md) and [CONTEXT.md](CONTEXT.md). In particular, three boards still need routing, exact component selection is incomplete, expression control remains pending and assembled fit has not been verified.

The user authorized a separate `acoustic-guitar-amp` build on 20 November 2026. Create it from the verified electric checkpoint after the current project is committed and pushed. Acoustic-specific input buffering and speaker/crossover work belongs on that branch. Acoustic-use research in this checkpoint is retained conversation/evidence; it has not changed the electric circuit.

Both builds require proper replaceable tube sockets, with socket/retainer and tube-removal clearances included in the mechanical design. See the canonical requirements in the handoff.
