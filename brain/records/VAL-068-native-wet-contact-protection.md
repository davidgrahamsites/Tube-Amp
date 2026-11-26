---
id: VAL-068
type: validation
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Native wet-contact correction

The VAL-067 opposing-series clamp and coordinated resistor corrections are implemented in source, native07c and Reverb PCB. D603/D604 are exact Vishay BZX55C27-TAP; R616 is100ohm PR01000101000JA5001W/5%; R618 is1M MF0207FTE52-1M350V. Functional blocks and existing resistor values remain intact.

Owner and reproducible evidence: [integration contract](../../engineering/whole-amp/reverb-600/wet-protection-integration/CONTEXT.md), [review](../../engineering/whole-amp/reverb-600/wet-protection-integration/review.md), [checks](../../engineering/whole-amp/reverb-600/wet-protection-integration/results/checks.json).

Explicit net-delta and polarity negative control pass;240components/621connected pins match the circuit contract.20other native files preserved,17page rasters identical. ERC remains one existing bond naming warning; Reverb DRC0/opens0 under current rules.140prior drill hits preserved, four0.9mm diode holes added, two R616 holes changed to0.9mm. Board outline/mounts unchanged.192-case resistor tolerance screen gives0.000193552dB maximum gain change; power/relay hardware exclusions remain.

China exact-part indexed listing/MOQ evidence is retained, not live stock or confirmed Shanghai checkout. Full voltage spacing, contact life, power sequencing, loop/expression adoption, remaining routing and populated three-board/drill fit remain incomplete. No fabrication release. Next: qualify the tube-level interboard connectors/spacing, continue remaining integrated circuit corrections and populated chassis assembly.
