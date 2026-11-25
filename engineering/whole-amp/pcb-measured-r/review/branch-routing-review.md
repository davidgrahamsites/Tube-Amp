# Seven reverb T-junction repairs

Owner: PCB integration. November 24, 2026. Baseline 738fd04.

`branch-routing-contract.json` declares the seven orthogonal T nodes on DRIVER,
REC_IN, +15V and GND. Each becomes two tangent quarter-circle branches of radius
0.8 mm. Twenty-one straight segments are shortened and fourteen arcs added;
their existing 0.3 mm widths are preserved. These local repairs do not change
functional blocks, footprint/pad geometry, net assignments or mounting/drill data.

`tools/repair_branch_candidate.py` creates a new temporary candidate from a hashed
baseline. `tools/check_branch_routing.py` independently solves arc centers,
checks tangency to the retained segments, exact native delta, unchanged exported
drills and native DRC. Narrowed-width, wrong-net, displaced-midpoint and missing-arc
negative controls are rejected. All nondeclared native atoms are identical.

The candidate passed and was adopted; the active board was checked again. KiCad
10.0.6 reports zero Reverb DRC violations and zero unconnected items. The native
[combined-layer plot](branch-routing.pdf) was visually inspected: the seven forks
are continuous rounded junctions, the U12 repair is preserved, and no component
or mounting position moved. This is a copper review, not manufacturing artwork.

The socket checker now validates this exact follow-up before projecting back to
the U12 and socket baselines. It contains no blanket allowance for later copper
changes. Current socket checks pass; Control retains 13 existing DRC findings and
79 unconnected items. The independent 134-entry copper coverage audit now reports
four outside-pad/via branch candidates: Power B_RECT and Control NEG_RAW, CTRL_RAW
and RESET_RAW_N. The general audit does not screen arc curvature; the dedicated
U12/branch checks cover the sixteen present Reverb arcs.

Remaining work: inspect those four branch candidates individually, review tiny
chamfers and pad/via approaches, establish path currents including fault and pulse
conditions, then size copper/vias/thermal connections against the agreed stackup.
Preserving width does not qualify ampacity. No all-board routing or EMI approval.

Mechanical inventories and FreeCAD diagnostic receipts were refreshed to this
board hash. Geometry is unchanged; the existing support-plane trial still fails
and the populated three-board chassis is not released. The 46 mm chuck measurement
is retained; complete drill access awaits body and bit dimensions.
