# KiCad engineering brain
One job: retain retrievable engineering knowledge as the project develops.

## Inputs
[Source register](sources.md), [generated catalog](INDEX.md), and task-relevant files under `rules/` and `records/`.

## Process
Apply [continuous feedback capture](rules/feedback.md) during every active project session. Route through [the project-wide catalog](catalog/WORKSPACE.md); append attributed feedback to `feedback/events.json` and resolve it into the existing canonical record. Do not create a second requirements database.

1. Read the relevant domain rule-set, then specific records and evidence.
2. Capture a reusable rule, decision, component finding, or check in one canonical home; link existing facts instead of copying them.
3. Copy a template for new records. Use a stable ID, type, domain, status, update date, and evidence links.
4. State assumptions, scope, alternatives and the next check. Historical ChatGPT suggestions and supplier titles are not verification.
5. After meaningful work, update affected records and project status; run `python3 brain/tools/build_index.py`.
6. Rebuild the materials/feedback views with `python3 brain/tools/build_project_catalog.py --as-of YYYY-MM-DD`, using the client date. Resolve reported missing paths, duplicate IDs and reference ownership before handoff.

## Outputs
- `rules/`: reusable guidance with stable individual rule IDs.
- `records/`: project-specific decisions, part dossiers and validation results.
- `_templates/`: starting shapes for new records.
- `INDEX.md`: generated lookup; never edit by hand.

## Schema and evidence
Types: `rule-set`, `decision`, `component`, `validation`.
Domains: `schematic`, `bom`, `components`, `pcb`, `manufacture`, `cross-domain`.
Statuses: `documented` (recorded practice or requirement), `proposed`, `selected` (chosen, not necessarily verified), `verified` (a scoped claim supported by evidence), `blocked`, `superseded`.
Every node has YAML frontmatter: `id`, `type`, `domain`, `status`, `updated` (YYYY-MM-DD).
Verification applies only to the stated claim, revision and conditions. Preserve failures and superseded reasoning. Record actual manufacturer documents, dated supplier specifications and measurement conditions when verifying parts.

## Human check
The user can edit any record. Seek decisions when evidence cannot resolve a material choice. Keep unresolved choices explicit and preserve the engineering review boundary in [the handoff](../Renegade_Codex_Handoff.md).

## Retrieval
Start with `INDEX.md`, read the domain rule-set, then the specific record, then its evidence. Avoid loading the entire brain.
