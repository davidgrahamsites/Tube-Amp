# Socket coverage checker
Owner: Renegade integration. One job: compare the reviewed socket plan to active device identities.
Inputs: parent socket-plan.json, canonical circuit and component coverage.
Process: audit_socketing.py reads these inputs without mutating them; rejects omissions, duplicates, conflicting units and unsubstantiated qualification. Includes negative controls for a missing regulator and an added IC.
Outputs: ../results/socket-audit.json. No native CAD changes.
Human check: review every unresolved device; an accurate inventory is not a socket qualification pass.

build_footprints.py emits the two declared candidate libraries; check_footprints.py independently checks exact source/native/drill deltas against footprint-contract.json baseline. Native mutation belongs to pcb-measured-r/tools/integrate_socket_footprints.py.
