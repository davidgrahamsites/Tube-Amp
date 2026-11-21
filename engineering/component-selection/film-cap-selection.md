# KYET polypropylene capacitor selections — November 12

Select these exact metallized polypropylene parts. The supplier's manufacturer approval sheets identify the exact MPN, dimensions,5% tolerance and630VDC rating. This is an electrical selection; final cabinet/PCB fit remains unconfirmed.

| References | MPN | Value | Qty | LCSC SKU | MOQ | Unit CNY at MOQ |
|---|---|---|---:|---|---:|---:|
| C8,C11,C16,C17,C19,C23,C24 | KP223J2J1001 |22n|7|C390074|10|0.293|
| C3,C20,C21,C601 | KP104J2J1006 |100n|4|C390130|10|0.2693|
| C4,C6 | KP473J2J1001 |47n|2|C390076|10|0.3033|
| C10,C14 | KP105J2J2002 |1u|2|C390157|5|0.864|
| C7 | KP684J2J1502 |680n|1|C390149|5|0.7247|

Domestic observations are dated November11; links and exact stock counts remain in candidate-register.json. MOQ spend is¥16.60 before shipping, including spares.630V is needed for the coupling positions; the two1u and680n cathode positions do not require that high voltage, but these stocked film choices are inexpensive. Their larger bodies must be included in layout/fit review; they are not interchangeable with small50V footprints.

Manufacturer evidence: evidence/KYET-<MPN>.pdf/.txt. The sheets specify continuous rated-voltage operation from-40 to100°C, dielectric loss≤0.1% at1kHz/25°C, and require **DC plus AC/surge peak** to stay below the rating. This does not establish audio-band ripple-current or repetitive-pulse limits. Retain them away from tube/screen-resistor heat and verify local temperature.

| MPN | Nominal W×H×T mm (each±1) | Pitch±0.5 mm | Lead diameter±0.05 mm |
|---|---|---:|---:|
| KP223J2J1001 |12×10×4.5|10|0.6|
| KP104J2J1006 |12×11×5.5|10|0.6|
| KP473J2J1001 |12×11×5.5|10|0.6|
| KP105J2J2002 |22.5×16×8.5|20|0.8|
| KP684J2J1502 |17×14.5×8.5|15|0.8|

check_film_caps.py checks all16 references in both nominal channel operating points:32 checks pass, highest DC voltage265.501V. These are nominal400V/-40V generic-model results, not high-line/startup/overdrive qualification. Existing supply peak510.31V alone is not the voltage across every coupling capacitor; the opposite terminal and transients must be included. Do not claim full630V surge margin from a ground-referenced supply peak.
