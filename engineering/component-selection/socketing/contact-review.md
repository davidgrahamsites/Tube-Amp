# Power contact screening — November24

No contact is selected by this review. It narrows the regulator search before footprint or heatsink dimensions are frozen.

| Candidate | Evidence | Disposition |
|---|---|---|
|Molex0009483031 /09-48-3031|[Mouser listing](https://www.mouser.com/en/ProductDetail/Molex/09-48-3031?qs=ZwgtpdmWYYR3xA3qvqfIMQ%3D%3D) labels it obsolete and unavailable in the retrieved region.|Reject as the normal new-build sourcing route. Broker stock claims do not establish a reliable Chinese purchase path.|
|TE5050865-5|[Manufacturer](https://www.te.com/en/product-5050865-5.html) lists6.5A maximum,−65…125°C,1.83mmPCB hole and0.86–1.04mm mating-pin diameter. Page says active but presently unavailable directly.|Candidate only. Circular pin acceptance does not qualify the ST0.61–0.88mm×0.48–0.70mm rectangular lead range. No native hole adoption.|
|HarwinH3161-01|[Manufacturer](https://www.harwin.com/products/H3161-01) specifies0.90–1.05mm round mating pins and10A at25°C/7.5A at85°C.|Candidate only; adequate headline current does not establish rectangular-lead compatibility.|
|Mill-Max receptacle family|[Manufacturer brochure](https://www.mill-max.com/sites/default/files/external/assets/2024-11/mmax-pins-recepticles-brochure-web_version-final.pdf) supports round/square/rectangular leads in principle.|No exact contact selected; require its exact lead limits, drawings, current derating and domestic stock.|

The auxiliary [supply envelope](../../whole-amp/aux-supply/envelope-review.md) now supplies conditional current/thermal bounds. It does not qualify fault current, contact temperature or actual socket fit. The current4regulators must remain separately removable from their heatsinks; U7 pin mapping/tab potential differs from L78. Neither a regulator's socket nor its solder joints may carry heatsink or service extraction loads without mechanical support.

The small SOT23 supervisor still needs a qualified socket-compatible circuit or keyed removable adapter. DIP8/14 and all tube sockets remain unqualified. Do not exempt a device or equate a package name with an actual socket. No ordering/contact/upload occurred.
