---
id: VAL-024
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Socket coverage and negative-regulator bypass correction

Owner: Renegade integration. Authority: FB-114–116 and standing repair authorization. [Through-chassis scope](../../plans/renegade-working-prototype/through-chassis.md) retains all six requested scopes.

[Socket review](../../engineering/component-selection/socketing/review.md) inventories ten ICs/six tubes, including regulators and supervisor. Six inventory checks and three negative controls pass; all actual socket assemblies remain pending. Live domestic listings and the CONNFLY drawing are retained with missing ratings explicit. ST maximum rectangular TO-220 lead dimensions also expose U7's provisional1.1mm direct-lead drill limitation; socket terminals require their own final hole specification.

[Supply correction](../../engineering/whole-amp/aux-supply/review.md): C2122.2µF aluminium was inconsistent with ST's minimum ten-times-2.2µF guidance. Adopted47µF/50V EEUFR1H470 in P127 and source/native values. Current LCSC stock535/MOQ5/¥1.1676 observed. Native value-only reverse delta, full net/component comparison and CLI checks pass11 checks. Existing ERC warning and13 Control courtyard findings remain;90 unconnected items remain. Two airwire endpoint choices differ but copper/geometry/net bytes are preserved.

Six output experiment decks remain identical because they exclude the supply sheet. No new regulator transient, socket thermal test or hardware measurement is claimed. Source-hash historical audits must be interpreted at their recorded revision; this checkpoint is the explicit electrical-difference bridge.

Human visual check covered the changed full supply sheet and enlarged C212 region: value/polarity readable, no new overlap. Existing long local routes and U7 text crowding remain a schematic-readability task, not an accepted final drawing.

Next: correct C212 exact footprint/local placement, qualify sockets/heatsinks and remaining bypass/protection, then propagate actual parts into the three-board assembly. Actual drill dimensions remain deferred until November25. No fabrication release.
