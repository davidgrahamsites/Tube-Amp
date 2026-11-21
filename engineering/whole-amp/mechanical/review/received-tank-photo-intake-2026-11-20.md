# Received tank and DT9205A photo intake — 20 November 2026

## Task card
Owner: integration agent. Inputs: six user photographs; current fit register; seller statement. Output: preserved source photos, attributed observations, Chinese glossary and meter-specific resistance procedure. Dependency: physical readings supplied by user. Automated operations: copy/hash verification, register update, catalog rebuild. Human check: identify sockets and report actual display readings. Done condition: all six photos retrievable, confirmed facts separated from unknowns, instructions delivered. Estimated effort: one short documentation session. No circuit change or energized test.

## Evidence and observations
Sources: [photo manifest](../evidence/received-tank-2026-11-20/manifest.json). Originals are unchanged.

- Photo 03 confirms model **M8EB2C1B**, second marking **R2610270015**. Serial/date format remains undecoded.
- Photo 01, viewed from the front as photographed: **left red RCA socket is stamped OUT; right white RCA socket is stamped IN**. Use stamped labels as authority when the tank is turned around.
- Photo 04 shows three long reverb springs and four short suspension springs supporting an inner assembly. Photos 02 and 04 show mounting flanges and pale grommets with metal eyelets. Material properties and dimensions are not established.
- Photo 05 shows separate RCA terminal boards, signal wires and return wires. Photographs alone do not verify input-shell isolation or output-shell bonding to the case.
- Photo 06 identifies an enhanced-version DT9205A manual-range multimeter. Red lead is in VΩ; black appears connected to COM. Check these markings physically before measuring. No resistance reading is shown.
- Seller-reported 600 Ω input / 2250 Ω output, medium decay, input insulated/output grounded, no lock, horizontal/open-side-down remain the provisional electrical design basis in the [canonical register](../fit-register.json). These are AC impedance claims, not measured DC resistance.
- No scale is present. Body dimensions, coil DC resistance, impedance frequency/level, recommended and maximum drive current remain unverified. Photos do not demonstrate working audio performance.

## Chinese labels visible on this meter
| Chinese | Pinyin | English |
|---|---|---|
| 增强版 | zēng qiáng bǎn | Enhanced version |
| 自动关机 | zì dòng guān jī | Automatic power-off |
| 全保护电路 | quán bǎo hù diàn lù | Full-protection circuitry (printed claim) |
| 电阻 | diàn zǔ | Resistance |
| 蜂鸣 | fēng míng | Buzzer / continuity beeper |
| 电容 | diàn róng | Capacitance |
| 直流电压 | zhí liú diàn yā | DC voltage |
| 交流电压 | jiāo liú diàn yā | AC voltage |
| 直流电流 | zhí liú diàn liú | DC current |
| 交流电流 | jiāo liú diàn liú | AC current |

COM means common; VΩ is the voltage/resistance socket. Ω means ohms; k means thousand; M means million. The protection wording does not establish suitability for live tube-amp or mains measurements. This task uses only the disconnected passive tank.

## Resistance measurement: perform now
1. Disconnect both RCA cables from the tank. Leave the amplifier and all power supplies out of this test. Support the tank by its case/flanges without pressing on the exposed springs.
2. Black meter lead into COM. Red meter lead into VΩ. Leave mA and 20A unused.
3. Select the yellow **2k** position in the **电阻** sector on the upper-left side of the dial. This is the resistance range, not a voltage or current setting.
4. Touch the probe tips together. Expect a reading near zero. Separate them again. This checks the leads and contacts.
5. Measure INPUT: locate **IN**, the white socket on the right in photo 01. Touch red probe gently to the metal contact inside its centre hole. Touch black probe to the shiny outer metal barrel of that same socket. Do not bridge centre and barrel with one probe or force the centre contact wider. Hold still until stable.
6. Record the exact display, decimal point and range. Do not assume the number is in plain ohms. If the display indicates overload/open circuit, first recheck contact; try 20k if necessary and report the selected range. An open-coil conclusion requires verified contact and a suitable range.
7. Repeat at **OUT**, the red socket on the left in photo 01: centre contact to that socket's own outer barrel.
8. Turn the meter OFF. Send: probe tips together = ___ (range ___); IN = ___ (range ___); OUT = ___ (range ___).

Do not measure IN to OUT for these coil tests. Do not substitute the painted tank case or nearby mounting rivets for the socket barrel. Each coil is measured separately. A normal result can be much lower than 600/2250 Ω because DC resistance and AC impedance are different quantities. Do not use these resistance readings to infer maximum drive current.

For later AC tests and source evidence, see [tank characterization plan](tank-characterization-plan.md). No bench result has yet been supplied.

## Subsequent user measurement report — 2026-11-20
The user reported shorted tips `000`, IN `.076`, OUT `.235`, all on the 2k resistance range. Converted results and conditions are now in [fit-register.json](../fit-register.json), under tank_received.electrical_measurements. This closes the earlier pending DC-reading request. No calibration, room temperature, shell-to-case test, AC impedance or current qualification was supplied.

These finite readings are consistent with continuity through both coil paths; they are not a complete tank serviceability test. Earlier simulation assumptions (56 ohm input / 200 ohm output) now require a new measured-resistance case. Keep unknown inductance and test frequency explicit; do not derive a verified inductance from supplier impedance without its frequency. Historical simulation results remain historical and unchanged by this intake.
