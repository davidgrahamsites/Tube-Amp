# Bias resistor screen contract

One job: reproduce bias-resistor power estimates from the existing ideal-source fixture.
Owner: component-selection engineering. Public output: `runs/results.json`.
Inputs: original16 decks in `../../bias-cap-screen/` relative to component-selection; existing `engineering/whole-amp/tools/spice_runtime.py` adapter and installed KiCad ngspice library. Exact relative paths are resolved by the factory.
Process: run `python3 engineering/component-selection/evidence/bias-resistor-screen/factory/run.py` from project root. Original16 comparison plus high-source phase/capacitance/resistance corners. No design files changed.
Outputs: structured case inputs, complete decks, source hashes and per-case metrics in `runs/results.json`; ngspice messages/version in `runs/ngspice.log`. Stable factory is separate from products.
Human check: inspect worst-case R39/R40 waveforms and manufacturer pulse curves before release. Verify actual transformer voltage and hot enclosure temperature; this ideal-source model cannot qualify hardware faults.
