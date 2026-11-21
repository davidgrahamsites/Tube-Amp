---
id: VAL-007
type: validation
domain: schematic
status: verified
updated: 2026-10-04
---
# Supplied PowerPoint revision comparison

## Claim and revision
After the user's “Updated schematic” message, the current `Renegade Tube Amp.pptx` has SHA-256 `00c43b64bb87dee26b7982b797921cbb307a56d60e0324fe06e7f86d9d6eecc9`, differing from the archive hash recorded by [VAL-003](VAL-003-original-ppt-intake.md). Its three embedded schematic/BOM images remain byte-for-byte identical to the retained intake images. Their order, placement transforms and crop settings also match the prior manifest.

## Method
Python 3.13.2 standard-library `zipfile`, `hashlib` and `xml.etree.ElementTree`: run ZIP integrity checking, resolve presentation and slide relationships in slide order, hash and directly compare each image with the retained extracted file, normalize XML transforms for comparison, and inventory slide text/shapes and notes. Compare with the preserved intake manifest rather than replacing historical evidence.

## Actual result
ZIP integrity passed. Three slides, each with one image and no editable text or additional circuit drawing shapes. Three of three image hashes and direct byte comparisons match; three of three transforms/crops match. No notes-slide text is present. No revised circuit content was found in the current PowerPoint. The only native schematic located in the workspace remains the library preview.

## Evidence
[Comparison report](../../sources/original-ppt/revision-check-2026-10-04.json), [prior manifest](../../sources/original-ppt/manifest.json), [prior inspection](../../sources/original-ppt/inspection.md), and [task card](../../sources/original-ppt/task-source-revision-check.md).

## Scope and follow-up
This verifies source-content continuity, not electrical correctness. The previous archive bytes were not available for a complete package diff, so the cause of the archive hash change is unknown. A changed package hash alone does not establish a circuit revision. The user subsequently clarified that they want creation of the revised schematic, not intake of another drawing; see [VAL-009](VAL-009-updated-schematic-draft.md).
