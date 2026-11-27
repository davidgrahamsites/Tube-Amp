# Spacing evidence factories
Owner: integration. Inputs: ../contract.json and native files. Process: temporary rule tests and independent report audit. Outputs: ../results. Human check: trace a reported violation to the actual copper objects. Factories never edit active copper.

domain_screen.py owns VS-002 model/rule orchestration. It reads the existing wet-protection dc() calculation as a small domain interface, verifies current circuit values, independently solves KCL, and tests temporary boards. It never changes active copper. Human check: inspect C607 geometry and rule priority against the reported copper pairs.
