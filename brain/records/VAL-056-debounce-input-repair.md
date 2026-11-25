---
id: VAL-056
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Native debounce capacitor input-current limits

[Owned review](../../engineering/whole-amp/control-switching/debounce-input-review.md) records native R304/R314 10 kΩ between C301/C311 and U1 inputs. The source circuit, readable native sheet and Control board change together; no blocks, sockets or mounting holes move. Exact Yageo RT0603BRD0710KL has a Chinese LCSC route and dated positive stock; Shanghai checkout is not verified.

Native XML changes are exactly the two series insertions. Twenty other native files and all prior Control geometry/copper are preserved except two pad net names. ERC remains one existing finding, Control DRC13 with79 opens. 1,536 passive timing cases and eight ngspice witnesses pass; maximum added timing change0.5953 ms. Input-current bound is0.536 mA each under the stated5.25 V assumption. The final changed sheet and crops were visually checked.

This supersedes VAL-055's direct-capacitor native finding only; its historical candidate/hash evidence is not rewritten. Combined phantom-power bound is1.576 V, so complete power sequencing remains unqualified. Existing capacitor schematic/source/board footprint mismatch is now explicitly queued for reconciliation. Next: exact capacitor synchronization, full power sequencing and remaining native integration/routing, then populated three-board fit. All six scopes remain incomplete; no fabrication release.
