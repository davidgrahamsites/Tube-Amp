# Current PCB geometry and FreeCAD fit diagnostic

Owner: integration. Date:2026-11-24. Authority:FB-112. **Not a manufacturing release or populated chassis.**

The editable [FreeCAD model](board-fit-diagnostic.FCStd), [STEP board solids](board-fit-diagnostic.step) and [dimensioned comparison](board-fit-diagnostic.pdf) now contain the actual four native board outlines and their16 mounting holes. Each current mounting hole is round, nominal3.2mm NPTH. This verifies file geometry, not a selected fastener fit, hole tolerance, washer clearance or drill approach. Non-round component lead holes are outside this mounting-hole adapter's scope; it refuses unsupported mounting-hole shapes rather than converting them silently.

The read-only PCB adapter owns `../../pcb-measured-r/review/mechanical-inventory.json`. It verifies rectangular native outlines, records original board coordinates/hashes, exact thickness and holes. FreeCAD owns the explicit comparison placements only. The register's `pcb_envelope_study` is the editable source for trial construction allowance10mm, side flange budget15mm, board gap8mm, upper plane70mm below the assumed top and60mm tier separation. **These are unqualified trial inputs**, not electrical clearances or drill/thermal results. The cabinet467×160×383mm datum box combines user readings with an uncertain depth/common-frame interpretation; it is not measured empty usable volume.

| Existing board tier | Required support budget | Difference from assumed cabinet width/depth |
|---|---|---|
| Main290×140 plus Reverb160×100 |508×160mm |41mm too wide |
| Power rotated175×160 plus Control230×110 |463×180mm |20mm too deep |

Thus the earlier board-only packing sketch does not leave these proposed flanges/construction allowances. Keeping all boards on these two horizontal planes is not a fit solution. For this particular allowance budget, combined Main+Reverb board widths would need at least41mm reduction, or Reverb must move to another orientation/plane. The Power depth must reduce at least20mm, or that board must be reoriented onto another mounting plane. These are necessary envelope constraints, **not evidence the parts can be repacked into those outlines**. Preserve all functional blocks and proceed toward the user's three-board preference; current four native boards were not consolidated or rerouted here.

The inventory finds196 footprints without assigned3D models. Populated part heights, speaker basket/magnet, six sockets/tube-removal paths, PT/OT/choke, plugged connectors/cables and heat keepouts are omitted and remain visible exclusions. No load-bearing chassis metal, final screw location, support attachment or withdrawal path is invented. Fixed cabinet supports must carry the eventual removable chassis; removable upper rear wood must stay independent.

The FreeCAD receipt verifies valid solids, analytical drilled volumes, editable native dimensions on reopen, four STEP solids, volume preservation, all exported positions and90° Power rotation. Coordinate convention: assumed inside front-left floor origin; X right,Y rear,Z up. Geometry/plot was visually inspected. View the objects as a fit diagnostic; the export includes PCB solids only, not the unqualified datum box or fabrication metalwork.

Drill clearance remains **pending until the user provides tool dimensions on/after November25**.15mm flange budget is not an access approval. The speaker reference's283mm cutout still fails the receivedapproximately270mm aperture. Actual speaker, magnetics, sockets, connector bodies and cable bends must enter the common assembly before fabrication drawings or populated fit claims. Prior234 unconnected PCB items and68 provisional courtyards remain unresolved; the read-only adapter preserved all board hashes.

Factory: `../tools/board_fit_cad.py`, run in verified FreeCAD1.1.4 console with minimal environment, UTF-8 and isolated settings. `../tools/plot_board_fit.py` plots its receipt; it is not a second dimensional edit surface. Native/source hashes accompany results; the register hash covers exactly the datum and study fields consumed so unrelated panel work does not change this receipt. Current-only CAD export filenames and disabled document backups avoid accumulating full copies.
