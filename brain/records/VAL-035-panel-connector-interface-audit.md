---
id: VAL-035
type: validation
domain: components
status: documented
updated: 2026-11-24
---
# Panel connector and crimp interface audit

[Harness integration](../../engineering/whole-amp/harness-integration/review.md) derives all thirty terminal assignments for ten panel pots from the current circuit, preserving Main/Reverb ownership. Two existing pot-to-pot nets need board nodes if each pot receives its own PCB plug. Current individual Main wire pads and generic JR4 are not the completed connector design.

Manufacturer tooling data resolves 638190000 applicability to 430300008 and adds the missing minimum insulation diameter. Installed footprint nominal hole/locator geometry agrees with the family drawing text; full visual/tolerance/mating evidence remains pending. Mapping, native preservation and negative controls pass; no active CAD changed. Chinese catalogue leads exist but exact current stock, wire and Shanghai delivery are not qualified.

Next: exact cable and complete connector geometry, then explicit schematic interfaces and three-board placement. Physical crimps, voltage/fault spacing and populated access remain open. All six overall scopes remain in progress.
