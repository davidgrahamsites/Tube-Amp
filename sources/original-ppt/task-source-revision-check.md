---
id: TASK-P01-REVISION
type: task
domain: schematic
status: documented
updated: 2026-10-04
---
# Source revision check

## Owner and dependencies
Root agent owns the comparison and documentation. Depends on the prior intake manifest and retained source images.

## Inputs
Current `Renegade Tube Amp.pptx`, SHA-256 `00c43b64bb87dee26b7982b797921cbb307a56d60e0324fe06e7f86d9d6eecc9`; prior archive hash and three extracted image hashes in `manifest.json`.

## Outputs
`revision-check-2026-10-04.json`, brain record VAL-007 and source/project status notes. Preserve the current presentation and historical manifest/images.

## Method and automation
Python standard-library ZIP integrity, relationship/XML parsing, SHA-256 and image byte comparisons. Circuit Design Skill Ladder L0 and PPTX source inspection. No circuit modification or energized human measurements required.

## Done-condition and evidence
Completed: identify whether source schematic/BOM image content, order, transforms or crops changed. All match the prior intake; archive hash differs. No new native amplifier schematic found. User intent remains to be clarified.

## Effort and stopping conditions
Approximately ten minutes, including documentation. Prior archive bytes are unavailable for a complete package diff. A different updated drawing or clarification is needed to review an actual circuit revision.
