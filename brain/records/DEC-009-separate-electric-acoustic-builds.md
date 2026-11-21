---
id: DEC-009
type: decision
domain: cross-domain
status: documented
updated: 2026-11-20
---
# Separate electric and acoustic builds

## Question and scope
Preserve the current electric-guitar project and develop an acoustic-specific amplifier as a separate Git branch in the user-specified repository.

## Options and tradeoffs
Separate branches preserve independently reviewable circuit, component, speaker, PCB and fit decisions. The common checkpoint contains all current engineering materials, including historical failures and preliminary acoustic research. Sharing a baseline does not qualify either build for fabrication.

## Decision and authority
On 20 November 2026 the user authorized an op-amp buffer and selection of a speaker, tweeter and crossover for acoustic use in the existing cabinet. The user then explicitly requested two separate builds, publication of all current project materials to https://github.com/davidgrahamsites/Tube-Amp, completion of the electric-branch upload first, and extensive notes on the acoustic branch for a new chat the user will create.

Git names: `electric-guitar-amp` and `acoustic-guitar-amp` (spaces are not valid in Git ref names). First commit and verify the complete current project on the electric branch. Then fork the acoustic branch from that exact commit and add its extensive handoff. Acoustic implementation is handed to the user's next chat; no separate chat is created automatically.

The existing original six-tube electric circuit is preserved. Acoustic input buffering, clean voicing and speaker/crossover changes belong to the acoustic branch. This is authorization to design, not to purchase, contact suppliers again, drill the cabinet or upload fabrication orders.

## Evidence
- [Build identity](../../BUILD_VARIANT.md)
- [Canonical requirements](../../Renegade_Codex_Handoff.md)
- [Current engineering state](../../PROJECT_STATUS.md)
- [Input and speaker research](../../engineering/component-selection/evidence/acoustic-input-speaker-review-2026-11-20.md)
- [Feedback ledger](../feedback/events.json)

## Open questions and next check
Verify remote commit identity after each push. The acoustic handoff must distinguish confirmed guitar models from unconfirmed pickup/variant details, existing cabinet evidence from final fit, and proposed parts from selections. Current CAD and simulations are engineering drafts. Preserve the electric branch when beginning acoustic work.

## Acoustic-branch handoff checkpoint
Electric checkpoint `6eba80905b44ba7af29efd09fbd587d7280a8521` was pushed and verified with `git ls-remote` before creating this branch. See [ACOUSTIC_HANDOFF.md](../../ACOUSTIC_HANDOFF.md) for new-chat startup. Inherited engineering files are unchanged by the handoff. Acoustic implementation remains for the next chat.
