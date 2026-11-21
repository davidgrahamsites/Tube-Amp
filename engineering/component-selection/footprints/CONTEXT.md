# Selected-part footprint preparation
Inputs: component dossiers, manufacturer package dimensions and original native-board hashes.
Process: footprint factories prepare local KiCad geometry and integration-manifest.json records intended assignments. Preserve native boards; this folder does not own final placement/routing.
Outputs: footprint libraries, previews, dimensional checks and a planned integration manifest.
Human check: compare physical purchased parts and manufacturer maximum dimensions with pads/courtyards before integrating or fabricating.
