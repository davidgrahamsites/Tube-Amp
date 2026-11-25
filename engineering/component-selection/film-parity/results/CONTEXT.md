# Film identity reconciliation evidence
Owner: Renegade integration.
Inputs: ../contract.json, fixed baseline KiCad exports and exact manufacturer/selection evidence.
Process: native before/after exports, complete connectivity and allowed metadata comparison, unchanged board hashes, all-page raster equality and part/footprint checks. Factories remain in ../tools.
Outputs: one before/after export pair, check receipts and dated sourcing observations. HTTP failures remain recorded; historical stock is never relabeled fresh.
Human check: inspect the changed part identities in KiCad and confirm the actual delivered parts before assembly. Global fit, thermal and supply sequencing remain outside this evidence.
