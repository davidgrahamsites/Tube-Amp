# Logic and audio IC selections — November 12

Select genuine TI **SN74HC14N** forU1 and **SN74HC74N** forU2. The domestic register records MOQ1 prices¥6.92 and¥4.16 respectively on November11. Their manufacturer sheets (TI-SN74HC14.pdf / TI-SN74HC74.pdf) specify2–6V operation; the nominal5V controller supply is appropriate. Ground unused HC14 inputs, retain bypass capacitors and keep inputs within supply rails. Debounce/reset sequencing, hot enclosure conditions and supply transients remain system checks. Neither device accepts12V relay voltage on its logic pins.

Select TI **OPA2134PA** forU10/U11/U12 in the current three-dual-opamp candidate. Domestic MOQ1 price¥45.22,66stock observed November11; three cost¥135.66. Its FET inputs suit the high-impedance recovery/input network, and the manufacturer model is already used for the electrical checks. This is a significant cost item, chosen for documented sourcing/model/PDIP support, not a claim that costlier opamps always sound better. Quantity may change only with a documented circuit revision.

TI-OPA2134.pdf gives recommended±2.5 to±18V operation, nominal±15V and ambient-40 to85°C. Rails are not an allowable signal swing; retain the10V-peak internal design limit and verify actual load/rail tolerance. The proposed attenuated send avoids forcing the tube's larger dry signal through these opamps. Real spring-drive current, recovery noise, rail sequencing and overvoltage protection remain checks.

Manufacturer sources fetched November12:
- https://www.ti.com/lit/ds/symlink/opa2134.pdf
- https://www.ti.com/lit/ds/symlink/sn74hc14.pdf
- https://www.ti.com/lit/ds/symlink/sn74hc74.pdf

Pin-function cross-check: HC14 inputs1/3/5/9/11/13, outputs2/4/6/8/10/12, ground7/supply14. HC74 clear1/13,preset4/10,clocks3/11,D2/12,Q5/9,/Q6/8,ground7/supply14. OPA2134 output1/7,inverting2/6,noninverting3/5,negative4,positive8. These match the captured circuit's unit/power pin assignments. Native package/lead-envelope review and regulator supply qualification remain pending. Ambient limits require a cool control/reverb board area.

The attempted OmronG5V2 primary PDF download returned403; do not treat that failed download as a completed relay dossier. Existing supplier candidates remain available for follow-up.
