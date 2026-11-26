# FMP200 finished-hole correction
Owner: PCB integration. One job: correct insertion clearance on the 13 existing Main/Power FMP200 footprints and their library.
Inputs: contract.json, its baseline revision, manufacturer FMP V9 and existing selected-part coverage.
Process: tools/integrate.py makes a guarded local geometry-only edit; tools/export.py retains before/after KiCad DRC/drills; tools/check.py independently verifies exact deltas and net/placement preservation.
Outputs: updated footprints/boards, results evidence, per-reference package envelopes and review.md. This does not requalify resistor operating stress.
Human check: confirm purchased standard lead suffix/dimensions, fabricator finished-hole/registration tolerance and formed pitch before assembly; do not assume nominal hole is the finished minimum.
