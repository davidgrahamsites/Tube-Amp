# Brownout matrix and limits — 24 November 2026

Owner: control-switching. Contract: brownout-contract.json. Factories and receipts are in tools/ and results/. Native U3 remains TPS3808G50; no replacement is silently adopted.

Reran10 nominal reset cases and completed24 new dip cases plus two successive timestep refinements (36 total runs this checkpoint). The unmodified TI TPS389001 model was driven by ideal rail ramps to4.7/4.6/4.4/2V, with1µs/10ms ramps and1µs/100µs/20ms low plateaus. A completed run is not hardware qualification. Actual rail collapse, reset loading, relay rail persistence and clock interaction are absent from this bounded model.

The10µs-to1µs refinement failed the predeclared25µs transition tolerance (maximum163.89µs). The subsequent1µs-to0.2µs refinement passes the same tolerance (maximum8.374µs); both receipts are retained. Deep sustained dips assert reset; brief dips may not. A fast4.4V dip asserts after the rail has crossed4.5V, which is the adopted driver characterization floor, not the HC74 minimum operating voltage.

Threshold arithmetic exposes insufficient proposed noise margin after resistor endurance allowance:10.51mV falling and6.93mV rising against a proposed20mV allocation. Guaranteed complete assertion delay and actual rail slew remain unknown. Clock edges0/1/5ns after reset release violate the HC74's6ns recovery requirement at the stated4.5V/−40…85°C conditions. These are timing-limit comparisons, not simulated metastability results. Arbitrary clock coincidence is not qualified.

The previous vendor-model manual-reset CT-discharge discrepancy remains. Do not repair that model to manufacture a passing device claim. The TLV803E4.63V alternative is also not adopted: its maximum release4.793V exceeds the4.75V rail minimum and the reviewed3-pin parts lack MR.

Primary references: [TI TPS3890](https://www.ti.com/lit/ds/symlink/tps3890.pdf), [TI SN74HC74](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf), [TI TLV803E](https://www.ti.com/lit/ds/symlink/tlv803e.pdf). Next: resolve threshold/noise bounds, asynchronous clock reset release and removable carrier; qualify startup/collapse against the actual auxiliary supply. No native supervisor replacement or fabrication release.
