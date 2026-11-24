# Exact Panasonic FR-A package correction — November24

Seven selected capacitor positions now use three part-specific native footprints. This is a scoped package correction, not a manufacturing release. The electrical values and named-net/pin connectivity are unchanged from3efa8d9.

| MPN / references | Nominal pitch | Maximum body D×H | Maximum round lead | Specified finished PTH / assumed tolerance |
|---|---:|---:|---:|---:|
| EEUFR1H470 / C207,C212,C616,C617 |2.5mm|6.8×12.7mm|0.55mm|0.85±0.10mm|
| EEUFR1H101 / C204 |3.5mm|8.5×13.0mm|0.65mm|0.95±0.10mm|
| EEUFR1H100 / C211,C214 |2.0mm|5.5×12.5mm|0.55mm|0.85±0.10mm|

Manufacturer evidence: [Panasonic September2025 catalogue](https://industrial.panasonic.com/cdbs/www-data/pdf/RDF0000/ast-ind-152838.pdf), PDF pages14/19, printed12/17. The two-page [excerpt](evidence/manufacturer-excerpt.pdf) was visually inspected, including the outline tolerances and exact50V rows. The editable package contract distinguishes manufacturer dimensions from our fabrication/assembly assumptions. These are unsuffixed long-lead parts; B/H formed-tape suffixes can change pitch and are not interchangeable without review.

All three designs retain0.20mm minimum diametral insertion clearance under the stated hole tolerance. This allowance is for lead diameter, not the separate±0.5mm lead-spacing tolerance: flexible leads must be formed to the board pitch without stressing the seal. Fabricator hole/registration tolerances and received parts still need confirmation. Courtyards include maximum diameter plus0.5mm radial margin (0.25mm possible center displacement and0.25mm assembly clearance). Listed height excludes standoff, vent and service space.

## Native integration and checks

Authoritative source, two native sheets and Control/Reverb boards use identical footprint IDs. Reference positions, values, orientation, symbol paths and pad polarity are preserved. Every unaffected footprint and all board data outside the seven footprints and six identified C212 track endpoints match the baseline semantically. KiCad's unrelated default-thickness/path-order serialization was removed by restoring those unaffected footprint blocks verbatim.

The first DRC detected0.1229mm clearance between C212 positive square pad and its NEG_RAW track against the0.25mm rule. Six existing NEG_RAW segments were adjusted at unchanged0.4mm width/layer/net, using H/V/45-degree lines. Fresh strict checks restore the baseline: Reverb0violations/0unconnected; Control13missing courtyards/90unconnected; Main43/105; Power12/39. Total234unconnected and68missing wire courtyards remain. ERC retains the existing GND/PE alias warning. See results/integration-checks.json and native reports. Neither that warning nor the routing backlog is waived. The14 selected round plated-hole hits were also matched against native Excellon tool sizes/coordinates/plating in results/drill-checks.json; diagnostic drill exports are not a fabrication release.

Native Control/Reverb PDF plots were visually reviewed. All seven capacitor outlines/polarity marks are visible, the C212 escape is clear, and no new courtyard overlap was reported. The broader long bypass loops, missing sockets and unfinished layout remain visible; this review does not approve them. Schematic changes affect hidden footprint properties only; preservation checks prove no drawing/value/wire change, so this checkpoint does not claim a new whole-schematic humanization pass.

The existing C212 value correction still applies (47µF aluminium, minimum37.6µF at−20%); its old3.5mm native pitch hold is now resolved. Local placement and complete regulator stability/startup/load/heat qualification remain open. The earlier aux-supply checker is a historical value-only receipt; this integration receipt is the explicit bridge to the current package revision. No electrical simulation was repeated for a footprint-only change.

## Sourcing and next actions

C407950/EEUFR1H470 was visible on the domestic LCSC page at535stock,MOQ5,¥1.1676 each onNovember24. The100µF and10µF exact MPNs retain their November11 observations; attempts to refresh their LCSC search pages onNovember24 timed out and must not be reported as fresh stock. See results/supplier-refresh.json. Domestic delivery policy supports a Shanghai route in principle; an exact shipment/price/order has not been confirmed. No purchase or supplier contact occurred.

Next: qualify exact socket/contact geometry and regulator heat/service access; relocate actual bypass loops around those envelopes; resolve high-voltage capacitor/tube/transformer envelopes; then consolidate and route the populated three-board chassis. Preserve the independent removable back and defer the real drill-envelope check untilNovember25.
