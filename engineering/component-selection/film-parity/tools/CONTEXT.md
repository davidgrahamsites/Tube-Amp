# Film identity factories
Owner: Renegade integration.
Inputs: ../contract.json, native source/schematic, selected KNSCHA part dossier and immutable baseline exports.
Process: synchronize.py performs a guarded hidden-metadata update. check.py independently validates complete pin partitions, allowable metadata deltas, physical-board preservation and exact local footprint pads. Exports use installed KiCad CLI; raster comparison uses PyMuPDF.
Outputs: native metadata and ../results receipts. No board routing, unrelated component selection or physical qualification side effects.
Human check: review exact part-to-footprint assignment and compare physical lead/body measurements with retained manufacturer drawings.
