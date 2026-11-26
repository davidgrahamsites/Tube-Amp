# Socketed-device qualification
Owner: Renegade integration. One job: account for replaceable sockets for every IC and tube.
Inputs: ../../whole-amp/reverb-600/circuit.json, ../coverage.json, FB-116 default as qualified by FB-117 and policy.md, socket-plan.json and dated supplier observations.
Process: edit socket-plan.json for reviewed engineering decisions; tools/audit_socketing.py compares it with the actual circuit and emits explicit pending gates. Dated observations are evidence, never automatic part selections. Keep native PCB changes in the PCB module.
Outputs/public seam: results/socket-audit.json and review.md. The manifest supplies requirements to component selection and the populated chassis, not fabrication dimensions.
Human check: trace each physical package to its socket drawing, pin-1 orientation, lead acceptance range, maximum fitted height, extraction path and retention. Verify an actual sample before releasing footprints.

Current dimensional seam: socket-envelope.json carries provisional TE DIP candidate bounds to mechanical/tools/check_socket_fit.py. te-candidate-review.md separates nominal compatibility from release qualification. No native footprint or purchase is silently changed by this manifest.

Draft footprint correction: footprint-contract.json declares the five native package changes and C352 clearance repair. Read footprint-review.md and results/footprint-checks.json; adopted draft geometry is distinct from final socket qualification.

Contact tolerance seam: contact-fit-contract.json records exact lead/contact evidence; tools/check_contact_fit.py emits results/contact-fit.json. contact-review.md explains rejected fits and retains cooling requirements by linking to the auxiliary-supply owner. No contact selection or native mutation.
