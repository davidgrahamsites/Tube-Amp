# Low-voltage film capacitor selection — November 20, 2026
Owner: component integration. Scope: P090 (11 references) and P094 (2 references); no other group promoted.

Select KNSCHA MEB104J63V82CB0236 for C604, C610–C615, C203, C206, C210, C213. 100nF ±5%, 63V, polyester, 5mm pitch; body W7.2 x H6.5 x T2.5mm ±0.5; nominal lead0.5mm. Select MEB105J63V82CB0235 for C606/C607: 1uF ±5%,63V, polyester,5mm pitch; exact-part table W7.2 x H10.5 x T5mm ±0.5, lead0.6 ±0.05mm. The family matrix contains several sizes; the exact-part table governs. Both original manufacturer PDFs are saved alongside this report and page2 was rendered/inspected.

Engineering envelope: capacitor differential voltage <=32V and local ambient <=85C in normal operation. Supply bypass positions are on regulated 5/12/±15V nets; recovery/coupling positions are low-voltage audio. 63V rating gives 1.97x voltage ratio against this envelope. Above85C manufacturer derates voltage 1.25% per degree, so do not ignore enclosed-cabinet temperature. These are nonpolar film parts, avoiding ceramic voltage-dependent capacitance in the audio coupling path. This is suitability reasoning, not a listening-test claim. Board high-frequency bypass placement, startup, HV coupling-fault containment, ripple/temperature and physical fit remain to qualify.

Manufacturer sources (accessed November20):
- https://atta.szlcsc.com/upload/public/pdf/source/20220613/95E40529FEB7A3E68EC83AD5A7304622.pdf
- https://atta.szlcsc.com/upload/public/pdf/source/20220712/44A2F3FCFA20D943DF6A492DC0D1EB3A.pdf

Mainland distributor identities rechecked: https://item.szlcsc.com/3579063.html and https://item.szlcsc.com/4544345.html . Public extraction did not expose a current RMB quote/stock. Preserve November11 observations:100nF MOQ10, RMB0.263736,28K+;1uF MOQ5,RMB1.168,10K+. No new stock/date claim. Do not confuse JLCPCB assembly-only inventory with parts available for separate shipment.

R605 sourcing follow-up: https://www.oneyac.com/product/264604.html lists the different 5% FMP200JR-52-220R with zero stock,2500 MOQ,16-week lead time. This does not close the low-quantity domestic source. Keep the 1% FMP200FRF52-220R candidate unresolved; no silent replacement. R616 fault rating also remains unresolved.

New footprints use maximum body courtyard plus0.25mm, 5mm hole pitch,0.9mm finished drill and1.8mm pads. Lead forming/actual fit must be checked against the ±0.5mm pitch tolerance. No fabricated-board acceptance is implied.
