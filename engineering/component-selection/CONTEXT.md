# Exact component selection
One job: choose documented, quantity-one-build parts for the current amplifier revision.
Inputs: whole-amp circuit/fit requirements, coverage.json, candidate-register.json and dated supplier/manufacturer evidence.
Process: evidence dossiers justify selections; coverage.json maps native references to requirements and selected MPNs; build_selected_bom.py produces the selected subset. Old revisions may have different reference values; each change must name its revision. Supplier observations retain their original date.
Outputs: selected-engineering-bom.csv, summary, component dossiers and integration manifests. These are engineering choices, not purchase authorization or a complete order list.
Human check: confirm exact ordered suffix, package, current domestic availability and as-received dimensions before PCB manufacture or assembly.

P057 candidate fit: fc6136-fit-contract.json is the reviewed extraction from CRC approval 26124D02. It is not an adopted footprint. The native-board adapter and rejection evidence live in ../whole-amp/pcb-measured-r/tools/check_fc6136_fit.py and review/fc6136-fit-review.md. Coverage must not conflate CRC candidate dimensions with the native Panasonic package.
