---
id: VAL-003
type: validation
domain: schematic
status: verified
updated: 2026-10-04
---
# Original PowerPoint received and inspected

## Claim and revision
The original user-supplied PowerPoint is present, intact and mapped to three visually inspected source images. SHA-256: `5e2bca494bf6c9c81c61cfbdce5e4e2ac8458ad87ce4484ce45043bce83ae0ac`. Verification applies to intake/extraction and recorded source observations, not electrical correctness.

## Method
Python standard-library ZIP integrity, relationship/XML inventory and SHA-256 checks. Extract original PNG bytes; inspect all three using the image viewer, with independent visual review. Transcribe the printed BOM to CSV and reconcile easily misread reference labels against enlarged source images.

## Actual result
Three slides, one PNG per slide and no editable slide text. Original and extracted image identities are recorded in the manifest. The source identifies four 12AX7 and two EL34 tubes, preamp/channel switching/effects loop and power/supply circuitry. Fifty BOM groups are transcribed, preserving the LED quantity ambiguity and jack/control reference gaps. R21 in the 100k group was resolved visually; no duplicated R2 value conflict remains.

## Evidence
[Source inspection](../../sources/original-ppt/inspection.md), [manifest](../../sources/original-ppt/manifest.json), [as-printed BOM](../../sources/original-ppt/bom-as-printed.csv), and [source task](../../sources/original-ppt/task-P01-source-intake.md). The inspection links all source images and dated manufacturer checks separately from original-slide facts.

## Scope and follow-up
Missing-source dependency resolved. No completed native baseline, full net-by-net reconciliation, selected-component simulation, safety assessment, measured power or cabinet-fit evidence. Source construction ratings and legacy 120 V supplies cannot be adopted as a released 220 V / 50 Hz design without review.
