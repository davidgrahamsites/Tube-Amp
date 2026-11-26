---
id: VAL-065
type: validation
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Reverb voltage-spacing and interface acceptance

[Owned review](../../engineering/whole-amp/reverb-600/voltage-spacing/review.md) binds retained passive fault evidence to current participating values/pins and corrects JR1/JR5 canonical low-voltage requirements. Their XH 250 V candidate cannot cover the conditional 293.455/276.844 V envelope. K3's 138.422 V open wet-contact fault result exceeds its 125 V DC switching limit; actual fault-time contact operation needs qualification.

Unchanged active reverb board: old rules give zero DRC/opens; temporary 2.5 mm clearance / 4 mm creepage comparison gives 72/22 reports, zero opens. This is a provisional four-net comparison, not a certified insulation rule. Native header gaps are 0.84 mm; K3 wet-to-ground pad gap is 3.28 mm. Independent source/geometry checks and four negative controls pass. No copper, component or rule adoption.

Phoenix 7.62 mm header/plug is only a comparison lead. Chinese plug listing exists; live stock, exact header domestic availability, retention, hole tolerances and Shanghai delivery remain unverified. Preserve functional blocks; resolve exposure with approved loop/protection integration before committing to larger parts. All six scopes and fabrication release remain open.
