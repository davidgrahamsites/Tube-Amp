# Auxiliary supply and socket thermal envelope — November24

**The provisional supply is not qualified.** Seventy-two rectifier/load cases, four limiting-case timestep repeats and three proposed-preload repeats completed. Evidence checks pass;48 of72 baseline cases have at least one engineering-screen flag. These flags are not48 measured failures, nor do unflagged cases establish build readiness.

## Task card and scope
Owner: Renegade integration. Input revision:a1ddf86, current circuit hash recorded in results. Inputs are `envelope-contract.json`, current sheet08 topology, ST L78/L79 and TI/Omron data. Output is `results/envelope/`, consumed by socket/heatsink and transformer selection. Effort: one bounded simulation/review checkpoint. Done-condition for this checkpoint: reproducible completed runs, topology guard, independent current-balance and thermal arithmetic checks, limiting-case refinement and explicit assumptions. Physical transformer/load data, retained socket samples and measured cabinet temperatures are required before supply acceptance.

`tools/screen_envelope.py` owns this raw rectifier model and thermal postprocessing. `tools/check_envelope.py` independently audits its evidence. `tools/screen_bleeder.py` performs only three targeted proposed-preload comparisons. None edits source/native circuits.

## Model boundary
The fixture preserves the four-diode centre-tapped rectifier and the two1000µF reservoirs, including polarity. It assumes800/1200µF capacitance,0.15Ω ESR and generic rectifier diodes. Two illustrative winding equivalents use19.8V/7.2Ω and21.6V/14.4Ω per half at nominal line. They approximate18V/0.25A with10/20% resistive regulation; they are **not selected transformer specifications**. Line factors0.9/1/1.1 at50/60Hz do not implement or verify the120/220V mains switch.

Loads ramp onto the raw rails after50ms; regulator control loops and output capacitors are absent. Thirty milliamps per audio rail comes from six amplifiers' stated quiescent-current maximum; added20/70mA signal/expansion allowances are assumptions. Logic loads2/10/20mA are scenarios. The energized-coil allowance uses the selected H1 relay's12.6V/864Ω corner, at the resistance reference temperature. These are not complete operating/fault load budgets.

Manufacturer bases: [ST L78 DS0422rev38](https://www.st.com/resource/en/datasheet/l78.pdf), tables2/10/15/16; [ST L79 DS0428rev24](https://www.st.com/resource/en/datasheet/l79.pdf), tables2/9; [TI OPA2134 SBOS058B](https://www.ti.com/lit/ds/symlink/opa2134.pdf), section5.7; [Omron G5V-2](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v2.pdf), H1 coil table. Exact values, assumptions and source scope are retained in the contract. Datasheet test ranges are screens, not modeled dropout curves.

## Results

| Scenario | Maximum half-winding RMS | Maximum conditional regulator heat, all4 | Tightest shared-sink budget at60°C ambient |
|---|---:|---:|---:|
| Idle,30mA/audio rail; relays off |0.107A|1.92W|18.65°C/W|
| Working reserve,50mA/audio rail;3relays on |0.194A|3.05W|10.85°C/W|
| Expansion stress,100mA/audio rail;3relays on |0.279A|4.04W|7.94°C/W|

Sixteen expansion cases exceed the provisional0.25A half-winding rating. Working-reserve cases do not, but that alone does not select a9VA transformer: actual thermal rating, core loss, regulation, mains winding and load dynamics remain unknown. Twenty-three cases exceed the positive supply's conservative documented-range screen; four exceed the negative range. None of these72 cases exceeds35V raw. Do not infer surge or no-load protection from that result.

Thermal calculations use100°C target junction,40/60°C local ambient,5°C/W junction-case and an assumed1°C/W insulating interface. Device output bounds are taken in the worst heat direction; their sum is a conservative combination of independent bounds. It is valid only conditionally on regulation. For a shared sink the temperature rise uses **total** power, not each regulator's individual dissipation. Bare-package reference estimates reach128.8°C at the60°C stress corner; this supports reserving a real heatsink, not assigning a physical temperature to the unbuilt chassis. U7's negative-input tab needs electrical isolation from grounded/common metal. Supplier thermal curves, mounting torque, insulation and airflow must replace assumptions.

## Minimum-load correction candidate
All24 idle cases use2mA on5V, below L7805C's5mA regulation condition. The current quiet logic has no documented guaranteed5mA floor. An820Ω±1% preload across5V/GND would provide at least5.735mA at4.75V and dissipate at most33.95mW at5.25V. A1kΩ±1% alternative fails the standalone minimum-current screen. Temperature coefficient, ageing, physical derating and exact Chinese-stock part selection remain open.

Three targeted repeats add the proposed preload's maximum6.467mA to each scenario's worst-heating baseline. U5's minimum-load flag clears in those scenarios; additional regulator heat is at most0.143W. This does not cure the transformer or input-range flags. **No preload is yet adopted in native CAD.** Verify reset/startup behavior and exact part/package before integration.

## Evidence and limits
All runs reach0.6s. Metrics cover the final0.2s. Independent positive/negative raw-node KCL checks pass; all four selected limiting cases retain their flags at half timestep. Raw minimum-voltage differences stay below36µV and winding-RMS differences below0.0013%. Four deliberate corruptions—missing case, reversed diode text, incorrect shared-sink heat and truncated run—are rejected. These tests establish fixture/evidence consistency, not semiconductor model validity.

No regulator stability, startup/reset, short-circuit, reverse-current, audio-current waveform or EMI/RFI simulation is claimed. Exact diode and transformer models are still needed. Source, native schematic and boards remain unchanged; existing ERC/DRC results are not rerun or relabelled as new passes. This screen advances power/socket selection and keeps all three functional blocks intact.

## Next action
Resolve the exact auxiliary transformer and regulator/socket assembly together; incorporate an evidenced5V preload, local bypass and split-rail protection as one reviewed native change. Keep all10 ICs and6tubes socket-required. Carry heatsink/retention/removal envelopes into populated three-board fit. Actual drill envelope remains deferred untilNovember25. No fabrication release.
