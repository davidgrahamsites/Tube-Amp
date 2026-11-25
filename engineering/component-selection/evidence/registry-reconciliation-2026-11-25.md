# Missing selected-part identities — 25 November 2026

Selected-BOM generation failed because P074 and P129 already selected parts
absent from candidate-register.json. This repairs those records without
changing their engineering selection or importing unrelated working edits.

- **AOS AO3400A**, Q1/Q2, P074: [domestic LCSC C20917](https://item.szlcsc.com/21629.html)
  was reopened and confirms AOS, exact MPN and SOT-23. Current domestic RMB
  quote, minimum quantity and stock were not exposed; these remain unknown.
  [Existing electrical evidence](electric-lv-parts-2026-11-21.md) and the
  control-switching module own qualification. ICKey results with the same MPN
  identified HUASHUO, OM SENI or ChipNobo: they are not the selected AOS part.
- **UNI-ROYAL MFR0W4F8200A50**, R215, P129:
  [global LCSC C58624 identity](https://www.lcsc.com/pl/product-detail/C58624.html?is_substitute=1&original_product_code=C27412564&original_unit_price=0.0054)
  and [the existing preload review](../../whole-amp/aux-supply/preload-review.md)
  establish the selected identity and manufacturer old/new numbering evidence.
  They do not establish a current mainland offer. New code MF0W4FF8200A50 is
  not silently substituted. Domestic price, MOQ, stock and exact Shanghai
  delivery remain open.

Both candidate rows carry null RMB price and MOQ. The generator lists them as
unpriced and excludes them from its partial total. This is a repaired data
relationship, not a procurement pass. No contact, order or checkout occurred.
