# U12 routing repair — 24 November 2026

Owner: PCB integration. FB-119. Baseline f8b7236. u12-routing-contract.json declares the exact editable delta. repair_u12_candidate.py creates a fresh candidate; check_u12_routing.py independently verifies it and the adopted board.

Replaced the OUT_BUF square T beside U12 with two tangent quarter-circle arcs of 1 mm radius. Enlarged eight nearby 0.2 mm chamfers to 0.8 mm setbacks. Changed 23 existing segments and added two arcs, retaining 0.3 mm widths, all pads/footprints/nets, holes, slots and other board atoms. Other boards are unchanged.

Fresh native Reverb DRC: zero violations, zero unconnected items. Exported drill hits match the baseline. Exact-delta comparison and independently calculated arc circles/tangents pass; deliberately narrowed-arc and missing-branch controls fail. Native PDF was inspected at full-board and enlarged U12/C615/R616 scales: the rounded fork and larger diagonal corners are visible without altered pad placement. Current plot: u12-routing.pdf.

The socket verifier now checks the complete follow-up routing delta against its exact baseline before comparing the earlier socket-only change. Fresh socket/native-netlist/ERC/drill checks still pass with no new violations. Historical socket PDFs depict the preceding socket checkpoint; use u12-routing.pdf for current Reverb copper.

This is not an all-corners pass. audit_copper.py now reports pairwise branch angles separately from simple bends and keeps all_corner_review_complete false. Eleven remaining right-angle branch candidates outside pads/vias need review: Power 1, Control 3, Reverb 7. Arc items are explicitly outside the general bend screen; the two new arcs are covered by the dedicated tangent checker.

Current capacity is also not qualified. The audit now includes all pad-connected nets, including wholly unrouted ones: Main 52/8, Power 20/8, Control 32/19, Reverb 30/30 total/with copper. The 134 board/net entries have independently checked native pad coverage. Track lengths are summed inventory lengths, not source-to-load path resistances. Current budgets, final copper thickness, path/return sharing, thermal rise, voltage drop, vias, necks and protection remain required before width approval. Do not infer ampacity from zero DRC or a common default width.

The native board geometry/holes used for fit are preserved. Mechanical receipts are refreshed for current source hashes; their failed support-plane and unqualified drill/assembly status is unchanged. No fabrication release.
