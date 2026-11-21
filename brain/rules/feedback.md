---
id: RULE-MEM
type: rule-set
domain: cross-domain
status: documented
updated: 2026-11-20
---
# Continuous feedback and decision capture

User instruction: backfill the entire project, including materials and decisions, into ICM and keep collecting feedback and logging decisions as they occur. Owner: every active Renegade agent; the integration agent owns shared registers.

## At task startup
Read root CONTEXT.md, PROJECT_STATUS.md, brain/catalog/WORKSPACE.md and the task module's contract. Read recent events in brain/feedback/events.json and the relevant decision records. Current explicit user corrections override older proposals. Do not read unrelated projects.

## During work
1. Append each material requirement, correction, approval, cancellation or unresolved question to brain/feedback/events.json when it arrives, before dependent work. Use a stable FB identifier and the template. Preserve the user's wording in a short quote. Routine acknowledgements need no separate event unless they change authority or scope.
2. Record the source: conversation quote/locator or exact file. Unknown original dates stay null; recorded_on is the actual capture date. Backfilled summaries are not a complete verbatim chat archive.
3. Identify authority: user, supplier-as-relayed-by-user, engineer or measured evidence. Distinguish an accepted user choice, an implemented engineering change, a proposal and a test result. Do not convert one into another.
4. Resolve into the canonical home: product requirements -> Renegade_Codex_Handoff.md; dimensions -> engineering/whole-amp/mechanical/fit-register.json; component choice -> engineering/component-selection/coverage.json plus evidence; decision/evidence -> brain/records; native revision -> its engineering module. Link from the feedback event instead of maintaining a second set of requirements.
5. If a choice changes, append a superseding event and link it to the old one. Retain previous decisions and dated supplier observations. A closed feedback event means the record is incorporated, not that the amplifier is built or tested.
6. Separate a new clarification from permission. Work within existing authorization; no repeat confirmation for ordinary reversible record or design work. Mail still requires the user's chirp-and-immediate-confirmation procedure. No order or fabrication upload is implied.

## At meaningful checkpoints and turn end
Update the relevant decision/evidence record, material route and PROJECT_STATUS.md if state changed. Rebuild both catalogs; validate feedback IDs, source paths, selected revision and duplicate reference coverage. After code, UI, moves or architecture edits, run the scoped ICM check and relevant project checks. Save outstanding items and the next concrete action before compaction/handoff.

## Scope and limits
This is a persistent workflow for future active project sessions. It does not claim background monitoring of Mail, WeChat or other chats. Capture externally supplied feedback when the user supplies it or an authorized task retrieves it. Measurements are evidence only when actually reported; instructions to measure are not measurements.

## Human check
The user can edit any ledger entry or linked decision. Surface a conflict only when it materially affects the next action; otherwise preserve uncertainty and continue independent work.
