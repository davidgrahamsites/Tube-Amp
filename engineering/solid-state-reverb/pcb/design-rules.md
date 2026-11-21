# Low-voltage reverb PCB design basis — v0.4

Scope: 160 x 100mm daughterboard, 2 copper layers, 1.6mm FR-4, 1oz copper, plated through holes, solder mask both sides. No mains, heater or B+ routing. Components are hand-soldered through-hole parts. Four 3.2mm NPTH mounting holes; insulated standoffs, at least 8mm board underside clearance to chassis as an assembly target. Board outline remains provisional for actual chassis fit.

## Electrical and fabrication constraints

- Maximum normal rail difference 30V (+15 to -15). No high-voltage insulation claim: C601's 630V coupling rating is a component rating, not a certified isolation barrier.
- Trace minimum 0.30mm, copper clearance 0.25mm; GND zone clearance 0.30mm. These exceed JLCPCB's published standard 1oz fabrication minimums (0.10/0.10mm) and leave hand-prototype margin. Source: https://jlcpcb.com/capabilities/Capabilities (checked 2026-11-11).
- Vias 0.8mm diameter / 0.4mm drill, annular ring 0.2mm. Edge copper clearance at least 1.0mm. Ground pour inset 1.5mm; mounting holes have additional copper exclusions.
- Design rail-current allowance 50mA per audio rail; relay coil 12.5mA nominal. At 0.30mm x 35um, 100mm copper resistance is approximately 0.16ohm: 50mA gives about 8mV and 0.4mW. This is a voltage-drop arithmetic check, not a thermal test.
- T3/regulators/rectifiers and logic board stay outside this audio board. Route high-voltage and mains harnesses in a separate chassis region, never through/over this board. Final assembled separation requires the actual chassis design.

## Layout and returns

Tank return/recovery occupy the opposite side from relay and power harness. Buffered send and mix are separate groups. JR3 input uses a shielded cable and short recovery leads. Six local 100nF decouplers plus two rail bulk caps support the three ICs. Bottom GND copper joins the routed reference network; the amplifier gets one intentional audio/chassis bond, never multiple accidental bonds via jacks, tank or board mounting.

K3 coil current returns through COIL_REV to its driver, not via the sensitive board ground. Twist its +12V/COIL_REV harness pair; keep its loop away from JR3. D341 flyback remains in the controller; verify the actual harness transient and relay pop before acceptance. JR2 tank-driver current and recovery return share board reference copper; inspect residual hum with the actual tank and transformers.

## Verification

Use native KiCad DRC with schematic parity plus the pin-partition comparison in `../validation/board-parity.json`. Resolve copper, courtyard, hole and silkscreen findings; preserve reports. Export Gerber/drills only from the checked board; exports are engineering previews until body/lead sizes, cabinet fit and circuit qualification gates close. No supplier upload or order is authorized or performed.

Unresolved: exact film-capacitor body sizes at the chosen voltage, selected header retention/mating hardware, tank transfer/headroom, op-amp overdrive under maximum preamp drive, regulator/heatsink integration, acoustic coupling and in-chassis stability. A DRC pass does not close these.
