---
id: VAL-006
type: validation
domain: cross-domain
status: verified
updated: 2026-10-04
---
# Design-imperative document and applicability review

## Claim and revision
All seven user-supplied `.txt` references in `Design Imperatives/` were read and compared with the current Renegade prototype requirements. The [inventory](<../../Design Imperatives/review/inventory.json>) identifies the reviewed byte revisions by SHA-256, file size and numbered-rule locations. Verification is limited to document coverage, inventory integrity and the specific primary-source/arithmetic checks recorded in the review.

## Method
Read the seven originals, distinguish numbered rules from uppercase section headings, verify each rule sequence and inventory the original bytes with Python SHA-256. Compare guidance with the canonical handoff, source intake, active prototype plan and simulation contract. Check selected claims against NDRC supply rules, SAMR standard records, KiCad 10 documentation, ADI AN-937, JJ tube datasheets, Hammond's rectifier guide and tube-specific grid-resistor references. Preserve original files; write findings and pending evidence areas separately.

## Actual result
Seven files contain 364 numbered items, with per-file rule sequences complete. Guidance broadly supports the prototype requirements. Findings include a tube-grid citation mismatch, a missing second heater datasheet, scope qualifications for grounding/device examples/standards, and absent design-specific numerical limits. The primary supply text supports normal single-phase +7%/−10% deviation, giving 198–235.4 V; planned simulation cases were updated while retaining 242 V as separate engineering stress. The 0.6 A JJ heater example and ideal 580 V bridge peak arithmetic are consistent with the named evidence.

Twenty consolidated evidence areas were created, all pending evidence. No circuit, new amplifier simulation, PCB rule execution, cabinet fit, component choice or hardware acceptance was performed by this review. The original Ministry of Justice source URL could not be fetched in this check; an accessible NDRC primary text supports the supply claim. Remaining citations were not exhaustively validated.

Fresh artifact checks confirmed seven inventory hashes/sizes match the originals, 364 ordered unique rule IDs, 20 unique pending tracker rows with valid original-rule references, 13 unique source-register IDs and 104 existing local Markdown link targets. Brain catalog regeneration reported 18 valid nodes. The ICM structural checker reported clean for `Design Imperatives`, `brain`, the active prototype plan and `simulation`. These are documentation integrity checks, separate from engineering acceptance.

## Evidence
- [Review and primary-source links](<../../Design Imperatives/review/REVIEW.md>)
- [Original-byte inventory and rule IDs](<../../Design Imperatives/review/inventory.json>)
- [Prototype evidence tracker](<../../Design Imperatives/review/prototype-checks.csv>)
- [Updated simulation contract](../../simulation/requirements.md)
- [Active prototype plan](../../plans/renegade-working-prototype/plan.md)

## Scope and follow-up
Derive numerical ratings, clearances/creepage, current/thermal constraints and performance criteria from exact parts and the reviewed circuit. Populate each relevant tracker row with responsible owner, method, acceptance limit, revision and evidence; justify non-applicability by actual topology. Verify other citations when a design decision relies on them. The handoff remains canonical and imported guidance does not approve fabrication or energizing hardware.
