# Catalog factories
Owner: memory integration. One job: generate navigable, checked views of canonical project records.

## Inputs
Frontmatter in `../rules/*.md` and `../records/*.md`.
The project catalog additionally reads `../materials/register.json`, `../feedback/events.json`, `../../engineering/component-selection/coverage.json` and visible workspace file metadata/content for hashes.

## Process
Run `python3 brain/tools/build_index.py` from the project root. Validate fields, allowed values, dates and duplicate IDs before writing the index.
Run `python3 brain/tools/build_project_catalog.py --as-of YYYY-MM-DD` with the client date for project materials, feedback and complete visible-file inventory. No tool writes engineering CAD, simulations or source inputs.

## Outputs
`../INDEX.md`; content files remain unchanged.
Project-wide products are `../catalog/WORKSPACE.md`, `FEEDBACK.md`, `FILES.json` and `checks.json`.

## Human check
Follow a task's rule-set and record links. The catalog reports recorded status and does not establish engineering correctness.
