# Pot-cable loading — HI-003, 24 November 2026

Long interchangeable pot leads cannot yet be accepted for this amplifier. The source-derived small-signal experiment finds significant treble sensitivity at several high-impedance nodes. Insulation diameter compatibility from HI-002 does not establish audio suitability, and a factory-made 300 mm lead is not automatically acceptable.

## What was run

`tools/cable_loading.py` uses the existing effects-loop fixture with unchanged source values and nets, comparing FX_SEND with and without added cable capacitance. Thirty-six baseline settings cover clean/dirty channels, three volume fractions, three correlated tone fractions and three dirty-gain fractions. These are electrical resistance fractions, not front-panel rotation or audio taper. Each baseline has fourteen loading cases: 504 total, plus eight individual-pot attribution cases and two finer-grid comparisons. No source or native CAD was changed.

Each physical lead contributes a hypothetical capacitance to ground. A second family adds mutual capacitance between each pair of leads in the same pot harness. Repeated-net leads retain both contributions; a capacitor between identical nets is omitted. Grounded wires do not receive meaningless ground-to-ground capacitors. No cable resistance, inductance, cross-harness coupling, pickup or shield termination implementation is modeled. These capacitances do not come from the proposed UL1330 wire; its manufacturer table does not supply an installed harness capacitance matrix.

A proposed engineering budget compares absolute gain change against the identical unloaded case over sampled 100 Hz–20 kHz. **One dB is a screening choice, not a user-approved product specification.** The script also retains changes normalized to 1 kHz, so level loss can be distinguished from altered response shape. Mutual coupling sometimes increases treble by bypassing attenuation; lower loss alone does not mean better isolation or correctness.

## Results that affect placement

| Hypothetical capacitance per lead / pair | Settings within 1 dB over sampled band | Largest absolute change |
|---|---:|---:|
| 1 pF to ground / 0.5 pF mutual | 36 / 36 | 0.346 dB |
| 3 pF to ground / 1.5 pF mutual | 36 / 36 | 0.997 dB |
| 5 pF to ground / 2.5 pF mutual | 24 / 36 | 1.592 dB |
| 10 pF to ground / zero mutual | 10 / 36 | 1.932 dB |
| 30 pF to ground / zero mutual | 0 / 36 | 6.365 dB |

The 3/1.5 pF row has almost no margin and is **not a qualified capacitance allowance**. It covers only this matrix and excludes connector/PCB parasitics, tube variation and independent tone-control corners. There is no defensible length in millimetres until the cable geometry and its capacitance are known. A scalar pF/m value would also need the correct measurement configuration, not an arbitrary conversion of all pair/ground entries.

At midpoint settings, loading only one pot with 100 pF per lead and 50 pF per pair gives the following 20 kHz changes: RV1 clean treble −7.66 dB, RV3 clean volume −4.79 dB, RV4 gain −2.91 dB, RV5 dirty treble −4.95 dB and RV8 master −6.72 dB. The bass controls and mid control give smaller changes in these cases (−0.45, −0.27 and −0.12 dB respectively). This prioritizes placement; it is not permission to ignore their other operating settings.

**Placement handoff:** put each sensitive pot's board interface close to its actual associated stage/tone network and minimize the complete high-impedance path, including PCB tracks and service slack. Do not freeze equal-length generic leads across the panel or add shielding indiscriminately without including its capacitance. Preserve block ownership, PCB-side connectors, insulated conductors, independent wooden-back removal and strain relief. No buffer or extra PCB has been authorized by this experiment. Grouped panel harnesses may be compared with the ten-plug proposal if they preserve all pot-to-pot nets and serviceability; no grouping change is adopted here.

## Checks and limits

An independent 100 kΩ/100 pF RC calculation agrees with the simulator's complex 20 kHz response within 5.6×10⁻¹⁷. Zero-loading repetition is identical. Repeated physical lead and same-net pair controls pass. Added ideal capacitors leave FX_SEND DC unchanged within 1 µV across the sweep. The largest attenuation and largest 20 kHz boost cases were rerun at 10 Hz instead of 100 Hz spacing; their reported maxima agree. Source/model/factory/native-board hashes remain unchanged during execution. These checks validate the bounded comparison, not all operating states.

The inherited fixture uses generic tubes, stiff supplies, a 20 kΩ input source, 470 pF input cable and an ideal output transformer. Its output-stage limitations remain; this report does not certify output response/stability, large-signal headroom or EMI. RV9 presence and RV602 wet cables are not covered. Exact per-net fault voltage and insulation remain open. The circuit's requested treble retention therefore still needs real cable/model data and broader control-setting coverage before PCB and harness release.

Next: obtain a low-capacitance, traceable Chinese harness construction and exact connector mating geometry; use the placement study to estimate each run, then simulate its actual capacitance matrix at independent control settings. Continue the separate voltage/fault and physical-clearance work. No purchase or fabrication release.
