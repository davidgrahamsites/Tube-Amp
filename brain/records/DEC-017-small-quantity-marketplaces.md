---
id: DEC-017
type: decision
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Small-quantity marketplace sources

FB-126 explicitly includes Taobao and Pinduoduo as potential sources when another supplier requires too many pieces. Do not discard an electrically suitable exact part solely because one listing has an excessive MOQ. Compare total delivered prototype cost, not only unit price.

Owner: component selection. Retain seller and exact SKU/variant, manufacturer, full suffix, package, dated available quantity and MOQ, condition/newness evidence, datasheet match, and Shanghai delivery basis. A generic marking or family-name title is not evidence of the exact manufacturer used in simulation. A different manufacturer's part reopens the affected device, pin/footprint and circuit checks. The economical/reliable policy and all socket/fit requirements remain in effect. No order, seller message or fabrication upload is authorized by this sourcing clarification.

Current application: Chinese LCSC BC857B-7-F listing reports 9000 stock but MOQ3000; this route is unsuitable for the prototype, not a rejection of the transistor itself. Initial public indexed searches did not establish an exact Taobao/Pinduoduo seller listing. The alternative Diodes MMBT3906-7-F listing reports608stock/MOQ1; its own primary model is now under evaluation. Neither item is purchase-released. Evidence is in engineering/whole-amp/expression-control/results/*source-observation.json.

Human check: before ordering, compare the chosen seller variant and device/package to the approved BOM and verify actual shipping to the user's Shanghai address.
