# Existing local ceramic bypass selection — November 25 reconciliation

Owner: component selection. This reconciles P076 with already adopted native C351, C352 and C353. It does not replace parts, alter a trace, or claim new layout qualification.

All three select **Yageo CC0805KRX7R9BB104** in circuit source, the native logic-power sheet and Control PCB. They use `Capacitor_SMD:C_0805_2012Metric`, two1×1.45mm SMD pads on1.9mm centers, +5V/GND. They require no component drill holes. The full23-file native schematic/board/source set is byte-identical to commit95d1d6a; see [identity and hash receipt](local-bypass-parity-2026-11-25.json).

The [manufacturer specification](https://yageogroup.com/download/specsheet/CC0805KRX7R9BB104), retained as `Yageo-CC0805KRX7R9BB104-2026-11-25.pdf`, identifies100nF,10%,50V,X7R,0805, body2±0.2×1.25±0.2×0.85±0.1mm, rated−55..125°C. This is a ceramic supply bypass rather than a signal-path film selection. Rated voltage alone does not establish actual capacitance, impedance or noise performance at temperature/bias; assembled loop verification remains open.

[Domestic LCSC C49678](https://item.szlcsc.com/50686.html) independently matches exact MPN,0805,100nF,10%,50V,X7R. The retrieved web page exposes no live quantity, MOQ or RMB price; direct HTTP retrieval returns405. Those fields remain unknown. Mainland supplier identity is established, but exact Shanghai checkout/delivery and current availability are unverified. No order, account operation or supplier communication was made.

Committed coverage P076 still referenced the former KNSCHA film part. A pre-existing working correction selected this ceramic but linked a missing November21 evidence file. This dated reconstruction replaces that pointer without inventing a historical report. P076 is removed from the film candidate's current coverage; its dated historical notes are retained. Unrelated working registry changes are preserved and excluded from this commit.

No ERC/DRC rerun is needed for these documentary changes because every native file is unchanged. This identity check is not a fresh bypass placement, return-path or EMI sign-off. In particular, the later proposed use of U1F must preserve a proper C351 ground return when its presently grounded input pin is repurposed. Keep that dependency in the power-sequencing integration.

Human check: confirm the supplied reel label and component dimensions against the exact part, inspect both solder joints and local supply/ground routing, and measure rail disturbance on the populated board. Full amplifier qualification and fabrication release remain open.
