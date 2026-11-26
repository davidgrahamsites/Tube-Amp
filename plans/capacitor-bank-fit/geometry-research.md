# Capacitor-bank geometry research

2026-11-26. Independent dimensional review of v2; local sources only. Scope: conservative maximum capacitor bodies and conditional orientation arithmetic. No native/shared-register edits, candidate adoption, insulation allowance, assembled fit or fabrication approval.

## Inputs and dimensional authority

- [Panasonic contract](../../engineering/component-selection/power-film/panasonic-contract.json): EZPV60506MTC, nominal 57 × 25 × 40 mm plus 1 mm on each maximum dimension gives **58 × 26 × 41 mm**. Four 50 µF, 600 V candidate bodies. The recorded 10 mm neighbor recommendation is a manufacturer body-spacing condition; it is not an HV insulation distance.
- [CRC contract](../../engineering/component-selection/fc6136-fit-contract.json): FC6136, nominal 57.5 × 35 × 50 mm plus 1 mm gives **58.5 × 36 × 51 mm**. Four 50 µF, 900 V candidate bodies. No CRC neighbor gap is established by this contract. Its four-terminal grouping and maximum lead diameter remain open.
- [Current board inventory](../../engineering/whole-amp/pcb-measured-r/review/mechanical-inventory.json): Main 290 × 140, Power 160 × 175, Control 230 × 110, Reverb 160 × 100 mm; all nominal 1.6 mm thick. These are current native outline dimensions, not complete populated envelopes or a three-board implementation.
- [Mechanical register](../../engineering/whole-amp/mechanical/fit-register.json): received width readings 467 mm, a 160 mm depth reading with unconfirmed endpoints, and 383 mm reported inside height do **not** define one verified empty usable cuboid. Support, speaker, magnetics and assembly transforms remain unresolved. Its scalar `power_film_cap_max_height: 41` does not cover the CRC candidate's 51 mm body; candidate-specific envelopes must be used.
- [Assembly review](../../engineering/component-selection/power-film/assembly-review.md) supplies support/service constraints. All four references C12/C13/C25/C26 remain separate circuit interfaces in the power block.

## Four-body bounds

All dimensions are millimetres. L, W, H are maximum body dimensions; g is the edge-to-edge gap between adjacent bodies. A zero-gap entry is a mathematical packing lower bound using maximum bodies, **not an assembly recommendation**. The g = 10 column preserves Panasonic's recorded neighbor recommendation and is only a comparison assumption for CRC; this research adopts no clearance. Bodies are all seated in their normal pin-to-board relationship, then the entire board may be rotated. Permissible mounting orientation and retention still require qualification.

| Candidate / arrangement | Formula A × B × H | g = 0, maximum bodies only | g = 10, conditional body array |
|---|---|---|---|
| Panasonic 2 × 2 | (2L+g) × (2W+g) × H | 116 × 52 × 41 | 126 × 62 × 41 |
| Panasonic 1 × 4, repeated across short body axis | (4W+3g) × L × H | 104 × 58 × 41 | 134 × 58 × 41 |
| Panasonic 1 × 4, repeated across long body axis | (4L+3g) × W × H | 232 × 26 × 41 | 262 × 26 × 41 |
| CRC 2 × 2 | (2L+g) × (2W+g) × H | 117 × 72 × 51 | 127 × 82 × 51 |
| CRC 1 × 4, repeated across short body axis | (4W+3g) × L × H | 144 × 58.5 × 51 | 174 × 58.5 × 51 |
| CRC 1 × 4, repeated across long body axis | (4L+3g) × W × H | 234 × 36 × 51 | 264 × 36 × 51 |

A planar 90° rotation swaps A and B without changing area. For a horizontal PCB, conditional array-plus-nominal-PCB extents are `(A, B, H+1.6)` in width/depth/height. For the same board stood vertically in the width/height plane they become `(A, H+1.6, B)`. Other cabinet-axis rotations are permutations, not new volume savings. Neither expression includes solder tails beneath the board, body seating tolerance, board margins, brackets, mounting holes, fasteners, insulation, connectors, wiring or extraction envelopes.

| Candidate / g = 10 array | Horizontal W × D × H, with nominal PCB thickness only | Vertical W × D × H, same limitation | Depth change on standing board vertically |
|---|---|---|---|
| Panasonic 2 × 2 | 126 × 62 × 42.6 | 126 × 42.6 × 62 | saves 19.4; height grows 19.4 |
| Panasonic short-axis row | 134 × 58 × 42.6 | 134 × 42.6 × 58 | saves 15.4; height grows 15.4 |
| Panasonic long-axis row | 262 × 26 × 42.6 | 262 × 42.6 × 26 | consumes 16.6 more depth |
| CRC 2 × 2 | 127 × 82 × 52.6 | 127 × 52.6 × 82 | saves 29.4; height grows 29.4 |
| CRC short-axis row | 174 × 58.5 × 52.6 | 174 × 52.6 × 58.5 | saves 5.9; height grows 5.9 |
| CRC long-axis row | 264 × 36 × 52.6 | 264 × 52.6 × 36 | consumes 16.6 more depth |

The Panasonic short-axis row trades just 8 mm more width for 4 mm less depth than its 2 × 2 array. CRC's equivalent trade is 47 mm more width for 23.5 mm less depth. Panasonic's 2 × 2 array is 1 mm narrower, 20 mm shallower and 10 mm lower than CRC at the same illustrative gap. These gains are usable comparison metrics but do not establish electrical interchangeability or available cabinet space. In particular, the Panasonic vertical 2 × 2's 19.4 mm depth saving is local and cannot be credited as fixing the existing 20 mm carrier overrun.

A horizontal upper tier needs lower-component height + unresolved separation + upper PCB thickness + body height + unresolved seating/support allowances, measured from the lower mounting reference. Its 42.6/52.6 mm PCB-plus-body term is not the total tier height. Minimum exposed leads leave only 0.4 mm (Panasonic) or 1.4 mm (CRC) beneath a seated nominal 1.6 mm board, before required solder protrusion or thickness tolerance. Leads alone cannot provide a useful raised platform.

## Whole-assembly deficits remain

Recomputed directly from current outline dimensions and the register's **unqualified diagnostic** assumptions: 10 mm construction edge allowance each side, 15 mm side-flange budget each side and 8 mm between boards. These values are not adopted clearances.

| Diagnostic tier | Width calculation | Depth calculation | Difference against provisional 467 × 160 comparison frame |
|---|---|---|---|
| Main + Reverb | 290 + 160 + 8 + 2×10 + 2×15 = 508 | max(140,100) + 2×10 = 160 | width +41; depth 0 |
| Rotated Power + Control | 175 + 230 + 8 + 2×10 + 2×15 = 463 | max(160,110) + 2×10 = 180 | width −4; depth +20 |
| Main + rotated Reverb, alternative screen only | 290 + 100 + 8 + 2×10 + 2×15 = 448 | max(140,160) + 2×10 = 180 | width −19; depth +20 |

A negative difference is merely arithmetic residual against that comparison frame; it is not usable clearance. Rotating Reverb removes the specific width overrun but transfers the problem to depth. Moving capacitors off Power cannot fix Main/Reverb's current carrier width. Removing their bodies also does not automatically shrink Power's outline: other components, routing, nodes, mounts and supports must be repacked. With the existing diagnostic allowances, a horizontal tier would need board depth at most 140 mm to stay within the provisional 160 mm frame. That is a study target, not an approved board size.

## Most useful next model/action

Make one common parametric **populated cassette comparison** with baseline A first: a revised power area, comparing Panasonic 2 × 2 against its short-axis row and retaining CRC as a distinct electrical/package alternative. Carry current Main/Reverb/Control geometry and the 41/20 mm residual deficits visibly; do not present a detached attractive bank as the solution. Then compare B, a supported upper bank, and C, a supported vertical bank, in exactly the same frame with uncertainty fields explicit. For C, start with the 2 × 2 footprint because it gives the largest depth trade among compact-width arrangements; retain the short-axis row where lower vertical height is useful.

Before ranking final feasibility, register actual speaker basket/magnet, magnetics, controls, tube/socket and extraction envelopes, fixed supports, rear-cover sweep and cassette withdrawal path. Unknown regions are unresolved constraints rather than free space. Add actual body retention and carrier load paths, rated connector/terminal/underside and insulating hardware envelopes, lower-component thermal exclusion regions and full fastener-tool sweeps. Board standoffs support the board but do not by themselves qualify capacitor body retention. No electronics or support attaches to the removable rear wood. Finish with a dimensioned inert mock-up/service sequence; independent rear-cover removal and ordinary fastening access remain mandatory.

Verification: recomputed all array and tier formulas with Python Decimal directly from the dimensional inputs; matched existing 2 × 2 assembly receipt and 508 × 160 / 463 × 180 trial tiers. No existing geometry generator was used as the arithmetic oracle. No CAD or physical fit verification was performed.

Input SHA256 at review:

- Panasonic contract: `3ad199dbf07e064e15fc1d6bd563dacceac29db81b1557b6a58259475d9a11d3`
- CRC contract: `9deb91c6a0c0414d55d575e80079be6a21a20c2ce978d9af3ec1b971b7e6dfe7`
- Mechanical inventory: `de305cd39ec3a182a12f0d9cc8eeffb5dedb17109ee89b1ec24618fffa9ca6ac`
- Fit register: `f2f5e3f44f3055c3ba301e5c4bb1c2b0a4c5ff76547c4787c590da546ae9dd12`
