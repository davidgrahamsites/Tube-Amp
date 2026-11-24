---
id: VAL-025
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Exact low-voltage capacitor packages and drill verification

Owner: Renegade integration. Authority: existing parts-first, PCB repair and socket requirements (FB-115/116). This checkpoint advances T08 prerequisites without closing T04 or any full through-chassis scope.

[Package review](../../engineering/component-selection/footprints/panasonic-fr/review.md) links the Panasonic manufacturer drawings, editable dimension contract, generated library, native checks and supplier refresh. C204, C207, C211, C212, C214, C616 and C617 now have matching exact-part footprint IDs in the circuit source, native schematics and Control/Reverb boards. Four incorrect native pitches are corrected; the other three positions now carry maximum-envelope and explicit hole allowances. No values or topology changed.

Three packages pass 18 native geometry checks. All 28 integration preservation checks pass, including complete native named-net/pin comparison, unchanged non-target footprints, outlines, rules and project settings. The seven components retain their positions and polarity. An initial 0.1229 mm clearance error at C212 was corrected by adjusting six existing NEG_RAW track segments while retaining their identities, layer, net and 0.4 mm width; all six are H/V/45-degree. Native strict DRC is back to baseline: Main/Power/Control/Reverb have 105/39/90/0 unconnected items and 43/12/13/0 missing wire courtyards. Existing ERC GND/PE warning remains.

Native Excellon checks independently match all 14 selected round plated holes to the current board coordinates and 0.85/0.95 mm diameters. Fabricator finished-hole and registration tolerances remain assumptions pending confirmation. These exports are diagnostic, not a production package. Other components' holes/slots are not qualified by this result.

Control/Reverb native PDF plots were visually inspected; the seven polarity marks and C212 escape are clear. Hidden schematic footprint-only changes preserve the drawing exactly; broader readability and bypass-loop placement remain open. Historical value-only C212 evidence is retained, with this explicit revision bridge. The socket inventory was refreshed against the current source hash: all ten ICs and six tubes are required to be socketed, but the actual socket assemblies are still unqualified.

No new electrical simulation was needed or claimed for package-only changes; continued regulator and transformer/RETURN simulations remain separate work. C407950 stock was visible at 535 / MOQ 5 / ¥1.1676 on November24. The other two capacitor sizes retain November11 stock observations because the attempted refresh failed; Shanghai delivery is supported in principle by the saved domestic policy, not an exact quote or order.

ICM separates the editable package contract, footprint factory, PCB integration mutations, manufacturer excerpt and generated test/CAM evidence. Next: exact sockets/contact/heatsink envelopes, actual local bypass-loop placement, high-voltage capacitor and transformer constraints, and populated three-board repacking. Actual drill-tool dimensions remain deferred to November25. No manufacturing release.
