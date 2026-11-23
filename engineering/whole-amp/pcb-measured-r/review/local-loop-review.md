# Local bypass and relay adoption review

Owner: PCB integration. Scope: candidate C in `/tmp/renegade-local-loops-c`,
220 V electric build, four existing functional blocks. This is a bounded repair
review. It is **not a fabrication release**. Main, Control and Reverb candidates were adopted on 23 November 2026 after hash checks; Power is unchanged.

## Result

The bypass-capacitor and relay-loop repairs are adopted as an intermediate engineering checkpoint. The complete boards are not ready
to manufacture. `local-loop-adoption-guard.json` records before/candidate/adopted hashes. Fresh active strict DRC is in `requirements-run.json`; its hashes match the adopted boards. A changed hash requires renewed review. Power is unchanged. Project settings and custom rules match the active
copies byte for byte. KiCad had expanded the candidate Reverb project; its
active project was restored and Reverb DRC was rerun with the same zero counts.

| Adopted board | Missing courtyards | Unconnected items | Other native DRC violations |
|---|---:|---:|---:|
| Main | 43 | 105 | 0 |
| Power | 12 | 39 | 0 |
| Control | 13 | 90 | 0 |
| Reverb | 0 | 0 | 0 |

Total: 68 missing courtyards and 234 unconnected items. This reduces the
previous active-board count of 243 unconnected items by nine; it does not
complete routing. Native KiCad 10.0.6 ran with severity-all, all-track-errors
and zone refill. The command receipts are in `local-loop-native-review.json`.
The macOS sandbox initially aborted native DRC during application registration;
the successful read-only runs used the same CLI outside that sandbox.

## What was inspected

All four SVG exports were rendered to PNG and visually inspected. Main retains
its preamp/power-amplifier block placement; D331 and D332 sit beside their
respective relay coils. Control has C351, C352 and C353 at the local IC supply
connections. Reverb has C605 beside U11 and D341 at K3. The repaired loops are
short and the reference markings remain legible. No new obvious body collision
was seen. Power is unchanged. Most Main/Power/Control routes remain incomplete.
This visual check does not prove noise performance, current capacity, thermal
performance, enclosure fit or screw-tool access.

Every candidate pad matches the current `reverb-600/circuit.json` pad contract.
The fresh native schematic export includes the corrected D332 orientation:
pin 1 is +12V and pin 2 is COIL_CH. D331/Main, D332/Main and D341/Reverb
placement metadata were corrected separately by the schematic owner.
New diode symbol paths were repaired in the candidates before adoption; the exact
before/after hashes and paths are retained in the adoption guard.

Native endpoint comparison still finds the schematic combining the contract's
GND and PE groups. The PE endpoints are J7.3, JPE1.1 and JPE2.1. This needs an
explicit protective-earth/signal-ground bond contract. Do not remove protective
earth to make the check pass. Other native net-name differences are local
auto-generated labels; endpoint groups, rather than label spelling, were compared.

Existing symbol paths also need reconciliation before an automatic schematic-to-
PCB update: candidate Main 56, Power 27, Control 53 and Reverb 46 paths differ
from the current complete native paths. Some omit the root UUID and some retain
older symbol IDs. These were not silently replaced in this bounded repair.

## Hole and slot inventory

`local-loop-hole-audit.csv` lists every drilled footprint pad and via, with
board, reference, pad number, MPN where available, exact nominal drill X/Y,
shape, plating, pad geometry, offset, position, nominal axis edge margin and
source/evidence gap. The JSON contains source hashes and pad/net checks.

| Adopted board | Drilled footprint pads | Vias |
|---|---:|---:|
| Main | 175 | 3 |
| Power | 79 | 0 |
| Control | 145 | 3 |
| Reverb | 125 | 12 |

The active and candidate inventories contain 1,084 drilled features in total.
All are round; there are no oval slots. This is a CAD observation, not proof
that every selected component fits. A rectangular or oval lead can use a round
hole only when its maximum cross-section fits with insertion allowance and
finished-hole tolerance. A rectangular lead requires its corner-to-corner
diagonal to fit. If a plated slot is required, its width, length, plating,
annular copper and fabrication support must be specified from the actual part.

K1/K2/K3 candidate relay drills are 1.0 mm with 1.8 mm pads: a nominal 0.4 mm
radial annulus. The inventory's axis edge margins are geometric screens only;
they do not include drill wander, plating, etch or fabrication tolerances.
The 3.2 mm non-plated mounting holes also require the actual fastener/washer
and tool-access checks.

All 68 missing courtyards are generic wire-terminal footprints with no
qualified mating connector or cable termination envelope. Adding arbitrary
circles would conceal the outstanding interface design. Correction FB-089: the user requires PCB-side connectors and insulated field wiring; pot-side adapters are not required. Once exact headers, housings, contacts, wire gauges
and strain relief are selected, replace the provisional ports, add source-backed
courtyards and repeat routing/DRC/mechanical checks.

## Remaining release gates

Complete routing; resolve the earth-bond contract and native symbol linkage;
qualify every through-hole part against its maximum lead dimensions and the
fabricator's finished-hole tolerances; integrate the pot harness interfaces;
check assembled cabinet clearance and removable-back access. Actual drill-tool
dimensions remain a user input. No manufacturing package is authorized by this
review.

Scoped ICM checks for tools and review: clean. Both new audit factories parsed
without Python syntax errors. Active adoption is complete. Fresh strict DRC, hole/pad audit and all four rendered board views were checked after adoption. No fabrication release.
