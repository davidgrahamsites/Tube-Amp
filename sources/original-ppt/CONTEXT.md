# Original amplifier PowerPoint evidence

One job: inspect the original amplifier drawing and BOM without changing the supplied presentation.

## Inputs
[Renegade Tube Amp.pptx](<../../Renegade Tube Amp.pptx>), received October 4, 2026. Source identity and slide/image mapping are in `manifest.json`.

## Process
Extract the original embedded images byte-for-byte, inspect all three at readable resolution, and record source facts and unresolved conflicts in `inspection.md`. Raster images contain the schematic text; absence of editable slide text does not imply absent circuitry.

## Outputs
`slide-01.png`, `slide-02.png`, `slide-03.png`, `manifest.json`, `bom-as-printed.csv`, `inspection.md` and `task-P01-source-intake.md`. Derived facts must cite the slide, not a historical guess. The source BOM transcription preserves printed values and conflicts; it is not a purchasing BOM.

## Human check

Subsequent source comparisons live in dated `revision-check-*.json` reports and task cards; retain the original manifest and extracted image evidence. The October 4 comparison is recorded in [VAL-007](../../brain/records/VAL-007-source-revision-comparison.md).
Review uncertain symbols/values and BOM conflicts against the source before baseline capture or parts selection.
