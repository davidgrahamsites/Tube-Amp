---
id: TASK-P01-SOURCE
type: task
domain: schematic
status: documented
updated: 2026-10-04
---
# Original-source intake for P01

## Owner and dependencies
Root agent owns extraction, source transcription and integration. An independent visual reviewer audits the source images under the PowerPoint skill. P01 also includes later baseline/target review; this record covers its source-intake portion only.

## Inputs
User-supplied `Renegade Tube Amp.pptx` in the project root, SHA-256 `5e2bca494bf6c9c81c61cfbdce5e4e2ac8458ad87ce4484ce45043bce83ae0ac`. Canonical handoff and active prototype plan.

## Outputs
This folder's slide images, manifest, as-printed BOM CSV and inspection. Project status, active planning dependencies and brain evidence updated. Original retained unchanged.

## Method and automation
Python standard-library ZIP/XML/hash/CSV tools; visual inspection of all three original embedded PNGs. No crop or rotation is recorded in the source XML. The diagrams are raster content, so editable-text extraction alone would lose the circuit.

## Done-condition and evidence
ZIP integrity checked; all three slides mapped to extracted images, with per-image hashes. Visual content and the 50 printed BOM groups recorded. Independent findings integrated in `inspection.md`. Fresh verification checks hashes, image mapping, CSV quantities/references and document links. No native amplifier schematic or validated purchasing BOM produced in this task.

## Effort and stopping conditions
Source recovery is complete. Ambiguous references, ratings and connectivity require reconciliation during baseline capture. Cabinet fit work still requires usable shell/chassis dimensions and selected part envelopes. Source receipt does not finish all of P01.
