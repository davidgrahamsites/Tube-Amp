# Secondary-loss evidence
Owner: Renegade integration. One job: retain reproducible evidence for the unadopted secondary-loss detector.
Inputs: ../../ac-loss-contract.json, ../../ac-loss-interruption-contract.json and auxiliary hold-up comparison decks.
Process: ../../tools/ac_loss_detector.py produces screen.json; ac_loss_interruptions.py produces interruptions.json; check_ac_loss.py independently audits both and the shared precision-monitor interface. Manufacturer documents remain under ../../evidence; source-observations.json preserves dated supplier fields and hashes.
Outputs: reports with exact decks, refinements, simulator logs, sourcing observations and checks.json. Candidate limits and false qualification flags are intentional.
Human check: compare physical secondary/ENV/reference/rail/contact timing with the declared allocations before native adoption. Five short restart cases and restoration chatter remain unresolved; inspect ac-loss-review.md.
