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


## November 25: rectangular-lead and replacement check

The manufacturer explicitly uses a rectangular lead's diagonal as its effective diameter. [Mill-Max pages 248–249](https://www.mill-max.com/sites/default/files/external/catalog/2019-06/248-249.pdf) also describe permanent contact sizing: a previously inserted larger lead can raise the minimum acceptable replacement size. Saved primary evidence is in `evidence/mill-max-248-249.pdf`; the editable inputs and computed output are `contact-fit-contract.json` and `results/contact-fit.json`.

The ST lead bounds are 0.61–0.88 mm wide and 0.48–0.70 mm thick: [L78 Rev38, tables19/20](https://www.st.com/resource/en/datasheet/l78.pdf), [L79 Rev24, tables10/11](https://www.st.com/resource/en/datasheet/l79.pdf). Independent extrema give diagonals **0.7762–1.1245 mm**. This is an inference from the drawings, not a sample measurement.

| Contact | Initial acceptance, mm | Full published lead-range result |
|---|---:|---|
| Mill-Max #34 | 0.8128–1.1684 | Smallest lead is too small; after inserting the largest lead, minimum replacement rises to 0.8705 mm. |
| Mill-Max #36 | 0.5588–1.0668 | Largest lead exceeds maximum by 0.0577 mm. |
| Mill-Max #18 | 0.9398–1.0922 | Both ends of the lead range fail. |

**Do not select these three contacts as a universal replacement socket for U4–U7.** This does not reject every Mill-Max product or establish that sockets are impossible. It rules out substituting a nominal fit or headline current rating for tolerance and service qualification. The checker includes a hypothetical virgin-fit/pass but replacement/fail case and a compliant positive control. Neither hypothetical contact is a real part selection.

Next: identify a purpose-built flat-lead contact or regulator package/contact combination with documented full tolerance and replacement acceptance, then verify exact shell dimensions, plating, temperature, mechanical retention and China ordering. Preserve the default socket requirement; no performance exception or native change is adopted here.

### Cooling interface carried forward

The current auxiliary owner remains [VAL-069 load results](../../whole-amp/aux-supply/results/loads/raw-screen.json), not the older envelope snapshot linked above. Across its 72 baseline cases, conditional total heat peaks at **4.286827 W**. The tightest shared-sink requirement is at most **7.3961 °C/W at assumed 60 °C local ambient**, or 12.0616 °C/W at 40 °C, for the existing 100 °C junction target and assumed 1 °C/W case-to-sink path. This includes heat from all four regulators; it is not a sink selection or a guarantee at fault/startup conditions. A chosen sink must meet the requirement inside the actual cabinet, with its mounting orientation and insulation. The unadopted hold-up supply has a different heat budget and must not inherit this limit.

The mechanical interface must provide independent heatsink fastening, U7 tab isolation, access to its fastener and a regulator extraction path. Do not hang a heatsink from socket contacts or attach it to the removable wooden back. No thermal or populated-chassis approval follows from this arithmetic screen.
