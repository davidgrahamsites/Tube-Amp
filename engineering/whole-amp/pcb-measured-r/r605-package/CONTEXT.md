# R605 package integration
Owner: PCB integration. One job: replace the physically undersized R605 package with the documented conditional FMP200 candidate, preserving circuit behavior.
Inputs: contract.json, its immutable baseline Git revision, current native board and 07a schematic, Yageo FMP V9 and VAL-069 current budget.
Process: tools/integrate.py makes a hash-guarded local package/route edit; tools/export_native.py exports before/after; tools/check.py checks topology, native preservation, drills, DRC and conditional power.
Outputs: one local footprint and corrected native metadata/placement, results evidence and review.md. This does not select a purchasable part or approve hot/fault operation.
Human check: verify actual resistor identity, body/lead dimensions and formed pitch; measure local/body/PCB temperature under agreed load/fault tests and confirm provisional 3mm standoff/7.2mm height before manufacture.
