# Design-imperative review

One job: assess the imported design references against the current prototype requirements.

## Inputs
Seven unchanged parent-folder text files, canonical handoff, original schematic/BOM inspection, active prototype plan and simulation contract. Selected primary sources are checked October 4, 2026.

## Process
Read all originals, inventory their hashes and numbered rules, compare their scope/claims, and record findings in [REVIEW.md](REVIEW.md). Consolidate relevant checks without duplicating the source text. Keep pending design evidence separate from completed document checks.

## Outputs
`REVIEW.md`, `inventory.json` and `prototype-checks.csv`. The review is the public seam; the CSV is a starting evidence tracker, not passed circuit tests or a complete certification checklist.

## Human check
Resolve numerical targets, component selections and applicable standards with the design/review owner; record evidence or reasoned non-applicability for checks used in a release.
