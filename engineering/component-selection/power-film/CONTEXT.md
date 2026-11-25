# P057 power-film package comparison

Owner: Renegade integration. One job: compare exact P057 purchase candidates with the current Power-board package without adopting an unqualified part.

## Inputs
`../fc6136-fit-contract.json` owns the CRC extraction. `panasonic-contract.json` owns the alternative extraction and dated supplier observation. Read the cited manufacturer evidence and `../../whole-amp/pcb-measured-r/boards/Renegade_Power.kicad_pcb`. The circuit interface remains C12/C13/C25/C26, 50 uF each; no connectivity changes are authorized by this comparison.

## Process and task card
Run `tools/check_packages.py` with KiCad's Python. It reads native pads and compares nominal pitch, a rigid-lead tolerance witness and centered maximum-body envelopes. It cannot specify a production drill or assess arbitrary component collisions. Inputs are hashed and the native board is read only. Effort: one research/check checkpoint; dependency: exact manufacturer and Chinese supplier evidence; done condition: reproducible comparison and a concrete unresolved-integration list, not selected parts or build readiness.

## Outputs
`results/package-checks.json` is generated evidence; `review.md` is the engineering interpretation. `evidence/` holds source documents and dated read-only supplier receipts. Component coverage remains owned by the parent module; this module proposes an alternative only.

## Human check
Compare all four actual leads with a 1:1 insertion gauge; verify terminal pairs and seating height before the eventual footprint is released. Check the exact suffix and delivered quote. No supplier message, order or fabrication upload is performed here.
