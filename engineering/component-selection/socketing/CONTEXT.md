# Socketed-device qualification
Owner: Renegade integration. One job: account for replaceable sockets for every IC and tube.
Inputs: ../../whole-amp/reverb-600/circuit.json, ../coverage.json, FB-116 default as qualified by FB-117 and policy.md, socket-plan.json and dated supplier observations.
Process: edit socket-plan.json for reviewed engineering decisions; tools/audit_socketing.py compares it with the actual circuit and emits explicit pending gates. Dated observations are evidence, never automatic part selections. Keep native PCB changes in the PCB module.
Outputs/public seam: results/socket-audit.json and review.md. The manifest supplies requirements to component selection and the populated chassis, not fabrication dimensions.
Human check: trace each physical package to its socket drawing, pin-1 orientation, lead acceptance range, maximum fitted height, extraction path and retention. Verify an actual sample before releasing footprints.
