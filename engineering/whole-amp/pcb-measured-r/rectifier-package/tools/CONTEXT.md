# Rectifier package factories
Owner: PCB integration. One job: reconcile selected D3–D6 identity and geometry.
Inputs: ../contract.json and its guarded native baseline.
Process: tools prepare a guarded candidate; adopt only after native validation, visual inspection and preservation checks. No board regeneration.
Outputs: scoped candidate generation and read-only native validation; no fabrication approval.
Human check: compare cathode bands, maximum lead/body dimensions, lead forming/support, current/heat and voltage spacing against the physical assembly. Thermal ratings and actual cabinet fit remain independent gates.
