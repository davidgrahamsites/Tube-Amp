# Exact component selection
One job: choose documented, quantity-one-build parts for the current amplifier revision.
Inputs: whole-amp circuit/fit requirements, coverage.json, candidate-register.json and dated supplier/manufacturer evidence.
Process: evidence dossiers justify selections; coverage.json maps native references to requirements and selected MPNs; build_selected_bom.py produces the selected subset. Old revisions may have different reference values; each change must name its revision. Supplier observations retain their original date.
Outputs: selected-engineering-bom.csv, summary, component dossiers and integration manifests. These are engineering choices, not purchase authorization or a complete order list.
Human check: confirm exact ordered suffix, package, current domestic availability and as-received dimensions before PCB manufacture or assembly.

P057 candidate fit: fc6136-fit-contract.json is the reviewed extraction from CRC approval 26124D02. It is not an adopted footprint. The native-board adapter and rejection evidence live in ../whole-amp/pcb-measured-r/tools/check_fc6136_fit.py and review/fc6136-fit-review.md. Coverage must not conflate CRC candidate dimensions with the native Panasonic package.

P057 sourcing alternative and full-pitch insertion check: [power-film/CONTEXT.md](power-film/CONTEXT.md) owns the read-only comparison with Panasonic EZPV60506MTC. Its dated RS China observation does not select or release either candidate.

Socket requirement: socketing/CONTEXT.md owns the exhaustive IC/tube manifest and qualified-contact gates. Native replacement geometry remains a PCB-module responsibility.

C607 voltage-rated coupling replacement: [reverb-coupling/CONTEXT.md](reverb-coupling/CONTEXT.md) owns exact part sourcing, package integration and preserved connectivity/drill evidence after VAL-061's conditional fault finding.
