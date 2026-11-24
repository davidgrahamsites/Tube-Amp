# Socket requirement checkpoint — November 24

All ten current ICs and six tubes are covered by `socket-plan.json`. The read-only checker passes six inventory checks and three negative controls, including omission of U7 and addition of an unreviewed IC. **No socket assembly is yet qualified or integrated.** DIP packages alone do not satisfy FB-116.

- U1/U2: two DIP-14 sockets.
- U10/U11/U12: three DIP-8 sockets.
- U3: SOT-23-6 supervisor. Select a functionally suitable socket-compatible replacement or design a keyed removable adapter, then recheck threshold, timing, reset and bypass routing.
- U4–U7: four TO-220 regulators. Contacts must accept actual rectangular leads and carry continuous/fault current; mechanical retention and the heatsink require separately removable fasteners. U7 has a different pin map and its negative-input tab must remain insulated from a common grounded heatsink.
- V1–V4: four noval tube sockets; V5/V6: two octal sockets. Exact ratings, retainers, tube heat and extraction space remain open.

## Supplier and drawing evidence

[CONNFLY DS1009-08AT1NX-0A2](https://item.szlcsc.com/73233.html), C72124: observed stock28,840, MOQ20, ¥0.17578 each at MOQ on November24. Candidate only. Its linked manufacturer [drawing](evidence/connfly-ds1009.pdf), C-DS1009-XXXX-XXX-E revE, gives 20mΩ maximum contact resistance, -20…105°C, and recommended 0.85±0.05mm PCB holes. The 500VAC/one-minute dielectric test is **not** a continuous working-voltage rating. It omits rated contact current and mating-lead acceptance limits; do not use it for power regulators or HV merely because its contacts fit visually.

The DS1009 drawing identifies 8-pin body length10.16±0.5mm, body width10.16±0.3mm and row spacing7.62±0.3mm; 14-pin body length17.78±0.5mm. PCB row/pitch drawing and mating range need separate interpretation before selecting finished holes. The 4.80mm nominal body-height indication is not a populated IC-plus-socket clearance. Square socket openings are unrelated to whether PCB drills should be round or slotted.

C41512 is discontinued. The live SN74HC74N search result from XBLW is **not** the selected TI SN74HC74N; no substitution adopted. The observations file distinguishes manufacturer identity, stock, MOQ, source and date. [LCSC domestic shipping policy](https://www.szlcsc.com/help/1102.html) supports mainland shipping in principle; exact Shanghai address/freight remains unchecked.

## Concrete lead-fit issue

ST [L79](https://www.st.com/resource/en/datasheet/l79.pdf), tables10/11, gives TO-220 lead width up to0.88mm and thickness up to0.70mm. The conservative bounding rectangle diagonal is1.1245mm. U7's current1.1mm nominal round drill cannot contain that full rectangle even before assembly/tolerance allowance. Socket adoption will replace that direct-lead interface, so its final holes must follow the **socket terminal** drawing. Do not simply enlarge every existing hole by a guessed amount. Final contact fit/retention must also work at the minimum lead dimensions, not just the maximum diagonal.

## Next action

Resolve the supervisor route and exact regulator contacts/heatsink fastening, then carry verified socket geometry and removal envelopes into the three-board assembly. The nearby supply review also found and corrected [C212's aluminium-capacitor value](../../whole-amp/aux-supply/review.md). This inventory does not close electrical, thermal or chassis qualification.
