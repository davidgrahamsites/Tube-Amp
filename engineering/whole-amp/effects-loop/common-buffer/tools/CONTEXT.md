# Headroom comparison factories
Owner: integration. Inputs: ../contract.json and existing full-circuit fixture. Process: generate decks, bounded SPICE workers, independent metric audit. Outputs: ../results. Human check: inspect the explicit clipping equation and compare results at equal stimulus. No active CAD writes.

composite_return.py owns the CB-002 standalone experiment. It reads composite-return.json, writes bounded per-case decks/receipts, and calls the existing spice_runtime adapter. Stable parameters stay outside results. No current native circuit is synthesized from this experiment.
