# Brownout timing evidence
Owner: Renegade integration. One job: retain failed slow-collapse baseline and raw-warning comparison evidence.
Inputs: ../../brownout-timing-contract.json, ../../raw-warning-contract.json, retained auxiliary decks, detector/precision-monitor records and manufacturer/source observations.
Process: ../../tools/brownout_timing.py writes screen.json; raw_warning.py reuses the same loaded-supply factory with an explicit candidate interface and writes raw-warning.json. check_brownout_timing.py audits both without native mutation. Reruns replace current reports/logs; exact decks and meaningful failed cases remain in the reports.
Outputs: screen, trial, source observations, simulator logs and checks. No accepted design is implied by passing evidence checks.
Human check: inspect the failed healthy-enable cases and measure actual relay contact/rail timing before any adoption. Follow ../../brownout-timing-review.md; nominal simulation is not manufacturing approval.
