# Audio headroom and precision rail-inhibit candidate

Owner: control-switching integration. Baseline1537482. Task: bind the monitor to the existing10Vpeak audio target, develop a concrete replacement, and retain exact Chinese sourcing. Inputs are the native reverb circuit, preceding static/latency results and manufacturer documents. Outputs are two editable contracts, two reproducible budgets and this review. Estimated effort: one engineering checkpoint. This checkpoint is complete when arithmetic/provenance and ICM checks pass; native adoption and hardware qualification are separate gates.

## Corrected acceptance boundary

The native six OPA2134 signal units retain10Vpeak. U10A/U11B followers need input common-mode headroom as well as output swing. [TI OPA2134 RevB](https://www.ti.com/lit/ds/symlink/opa2134.pdf), table5.7, supplies the25°C offsets used for the13.5V positive/12.5V negative-magnitude screening floors. Applying these offsets during decay remains an allocation, not a full-temperature guarantee. [ST L78](https://www.st.com/resource/en/datasheet/l78.pdf) table16 and [L79](https://www.st.com/resource/en/datasheet/l79.pdf) table9 give14.25/14.3V healthy minima under their stated input/load/temperature conditions, not a shutdown waveform.

The earlier buffered candidate permits release down to9.612/9.102V, below even an ideal10Vpeak output rail. Its11 passing static screens did not establish the required audio margin. A resistor-only proportional retune cannot fit the positive window: the4.75–5.25V reference spread forces an ideal13.5V low threshold to14.921V at the other extreme, above14.25V. The previous candidate remains historical evidence; no native circuit ever adopted it.

## Concrete replacement

The candidate uses TI REF5050AIDR plus LM393BIDR, both SOIC8 on removable socketed carriers. No socket exception is adopted. REF5 is distinct from logic+5V. Positive sense uses1.78k/1k and61.9k feedback against direct REF5. The negative attenuated-clamp network uses6.19k+68ohm toward the negative rail and499k feedback; other values are explicit in rail-monitor-precision-contract.json. RAIL_OK pulls up through1.5k to REF5 with a7.5k REF5 bleeder, so reference absence is not masked by the independent logic supply. Existing delay/inhibit topology remains unadopted; native R341 is still1k.

[TI REF50 RevO](https://www.ti.com/lit/ds/symlink/ref50.pdf) standard-grade limits, not high-grade marketing text, feed a conditional0.3% reference allocation. Its declared static terms total0.2884%; lifetime, hysteresis and solder coverage remain unqualified. [TI LM393 RevAH](https://www.ti.com/lit/ds/symlink/lm393.pdf) SOIC B-version full-temperature offset/bias bounds replace classic-part bounds. A typical1us response is not a maximum. The0.4% resistor profile remains conditional on exact parts and the documented0–85°C film profile.

| Magnitude | Enable range | Disable range | Minimum same-unit hysteresis |
|---|---|---|---|
| Positive |13.9028–14.1702V|13.7687–14.0412V|0.1113V|
| Negative |13.0737–14.2111V|12.7695–13.9265V|0.2458V|

16,640 endpoint cases and2,000 independent KCL comparisons give14/14 conditional static screens; maximum algebra/KCL discrepancy is1.78e-14V. Positive/negative minimum headroom margins are0.2687/0.2695V. The native57.4uF per rail, reduced by a20% sensitivity allowance, gives about0.123ms isolated hold at100mA. Actual regulator feed, raw reservoir, backfeed, temperature and load waveform can change this substantially. Relay coil decay evidence does not meet this interval; actual fast-mute timing remains to establish.

The first10k bleeder trial failed the passive reference-off0.9V allocation with0.9806V. The earlier8.2k version bounded it at0.8474V and reference load at9.5834mA. VAL-052 now uses7.5k for the combined AC-loss detector: its separate combined-node audit gives0.8187V passive reference-off RAIL_OK and9.8511mA total reference load. The regenerated standalone rail monitor still passes14 conditional checks; see ac-loss-review.md for the added interface. The off-state calculation assumes the reference sources no current and omits semiconductor backfeed; it is not a complete reference-failure guarantee. The0.9V screen comes from SN74HC14's4.5V negative-going limit; intermediate logic supplies and full startup sequence remain open.

## China supply route

Observed2026-11-25; exact record fields and source hashes are in evidence/precision-source-observation.json. [REF5050AIDR C27804](https://item.szlcsc.com/28554.html) reports9688 stock, minBuy1/ratio1. The tape variant avoids the rejected1000-piece tube route. [LM393BIDR C2865059](https://item.szlcsc.com/3069736.html) reports98286 stock, minBuy1/ratio5; budget five physical pieces pending basket confirmation. LCSC's [domestic courier policy](https://www.szlcsc.com/help/202.html) supports a Shanghai route in principle; no address-specific order/quote exists. Exact precision resistor SKUs, socket/carrier assemblies and bypass parts remain to source. These observations do not establish that the entire amp is purchase-ready.

## Reproduce and next gate

Run tools/audio_headroom_budget.py then tools/precision_rail_budget.py with Python3. Both only read CAD. The first's five passing evidence checks establish rejection of the old boundary, not circuit qualification. The second verifies headroom-result provenance before calculations. qualification=false is intentional in both reports.

Next: independently model the powered/unpowered reference and logic interface with the actual mute device, determine normal startup/power-down timing, then source the exact resistor/socket set. Only after this gate should native schematic/PCB adoption be attempted with connectivity/ERC/DRC/visual preservation checks. Keep functional blocks and rear-panel/drill-access requirements intact. Human check: measure audio headroom, rail collapse, reference and RAIL_OK plus wet output on one assembled prototype, at recorded signal/load/temperature conditions. All six through-chassis scopes remain open; no manufacturing release.
