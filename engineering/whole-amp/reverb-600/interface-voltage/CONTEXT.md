# Reverb interface voltage review
Owner: electrical integration. One job: establish the native dry/wet interface voltage stresses that constrain component ratings and ground copper.
Inputs: ../circuit.json, ../cad, ../../pcb-measured-r/boards, existing effects-loop evidence and the declared contract.json fixtures.
Process: tools/simulate.py reads source values/pins and runs a bounded passive network in ngspice; tools/correct_metadata.py removes false voltage classifications; tools/check.py verifies exact permitted native changes and numerical cross-checks. The native circuit remains electrically unchanged.
Outputs: review.md, contract.json, results receipts and corrected native metadata. Factories are under tools; temporary circuit copies are not deliverables.
Done condition: quantify capacitor differential stress separately from node voltage, identify unsupported ratings, and prove metadata-only changes with native checks. This is not clearance or whole-amplifier qualification.
Human check: trace JR1 through R612 to JR5 and R618/C607 on the schematic; compare actual startup/fault measurements and selected connector insulation before accepting a ground pour or fabrication.
