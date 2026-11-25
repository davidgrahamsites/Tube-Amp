# expression-control contract

Owner: Renegade integration agent. One job: own the protected low-voltage expression-pedal interface.

## Inputs
Paths in this contract are project-root-relative unless named as local. Read `engineering/whole-amp/expression-control/requirements.md`, `brain/records/DEC-016-buffered-loop-expression-selector.md` and `engineering/whole-amp/reverb-600/circuit.json`. Local edit surfaces are requirements.md, selector-review.md and ota-review.md.

## Process
User requested PANEL / EXPRESSION selection; exact control circuit and PCB integration are pending. tools/ota_screen.py screens the isolated audio gain cell; tools/audit_ota.py checks its retained evidence. models/ contains the unmodified manufacturer input and manifest; results/ contains repeatable run products. No native CAD mutation belongs to these factories. Pedal control/protection is a separate interface from audio gain-cell evaluation within this module.

## Outputs
ota-review.md interprets results/ota-screen.json and ota-audit.json; selector-review.md defines the proposed control interface. The current experiment is not an implemented expression feature. `brain/catalog/FILES.json` indexes roles and hashes; `brain/materials/register.json` identifies the owning material route.

## Human check
Open the local output with its source/reference and confirm revision, unresolved limits and actual part or circuit identity before using it for the build. For native CAD, inspect the render and pin/geometry checks; for runs, inspect assumptions and logs.
