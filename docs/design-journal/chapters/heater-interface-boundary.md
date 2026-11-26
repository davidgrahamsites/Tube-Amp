# Shared heater reference: simulation exposed an interface boundary

**Source checkpoint:** 26 November 2026; HD-002, VAL-076

**State label:** diagnostic evidence independently checked; engineering qualification remains false

**Baseline:** native baseline `d5566cd`; no native changes.

## The problem

The preceding heater-divider rating work established a component-stress problem but did not prove that all six tube units could share one heater reference across the modeled signal and supply conditions. The user had also emphasized that all components need appropriate wattage and size. That requirement remains important, but HD-002 exposed a separate interface constraint: increasing R506's wattage cannot repair an empty heater-to-cathode voltage window or a DC reference resistance above the reference EL34 limit.

## Requirements and authority

The screen uses JJ EL34 reference limits of 100 V and 20 kΩ, and JJ ECC83S reference limits of 180 V and 150 kΩ. These documents are candidate limits, not verified identities of installed or purchased tubes. Because the manufacturer documents do not explain polarity or AC timing for the voltage limit, the diagnostic conservatively applies an absolute instantaneous terminal-voltage limit including the heater sine peak. Different exact tube types or manufacturer guidance require a fresh applicability review.

All six units share HEAT_A/HEAT_B in the current native design. The modeled heater ceiling is 8 V RMS; it is not measured or approved operation at that voltage. The divider and midpoint tolerance/drift assumptions are encoded in the source contract. These limits define the screen, not a user-approved topology change.

## Evidence and reasoning

The current 220 kΩ/39 kΩ divider and two 100 Ω midpoint resistors yield a best-case stiff-source DC reference resistance of 33.177 kΩ nominal, or 36.574 kΩ under the declared tolerance/drift allocation. Even nominal exceeds the reference EL34's 20 kΩ limit. C505 lowers AC impedance but does not change DC resistance. The screen omits actual supply impedance, so it cannot claim that the physical circuit has a lower resistance.

The generic 12AX7A/6CA7 fixture covers clean and dirty channels; three input levels (1, 20, and 200 mV peak); two gain fractions; and three stiff B_PRE levels (275, 313, and 355 V), with B_SCREEN fixed at 380 V. Thirty-six base cases plus two longer, finer repeats complete. The conservative heater-endpoint excursion bound is ±5.76998 V around HREF. For each sampled cathode extremum, the checker derives the HREF interval required for each tube and intersects intervals across candidate groups.

Fourteen of 38 completed cases have no HREF interval common to all six units. Aggregate results show that separating only power tubes from preamp tubes does not fully solve the screen: at B_PRE=355 V, the preamp-only interval is 176.309–175.127 V and is empty. V3's two triodes share one heater, and the cathode-follower excursion pushes the lower bound upward. Near-ground power-tube cathodes cap the upper bound. The two longer/finer repeats preserve the shared-reference failure, with cathode-follower peak differences below 1 mV.

The coordinator's independent checker reconstructs 114 group windows; all 38 cases complete, 14 shared windows are infeasible, all 22 native hashes are preserved, and evidence checks pass. The checker does not change the model's scope: generic tubes, stiff rails, ideal output transformer/wet source, present passive routing, and no full transformer-powered or chassis behavior.

## Options and tradeoffs

A higher-wattage R506 may address the earlier resistor fault screen, but it does not resolve voltage-window incompatibility or DC reference resistance. Reducing audio gain, clamping the cathode follower, or substituting tube types solely to force a passing screen is not endorsed by the review.

The next candidate is isolated heater groups with separately bounded references while retaining the audio functional blocks. Four ECC83S heater loads sum to 1.2 A; two EL34 heater loads sum to 3.0 A. At 6.3 V, their combined nominal heater load is 26.46 W before pilot, regulation, and startup allowance. These are load sums, not transformer winding ratings. A continuous winding or its center tap does not create two independently isolated references.

Group separation alone leaves the 355 V preamp case failing because V3 shares a heater. A bounded lower B_PRE, exact tube limits, or another supported local solution needs study. A roughly half-B_PRE preamp reference is only a candidate to test. Delayed heater-reference behavior must be modeled with actual startup, rather than assumed to track an instantaneous fraction of B_PRE. The transformer requirement for a single heater winding is therefore not qualified by this screen.

## Decision and native change

VAL-076 documents the shared-reference compatibility boundary and the evidence checks. It adopts no new parts, transformer winding, audio topology, or native layout. Isolated groups and a bounded preamp rail/reference are next candidates, not selected design. No fabrication release follows.

## Verification and limits

The independent interval checker verifies 114 reconstructed windows and preserves 22 native files. The 38 simulations and two refinements reproduce a diagnostic incompatibility under stated assumptions. Engineering qualification remains false. Exact purchased tube identities and limits, full-frequency and tube-corner behavior, supply impedance and startup/fault response, heater leakage, insulation, thermal conditions, and actual physical measurements remain open.

## Remaining tests and next action

Establish the least intrusive complete heater supply/reference envelope. Evaluate any isolated-group candidate with the 355 V preamp case, including V3's shared heater, exact tube limits, rail tolerance, signal excursions, resistor drift, capacitor charge/discharge, cold startup, heater faults, leakage, insulation, and reference-clamp failures. Then qualify resistor voltage/power, exact China-sourced parts, transformer winding capability, connector/trace current, and populated fit together. Do not assign the nominal 26.46 W load sum as a winding rating.

## Physical-build placeholder

If a revised design proceeds, log exact tube manufacturer/type/lot, heater and reference waveforms, cathode-to-heater extrema, startup and defined fault conditions, instrument and probe ratings/loading, calibration check, thermal state, and safe test procedure. There are no physical measurements in HD-002.

## Reusable lesson

A component's wattage and package are only one part of its operating boundary. Shared references, DC resistance, common-heater grouping, signal excursions, startup, and transformer interfaces can fail independently of resistor power. Use a verified screen to identify the boundary, preserve assumptions, and keep candidate architecture separate from an adopted and physically qualified design.

## Sources

- [User component-rating requirement FB-141](../../../brain/feedback/events.json)
- [VAL-076](../../../brain/records/VAL-076-heater-interface-boundary.md)
- [HD-002 review](../../../engineering/component-selection/heater-divider-rating/interface-review.md)
- [Screen contract](../../../engineering/component-selection/heater-divider-rating/interface-contract.json)
- [38-case result](../../../engineering/component-selection/heater-divider-rating/results/interface-screen.json)
- [Independent interval-check receipt](../../../engineering/component-selection/heater-divider-rating/results/interface-checks.json)
- [Simulation log](../../../engineering/component-selection/heater-divider-rating/results/interface-simulator.log)
- [Preceding VAL-075](../../../brain/records/VAL-075-heater-divider-rating-boundary.md)
