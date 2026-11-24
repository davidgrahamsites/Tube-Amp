# Socket coverage checker
Owner: Renegade integration. One job: compare the reviewed socket plan to active device identities.
Inputs: parent socket-plan.json, canonical circuit and component coverage.
Process: audit_socketing.py reads these inputs without mutating them; rejects omissions, duplicates, conflicting units and unsubstantiated qualification. Includes negative controls for a missing regulator and an added IC.
Outputs: ../results/socket-audit.json. No native CAD changes.
Human check: review every unresolved device; an accurate inventory is not a socket qualification pass.
