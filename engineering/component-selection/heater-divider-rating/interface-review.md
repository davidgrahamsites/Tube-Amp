# Heater-reference compatibility boundary

November 26, 2026; HD-002; native baseline d5566cd. This diagnostic follows the [resistor rating screen](review.md). No native circuit, board, component selection or audio topology changed.

## Evidence and interpretation

The reference manufacturer documents specify 100 V heater-to-cathode and 20 kΩ heater-to-cathode resistance for [JJ EL34](https://www.jj-electronic.com/images/stories/product/power_tubes/pdf/el34_e34l.pdf), and 180 V / 150 kΩ for [JJ ECC83S](https://www.jj-electronic.com/images/stories/product/preamplifying_tubes/pdf/ecc83s.pdf). These are reference candidates, not verified identities of purchased tubes. The source excerpts and provenance are in sources/tube-limits.json. The first-page voltage limits do not explain polarity or AC timing; this screen conservatively applies an absolute instantaneous terminal-voltage limit, including heater sine peak. Manufacturer clarification or another exact tube requires a fresh applicability review; it must not silently inherit another brand's rating.

All six native heater units share HEAT_A/HEAT_B. The 220 kΩ / 39 kΩ divider and two 100 Ω midpoint resistors give a best-case stiff-source DC reference resistance of 33.177 kΩ nominal, or 36.574 kΩ with the declared tolerance/drift allocations. Even the nominal value exceeds the EL34 reference's 20 kΩ. C505 lowers AC impedance but does not remove this DC resistance. Actual screen-supply impedance is omitted, so the calculation cannot claim the real circuit has a lower resistance.

The existing generic 12AX7A/6CA7 fixture supplies cathode voltages for both channels, three input amplitudes (1/20/200 mV peak), two gain fractions and three stiff supply cases. B_PRE is 275/313/355 V; B_SCREEN is fixed at 380 V. This is 36 base cases plus two longer, finer repetitions. The fixture retains the current passive routing, ideal output transformer and ideal wet source; it is not the future common-buffer implementation or an actual transformer-powered amplifier. The original pentode model is unchanged; the existing fixture's local numerical fractional-power guard is declared in the saved source hash.

Heater voltage is conservatively assumed up to 8 V RMS, not measured or approved operation at that voltage. With the declared midpoint mismatch, the endpoint excursion bound is ±5.76998 V about HREF. For each tube and every sampled cathode extremum, the allowable HREF interval is calculated, then intersected across the group. An empty interval proves failure under these declared assumptions; a nonempty interval is only a necessary condition.

## Results

All 38 runs complete. Fourteen have no shared-reference solution for all six tubes. Across the sampled cases at each supply:

| B_PRE | Required HREF for all six | Required HREF for preamp tubes alone |
|---|---|---|
|275 V|96.830–94.229 V: empty|96.830–174.921 V|
|313 V|134.574–94.229 V: empty|134.574–175.019 V|
|355 V|176.309–94.229 V: empty|176.309–175.127 V: empty|

The dirty cathode follower drives the lower bound upward during overload; the near-ground power-tube cathodes cap the upper bound. The two extended runs double the simulated duration to 160 ms, measure its final 20 ms, and halve maximum timestep to 1 µs. Their cathode-follower peak differences are below 0.001 V and both retain the shared-reference failure. This supports a reproducible diagnostic, not convergence at every frequency or tube corner.

The independent checker reconstructs 114 group intervals from all combinations of cathode extrema and heater endpoints. Source/model/factory/result hashes and 22 native hashes pass. These are evidence checks; engineering qualification remains false. Raw extrema, case settings, model/fixture provenance and simulator messages remain in results/interface-screen.json and results/interface-simulator.log.

## Decision and correction boundary

Do not adopt a larger R506 as a complete heater-system cure. A wattage increase addresses one resistor failure; it cannot repair the incompatible voltage window or the DC-reference resistance. Do not reduce audio gain, clamp the cathode follower or substitute tube types merely to make this diagnostic pass.

The next engineering candidate is isolated heater groups with separately bounded references, keeping the audio functional blocks intact. Four reference ECC83S heaters need 1.2 A at 6.3 V and two EL34 heaters need 3.0 A, totaling 26.46 W nominal heater load before pilot, regulation and startup allowance. These are load sums, not transformer winding ratings. A single continuous winding or its center tap does not provide two independently isolated references.

Separation alone does not resolve the 355 V preamp case: both triodes in V3 share one heater. A bounded lower B_PRE, a suitable exact tube's documented limits, or another supported local solution must be evaluated. A roughly half-B_PRE preamp reference is a candidate to test, not a selected divider. Actual rail tolerance, signal excursions, resistor tolerance/drift, capacitor charge/discharge, cold startup, heater faults, leakage, insulation and reference-clamp failure must all be included. A delayed heater reference must not be treated as an instantaneous fraction of B_PRE.

The existing single-heater-winding transformer requirement is therefore not qualified by this screen. Exact transformer selection remains open; no additional transformer or winding has been ordered or committed to CAD. Next establish the least intrusive complete supply/reference envelope, then verify resistor voltage/power, exact China parts, connector/trace current and populated fit together. Objective 6 and fabrication release remain open.
