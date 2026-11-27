# Fit review products
Owner: integration agent. One job: record this fit assessment and outstanding checks.
## Inputs
`../fit-register.json`, `../evidence/`, `../tools/check_fit.py`.
## Process
Keep measured, published, inferred and assumed data distinct. Record failed screens without manufacturing claims.
## Outputs
`fit-screen.json`, `fit-review.md`, `tank-specifications.md`, supplier clarification draft and visual review.
## Human check
Review the complete installed assembly and supplier clarification before a fit release.

Current generated products also include panel face/underside SVG/PDFs, A4 paper tiles, dimensional JSON and a pot terminal CSV. The measurement-guide PNG is a generated teaching illustration accompanied by exact written start/end instructions; it is not source geometry or proof of cabinet fit.

socket-fit-diagnostic.FCStd/STEP and socket-fit-cad-checks.json retain the current five-DIP envelope trial. tool-access-review.md/checks.json separate received chuck diameter from proposed handling margin and pending full approach.

FIT-012 products: bench-tool-access.html is the editable human report; bench-tool-access.json is the native geometry screen. bench-access-bounds.FCStd/.step contain current board solids and known package bounds only. bench-access-cad-checks.json records independent intersections and export roundtrips. Do not use the exploded display positions as cabinet placement or these bounds as a manufacturing release.
