# Panasonic FR-A exact packages
Owner: component-selection engineering. One job: translate three selected FR-A long-lead packages into reviewed native footprints.
Inputs: manufacturer September2025 radial catalogue, exact MPNs and seven active references.
Process: editable package-contract.json owns dimensions; tools/build_footprints.py generates the parent Renegade_Selected.pretty entries and dimensional receipts. PCB integration belongs to whole-amp/pcb-measured-r, not this factory.
Outputs: three local footprints, source excerpt, checks and preview.
Human check: verify suffix/packaging, received lead spacing and polarity; confirm finished-hole and registration tolerances with chosen PCB shop, and reserve vent/assembly space. No procurement or assembled-fit release.
Task card: input native revision3efa8d9; output seven consistent source/schematic/board assignments; dependencies stock refresh and manufacturer dimensions; owner primary agent; automated native parse, net preservation and DRC; done condition scoped package correction with remaining routing/physical holds explicit; estimate one engineering pass.
