---
id: DEC-012
type: decision
domain: cross-domain
status: superseded
updated: 2026-11-24
---
# Keep current mains supply; defer multi-voltage variant

Superseded on November 24 by [DEC-015](DEC-015-switchable-mains.md) / FB-106: user now requests switchable 120 V / 220 V in the current build. The text below preserves the earlier decision.

## Question and scope
Whether the active electric amplifier should gain 120 V and 220–240 V operation now.

## Options and tradeoffs
Keep the existing 220 V / 50 Hz design basis and current work scope, or expand transformer, protection and verification work for multiple mains voltages. User chose to defer the expanded scope.

## Evidence
[FB-084 and FB-085](../feedback/events.json) preserve the feasibility question and subsequent explicit decision. [Current requirements](../../Renegade_Codex_Handoff.md#user-confirmed-requirements) remain canonical.

## Decision and authority
User decision, 22 November 2026: retain the active electric build at 220 V / 50 Hz. Keep multi-voltage operation as a future option for a separate handoff. Do not add a selector, change primary wiring or substitute parts solely for multi-voltage capability now. This does not cancel authorized circuit/PCB defect repairs, remaining component selection, fit checks or readable-schematic work. No electrical artifact changed as part of this decision capture.

## Open questions and next check
When the user starts the future variant, hand off the then-current verified electric revision and its unresolved items. Reassess exact primary windings/taps for every transformer and auxiliary supply, voltage selection, voltage-specific protection, intended mains ranges and 50/60 Hz operation, rail/heater voltages, thermal behavior and cabinet fit. No compatible magnetics or dual-voltage operating approval is established here. Do not create the future branch or treat this deferred option as a blocker for current work.
