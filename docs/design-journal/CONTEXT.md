# Design journal contract

Owner: Luna journal agent. The integration coordinator owns canonical records, shared feedback, and catalogs; this module owns derived narrative only.

## Inputs
Canonical project requirements and engineering evidence under `brain/records/`, owned engineering review files, machine-readable result receipts, and the current baseline ID supplied at each checkpoint.

## Process
Write a chronological, source-linked narrative of engineering problems and decisions for future design-guide and build-series use. Each chapter distinguishes reported facts, calculations, engineering interpretation, formal authority, implementation, verification, and open checks. Link to canonical sources instead of maintaining duplicate requirements. Never invent dialogue, measurements, failures, approvals, implementation, or physical-build outcomes. Mark pending coordinator verification plainly.

## Outputs
`README.md` is the entry index and editorial contract; `entry-template.md` is the stable chapter shape; `chapters/` contains narrative entries; `HANDOFF.md` records the next journal action and current backfill queue.

## Review seam
The journal owner checks narrative accuracy and source links. The integration coordinator verifies new canonical evidence and authority before a pending claim is promoted. Neither review turns simulation or CAD evidence into physical qualification.

## Human check
Before using any chapter in a public guide or post, follow its linked evidence and confirm that later project records have not superseded the described state; preserve all stated conditions and unresolved limits.
