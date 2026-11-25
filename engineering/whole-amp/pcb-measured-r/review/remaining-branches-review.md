# Remaining branch repairs — 24 November 2026

Four flagged junctions are repaired against baseline `9ce4c37`: Power B_RECT and Control NEG_RAW, CTRL_RAW and RESET_RAW_N. The exact editable delta is `../remaining-branches-contract.json`. Twelve existing segments were shortened and eight tangent circular arcs added. The Power branch retains 0.6 mm copper; Control retains each existing 0.3/0.4 mm branch width. No footprint, pad, hole, slot, net, board outline, project rule or other board atom changed. Main and Reverb are unchanged.

The independent verifier reconstructs the permitted native delta, calculates circles from three arc points, checks 45°/90° sweep angles and tangency to same-net/layer straight segments, and compares native drill exports. Narrowed-arc, wrong-net, non-tangent and missing-branch negative controls are rejected. Full candidate validation passed before adoption and was repeated on the active boards afterward.

Native DRC findings are unchanged: Power has 12 existing violations and 39 unconnected items; Control has 13 existing violations and 79 unconnected items. The verifier compares the complete violation lists and open counts by net, not just totals. These incomplete boards do not pass a manufacturing release. No rule was disabled to obtain the comparison.

Native PDF plots were inspected at board scale and enlarged junction scale. RESET_RAW_N now blends the horizontal/vertical branches into its diagonal stem. The rail junctions and B_RECT branch show continuous rounded transitions without displaced pads. See `remaining-branches-control.pdf` and `remaining-branches-power.pdf`. These are copper review plots, not assembly/fabrication drawings.

The refreshed copper inventory reports zero right-angle branch candidates outside pads/vias on all four boards. This is an exact-endpoint screen, not a complete review of pad escapes, interior intersections, zones or every existing arc. The eight added arcs have the dedicated geometric checks above. Full corner and current-capacity qualification remains open.

The socket checker now validates the complete Control routing delta before comparing its older socket correction. All 52 socket hole changes, native netlist/ERC comparisons and existing drill/DRC checks still pass. The panel connector audit is refreshed for the new board hashes; its unresolved two pot-to-pot board nodes and connector adoption holds remain. No circuit values or functional-block allocation changed.

Mechanical inventory is refreshed; exact native preservation proves board outlines, mounts and component positions unchanged. The existing four-board diagnostic remains an intermediate study: populated three-board placement, transformer/speaker fit, independent rear removal and full drill body/bit access are still not cleared. The 46 mm chuck measurement is retained. No procurement choice or new part was introduced by these repairs.

Next: continue exact connector interfaces and three-board placement, using the cable-loading evidence for high-impedance runs; derive current/insulation rules and complete routing. All six overall scopes remain active. No fabrication release.
