# Reset divider stability and procurement screen

Owner: control interface. November 24, 2026. Candidate comparison only; native U3
remains unchanged. `divider-contract.json` supplies limits to
`tools/check_divider_options.py`; `results/divider-options.json` is its output.
The historical contract, model and previous brownout results are preserved.

The Vishay TNPW080530K1BEEA / TNPW080510K0BEEA pair retains 30.1 kΩ / 10 kΩ.
The [manufacturer specification](https://www.vishay.com/docs/28758/tnpw_e3.pdf),
revision April 10, 2026, is retained with a hash under component-selection/evidence.
Pages 2, 4, 12 and 14 establish operating mode, tolerance/TCR and drift limits.
The endurance table was visually inspected. This comparison adds soldering drift
to initial, temperature and endurance errors independently for both resistors.
It uses a proposed −40…90 °C film-temperature screen; actual carrier temperature
is unmeasured. The general operating mode requires a suitable thermal assembly.

| Screen | Falling margin above 4.5 V | Rising margin below 4.75 V | Proposed 20 mV allocation |
|---|---:|---:|---|
| Previous Yageo endurance calculation | 10.51 mV | 6.93 mV | Fail |
| TNPW after soldering | 42.22 mV | 40.20 mV | Pass |
| TNPW general-mode 1,000 h | 38.81 mV | 36.65 mV | Pass |
| TNPW general-mode 8,000 h | 35.41 mV | 33.10 mV | Pass |
| TNPW general-mode 225,000 h | 21.83 mV | 18.87 mV | Fail |
| Additive humidity/thermal-cycle sensitivity | 21.83 mV | 18.88 mV | Fail |

These are bounded arithmetic screens, not a field-life prediction or combined
stress guarantee. Each profile enumerates 16 threshold/leakage/resistor corners
and is independently checked against the monotonic endpoint expression. A 1%
resistor-pair negative control fails. The 20 mV allocation remains proposed;
actual ripple, dynamic rail collapse, reset propagation and clock recovery still
need qualification. Do not adopt this pair merely on its 8,000-hour result.

## Dated purchase evidence

Observed November 24 through web retrieval; indexed stock may be stale. No order
or exact-address checkout was made.

- [DigiKey global 30.1 kΩ BEEA](https://www.digikey.com/en/products/detail/vishay-dale/TNPW080530K1BEEA/1857116)
  indexed 10,597 pieces, cut-tape MOQ 1, USD 0.41. Direct China product-page fetch
  was unavailable; this does **not** verify that exact part's Chinese purchase route.
- [DigiKey China 10 kΩ BEEA](https://www.digikey.cn/zh/products/detail/vishay-dale/TNPW080510K0BEEA/1857095)
  showed zero stock, CNY 3.39 at one piece. Its listed alternatives included
  10 kΩ BEEN (8,120, CNY 5.87), BXEN (2,198, CNY 7.86) and BYEN (548, CNY 10.83).
  These are leads for follow-up, not interchangeable approved picks. TCR codes
  E/X/Y mean 25/15/10 ppm/K respectively; packaging identity also needs checking.
- [DigiKey China delivery policy](https://www.digikey.cn/zh/help/features)
  establishes a China/CNY/DDP route, including mainland courier delivery in
  principle. It does not confirm an exact Shanghai order or delivery date.
- [Susumu RG1608N-3012-B-T5](https://www.digikey.com/en/products/detail/susumu/RG1608N-3012-B-T5/1259786)
  indexed a 15,000-piece order quantity and 18-week lead time; unsuitable for this
  low-cost prototype through that offer. The LCSC international catalogue entry
  C1709086 did not expose usable loose-stock/price evidence in retrieval. JLCPCB
  assembly inventory is not proof that loose parts can be purchased.

Conclusion: improved drift is a viable direction, but the pair is neither selected
nor purchase-ready. Next select an available tighter-TCR pair or a more suitable
supervisor threshold implementation, then qualify its removable carrier, reset
timing and actual supply conditions. Keep all functional blocks intact.

Human check: compare received MPNs and measured thresholds at cold/hot rail limits;
verify the carrier temperature, assembly process and reset/clock behavior before
accepting this interface.
