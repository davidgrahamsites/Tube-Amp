# Design journal contract

Owner: Luna journal agent. The integration coordinator owns canonical records, shared feedback, and catalogs; this module owns derived narrative only.

## Inputs
Canonical project requirements and engineering evidence under `brain/records/`, owned engineering review files, machine-readable result receipts, and the current baseline ID supplied at each checkpoint.

## Process
Write a chronological, source-linked narrative of engineering problems and decisions for future design-guide and build-series use. Each chapter distinguishes reported facts, calculations, engineering interpretation, formal authority, implementation, verification, and open checks. Under FB-148, document every material calculation alongside the choice it informs: define symbols and units, cite inputs, show equation and numeric substitution, report result, validation, assumptions, and scope limits. Link canonical records instead of maintaining duplicate requirements. Never invent dialogue, measurements, failures, approvals, implementation, or physical-build outcomes. Mark pending coordinator verification plainly. Historical math coverage stays explicitly incomplete until backfill is audited.

## Outputs
`README.md` is the entry index and editorial contract; `entry-template.md` is the stable chapter shape; `chapters/` contains narrative entries; `calculations/` contains readable, source-linked derivations; `HANDOFF.md` records the next journal action and coverage/backfill queue.

## Review seam
The journal owner checks narrative accuracy and source links. The integration coordinator verifies new canonical evidence and authority before a pending claim is promoted. Neither review turns simulation or CAD evidence into physical qualification.

## Human check
Before using any chapter in a public guide or post, follow its linked evidence and confirm that later project records have not superseded the described state; preserve all stated conditions and unresolved limits.

Writing rule: follow [the maintenance-English standard](../engineering-reader/document-standard.html) before delivery. Use short direct sentences, one action per procedure step, consistent part names and defined terms. State the check, expected result and failed-check action. Preserve calculations and limits. Review each new or revised HTML chapter; do not claim untouched history has passed this review.
