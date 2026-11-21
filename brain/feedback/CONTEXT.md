# User feedback intake
Owner: the active Renegade agent. One job: retain user corrections, preferences, approvals and open requests with their source and disposition.
Inputs: current user messages, ../records/, ../../Renegade_Codex_Handoff.md and ../../PROJECT_STATUS.md.
Process: append to events.json using ../_templates/feedback-event.json. Follow ../rules/feedback.md. Resolve the relevant canonical record before marking an event incorporated. Do not overwrite history or infer an approval.
Outputs: events.json is the editable event ledger; ../catalog/FEEDBACK.md is its generated reading view. Requirements remain in the handoff; technical decisions/evidence remain in their owning modules.
Human check: read the event quote, decision authority, disposition and linked record; correct any inference or wrong scope.
