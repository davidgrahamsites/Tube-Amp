---
id: VAL-057
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Adopted film-capacitor identity parity

[Owned review](../../engineering/component-selection/film-parity/review.md) closes VAL-056's film identity mismatch for 15 references: KNSCHA MEB104J63V82CB0236 and MEB105J63V82CB0235 now agree across circuit source, hidden schematic metadata and existing boards. Values, pins, blocks, drill geometry and all four boards are unchanged. Complete 144-net equivalence, 236-component metadata comparison, unchanged ERC and pixel equality of all18 PDF pages pass.

A dated ICkey mainland listing matches the 100 nF part and lists stock1556/MOQ10. The 1 µF listing has a package contradiction and remains unqualified; fresh direct LCSC stock retrieval failed HTTP405. Shanghai checkout, supplier identity at shipment and finished-hole tolerance remain unverified. No purchases or supplier communications.

C351–C353 already use Yageo ceramic bypass capacitors in native source and 0805 boards; committed P076 coverage is stale and the working correction points to a missing evidence file. That documentary repair is next, without substituting the physical part. Power sequencing/native integration, routing, socket/carrier qualification, three-board populated cabinet and actual drill access remain open. All six scopes incomplete; no build/fabrication release.
