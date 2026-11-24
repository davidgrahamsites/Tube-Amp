# Reset / relay evidence
Owner: Renegade integration. Inputs: ../contract.json and factories in ../tools, manufacturer model in ../models.
Process: replace current result files on rerun, retain exact decks/hashes and meaningful pass/fail metrics. No fabricated bench results.
Outputs: bounds.json, reset-screen.json, driver-screen.json, simulator logs and later native-check evidence if adopted. Human check: read ../review.md, inspect failed cases and qualification limits before using any candidate in production.

edge-* artifacts are the current reset-edge checkpoint. edge-integration.json describes an intermediate revision; edge-native-checks.json owns final native hashes. edge-before-10_logic_power.pdf and driver-sheet.pdf are the one preceding copy of their corresponding current sheet exports, not alternate editable projects.
