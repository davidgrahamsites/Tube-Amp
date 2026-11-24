# Native schematic identity repair — 24 November 2026

Owner: PCB integration. Task T02 in the [remaining-work queue](../../../../plans/renegade-working-prototype/tasks.md), following FB-103. Scope is identity metadata, not circuit or layout changes. **Fabrication remains on hold.**

Fresh KiCad 10.0.6 XML was exported from the current 18-sheet native schematic. Root UUID was read from that schematic, rather than assuming a historical root. Each circuit footprint was matched by reference and its existing pad/net contract checked before replacing or adding its native symbol instance path. The guarded factory is `../tools/reconcile_symbol_paths.py`; default mode checks without writing, `--apply` writes only after validating all four candidates. Source and output hashes plus exact path changes are in [the receipt](symbol-path-reconciliation.json).

| Board | Links repaired | Remaining path errors | Pad-contract errors |
|---|---:|---:|---:|
| Main | 56 | 0 | 0 |
| Power | 27 | 0 | 0 |
| Control | 53 | 0 | 0 |
| Reverb | 46 | 0 | 0 |

All four candidate boards loaded through KiCad's native parser before adoption. After adoption, a read-only rerun proposed zero changes, and the existing independent hole/pad audit reported zero path or pad-contract errors. Removing only `(path ...)` metadata lines leaves byte-identical files relative to the prior committed boards. Thus copper, footprints, pad shapes, holes, positions, nets, graphics and board settings were not changed. Project/rule files were not edited. A full DRC or image rerender was not repeated for this metadata-only change; the previous geometry's 234 unconnected and 68 missing-courtyard findings remain open, with the before/after hash chain preserved here.

The first check-only attempt correctly stopped at R618, which had no path field. The factory was corrected to handle an absent field only when the native parser also reports an empty path. It then checked all candidates successfully before any board mutation. Native Python emits wx/image-handler debug warnings in this environment; accepted runs returned zero and passed explicit native reload assertions.

This repair does not establish automatic whole-project schematic-to-PCB update safety. Generic wire ports and mechanical items without circuit symbols were preserved. Native local net labels differ from the contract, and native GND/PE endpoint groups still differ. T03 owns the explicit bond contract; T13 must test a board-scoped update on copies after interface and part choices are complete. Do not push the complete amplifier netlist into every physical board or remove protective earth to clear a warning.

T02 done condition is satisfied. The remaining electrical, packaging, drill-fit, tool-access and physical acceptance gates remain in the ordered queue.
