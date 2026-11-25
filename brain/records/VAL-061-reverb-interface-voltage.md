---
id: VAL-061
type: validation
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Reverb interface ratings and differential capacitor stress

[Owned review](../../engineering/whole-amp/reverb-600/interface-voltage/review.md) corrects JR1/JR5's misleading low-voltage ratings in source, native sheets/board and derived connectivity, and removes “LV” from the board legend/factory. Electrical values, pins, copper and drills are preserved. Native checks retain 144 nets, 236 components, 18 pixel-identical schematic pages, one existing ERC finding and zero Reverb DRC/opens. Existing clearance rules remain unqualified.

72 source-derived passive ngspice solves complete: 48 AC contributions, 18 conditional cold-plate transients and six C6-short DC screens. Independent nodal/DC arithmetic agrees within 9.1e-12 V. C607 differential peaks are 1.194 V in the larger audio fixture, 22.536 V in the declared healthy-C6 startup screen and 153.422 V in the available-rail C6-short bound. The last exceeds its 63 V rating. This is a conditional fault screen, not a measured failure or guaranteed single-fault maximum. Actual op-amp clamps, main-stage AC loading, tolerances and supply/heater sequencing remain outside the model.

No ground pour or new component is adopted. Next: resolve voltage-rated coupling/protection and real input clamp/rail injection; establish connector/net-specific spacing and rebuild the plane. China purchase/Shanghai delivery and all six build scopes remain incomplete. No supplier contact, purchase or fabrication release.
