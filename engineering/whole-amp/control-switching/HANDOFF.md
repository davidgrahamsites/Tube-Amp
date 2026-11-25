# Current control handoff — November24, VAL-032

Socket corrections from VAL-030 are now integrated and rechecked through the VAL-031/032 exact Reverb routing deltas. Five DIP footprints have1.0mm holes and larger socket courtyards; the old footprint action below is historical. Native U3 is still TPS3808G50. Read divider-review.md for the better-stability candidate comparison: shorter endurance passes, extended screens and exact China pair availability remain unresolved. No divider/supervisor replacement is adopted. Brownout timing, actual rail collapse, recovery-clock coincidence and removable carrier qualification remain next.

The user supplied46mm chuck diameter (FB-120). Full motor body/bit length and actual screw access remain pending. Three-board populated fit is not cleared. Keep sockets and functional blocks intact.

## Historical reset-edge checkpoint

# Control switching handoff — November 24, reset-edge checkpoint

VAL-029 / edge-review.md is current. U1C/D are now wired and routed as a two-gate reset conditioner inside the existing control block. Six pin changes, 27 tracks, one 0.4 mm via; all old copper, component geometry and mounting holes preserved. Native connectivity, layer-aware routing, exact drill delta and negative controls pass. No new ERC/DRC finding: existing ERC1, Control DRC13, Control79 unconnected. Source hashes are in results/edge-native-checks.json. Native PDFs and visual receipt are current.

The prior VAL-028 driver adoption remains in force. Its 55 runs and historical native receipts describe that checkpoint; do not run its baseline-specific check_native.py against the later reset change. Use check_reset_edges.py for the current delta. edge-integration.json records only the initial intermediate change; edge-native-checks.json owns final source hashes. Guarded mutation factories must not be rerun on adopted files.

The TPS3890 nominal model does not discharge CT on manual reset; this explains its timing discrepancy but is not proof of a hardware defect. G50 release threshold still lacks low-rail margin. Conditioned edges have a datasheet bound under stated 4.5 V/50 pF/-40..85 C conditions, not full startup/brownout qualification. Next: supervisor threshold/carrier and actual rail collapse, recovery-clock coincidence and socket/trace capacitance.

TE DIP sockets are preferred candidates with domestic loose-stock observations; all sockets remain required and no exception is adopted. Five native DIP footprints need 1.0 mm holes and larger courtyards after exact socket qualification. Read component-selection/socketing/te-candidate-review.md and mechanical/review/socket-fit-checks.json. The three-board populated chassis remains open; rear wood independent, actual drill envelope deferred November 25. No fabrication release.
