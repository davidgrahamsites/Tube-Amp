# Socket coverage evidence
Owner: Renegade integration. Inputs: socket-plan.json and canonical circuit through ../tools/audit_socketing.py.
Process: overwrite the current generated JSON when inputs change; retain the source hashes and explicit hold reasons.
Outputs: socket-audit.json consumed by review.md and the chassis task.
Human check: distinguish inventory checks from fabrication_ready; pending sockets must not become an approved BOM by inference.

footprint-checks.json, socket-*-drc.json, socket-erc.json and socket-netlist.xml are bounded native correction evidence. socket-control.pdf and socket-reverb.pdf are reviewed native plots, not fabrication packages.
