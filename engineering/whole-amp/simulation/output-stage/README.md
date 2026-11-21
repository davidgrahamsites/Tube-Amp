# Isolated EL34 screen-resistor experiment

2026-11-12; `tools/check_output_stage.py`; ngspice45.2 through KiCad10.0.6 Python. Generic unmodified Duncan/Munro6CA7 model, ideal400V plate and screen sources,-40V bias,40Vpeak complementary1kHz grid signals, ideal7.6k:8ohm transformer with100ohm winding resistances. Forty milliseconds completed; averages taken over last10ms. These are diagnostic conditions, not a complete amplifier or chosen-JJ validation.

|Each screen resistor|Screen A/B W|Resistor A/B W|Ideal load W|
|---|---|---|---|
|1k|9.787/9.801|2.874/2.885|44.481|
|2.2k|5.622/5.625|2.419/2.424|38.213|
|4.7k|3.080/3.081|1.800/1.801|28.850|

JJ EL34 manufacturer's limiting screen dissipation8W is the comparison reference: https://www.jj-electronic.com/images/stories/product/power_tubes/pdf/el34_e34l.pdf . Generic model behavior does not establish purchased-tube safety or delivered output power. Direct stiff grid drive does not reproduce blocking distortion or the actual phase inverter; full-amp comparison is required. Neither value is selected for construction yet. Larger screen resistors affect output and tone; manufacturer power derating and surge limits must be checked against full-amplifier results.

Measurement correction: ngspice does not expose `i(b.xv5.ba)` by default. Initial measurement failed after transient completion. Corrected script computes conduction plate current from the unchanged model's exact equation `1.86e-3*V(xv5.cc)` (and tube6 equivalent), rather than subtracting screen/grid/capacitive currents from cathode sense current. No model coefficient was modified.
