# Simulation tool qualification

One job: check that the installed ngspice engine can execute scripted analyses and return numerical data.

## Inputs
KiCad's bundled shared ngspice library and its native Python interpreter. API definitions follow the [official shared-library interface](https://ngspice.sourceforge.io/shared.html).

## Process
Run `qualify_ngspice.py` with KiCad's Python. Compare DC divider and transient RC results against analytic values; fail on missing vectors, nonfinite values, solver errors or mismatch. These circuits test the engine/interface, not the amplifier.

## Outputs
Version/log, qualification netlists and result JSON in `../qualification/`.

## Human check
Inspect failures and verify the selected runtime/library identity before using this route for circuit models.
