# Package comparison factory
`assembly_options.py` uses ordinary Python and the two candidate contracts for lead-length and conditional body-envelope arithmetic. It writes `../results/assembly-options.json`; no native CAD is changed. Human check: confirm that body extents exclude PCB margins, supports, connectors and access space.

Owner: component selection. Inputs: parent candidate contracts, manufacturer PDF and read-only native Power board. Process: `check_packages.py`, using installed KiCad Python; asserts pad identities and rectangular geometry, screens a tolerance witness, and compares candidate body envelopes. Output: `../results/package-checks.json`. Human check: examine the separate nominal, tolerance and body results; a successful script is not assembly approval.
