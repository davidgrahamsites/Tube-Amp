# Capacitor packaging: preserved electrical interfaces

2026-11-26. Owner: electrical interface research; integration owns adoption. Input: [v2 plan](v2.md), current 600R-1 circuit and power-film contracts. Output: node map and decision gates only. No circuit, selected part, native placement or safety qualification is adopted here. Human check: trace the four references and actual return wires on the eventual assembly, including unplugged service states.

## Actual node map

The authoritative [circuit contract](../../engineering/whole-amp/reverb-600/circuit.json) and a fresh, temporary KiCad XML export of the current native project agree on these endpoints. All four remain distinct references and retain their individual 50 µF values and 600 V minimum source requirement.

| Reference | Quantity | Pin 1 | Pin 2 | Existing functional relationship |
|---|---:|---|---|---|
| C12 | 1 | B_EARLY | GND | After R17, 10 kΩ from B_PRE; supplies R4/R7/R12/R15 first-stage plate feeds |
| C13 | 1 | B_PRE | GND | Same named node as C25; serves the B_PRE network |
| C25 | 1 | B_PRE | GND | After R35, 10 kΩ from B_SCREEN; B_PRE feeds R21/V3 and phase-inverter R29/R30 |
| C26 | 1 | B_SCREEN | GND | After L1 from B_MAIN; feeds output-screen resistors R41/R42 and downstream supply filters |

C13 and C25 are electrically parallel in the present circuit: their shared nominal node capacitance is 100 µF. This observation does not authorize replacing them with one component, moving their return takeoffs arbitrarily, or combining B_SCREEN/B_PRE/B_EARLY. The source still uses polarized capacitor symbols; film adoption must eventually reconcile symbol/package metadata without changing endpoints.

For each reference the same two **unselected** package alternatives apply: Panasonic EZPV60506MTC, 50 µF/600 V, maximum body 58 × 26 × 41 mm; CRC FC6136, 50 µF/900 V, maximum body 58.5 × 36 × 51 mm. See the [Panasonic contract](../../engineering/component-selection/power-film/panasonic-contract.json), [CRC contract](../../engineering/component-selection/fc6136-fit-contract.json) and [package review](../../engineering/component-selection/power-film/review.md). Four physical leads do not imply four independent electrical terminals; exact terminal-pair assignment and insertion tolerance remain gates.

## Current loops and removable-bank seam

The raw rectifier reservoir is **C29/C30**, two series 220 µF capacitors, not these four film candidates. Its charging loop runs from one T1 HV winding end through D3/D4 or D5/D6, F2, C29/C30 and the controlled GND return to T1 CT. Keep that high-pulse-current loop local during power-board repacking. Downstream topology is B_RAW → S2 → B_MAIN → L1 → B_SCREEN → R35 → B_PRE → R17 → B_EARLY; T2's output-transformer center tap branches from B_MAIN before L1.

For A/B/C, draw both recharge and load-return loops for each filtered node. A short positive wire with a distant shared return is not a short loop. Record conductor lengths and loop geometry, common return impedance and where screen/load returns join the reservoir return. Keep pulse-current paths out of quiet preamp reference wiring. This is a circuit-specific engineering inference from the native topology and the general loop-inductance principle documented by [TI's power-loop guidance](https://www.ti.com/document-viewer/lit/html/SSZT632/GUID-FAB54C52-3C47-4214-9183-2948E90A51BC); its buck-converter example is not a numeric rule for this tube supply.

The [grounding contract](../../engineering/whole-amp/reverb-600/grounding-contract.json) prohibits intentionally carrying reservoir, heater or normal signal current through chassis. PE remains a permanent dedicated safety path; GB1 is the separate signal/chassis bond. Neither metal brackets nor mounting screws become capacitor returns. Preserve one logical GND with deliberate physical return paths; a new daughterboard does not authorize a general GND/PE interchange or a ground split.

B/C require an explicit connector pin map containing B_SCREEN, B_PRE, B_EARLY and their controlled return connections. Do not assume one common return pin is adequate merely because all returns are named GND. Qualify the chosen conductor/contact arrangement for operating, charging and fault current, voltage, temperature, wire retention, mating access and exposed contacts in **both** halves. Identify accidental open-return and wrong-mate states. Support capacitor mass through the cassette structure, not headers or leads. This report specifies no pin count, connector family or wire gauge without those inputs.

## Discharge and service states

The existing R501/R502 series path discharges the raw reservoir but is upstream of S2; opening standby removes that path from the downstream filters. However, downstream discharge is **not absent**: B_SCREEN → R506 (220 kΩ) → HREF → R507 (39 kΩ) → GND remains in the source, with C505 on HREF and the four filters coupled through R35/R17. Tube loads and S2 state change the decay. No single-capacitor RC timing claim represents this network.

A disconnected capacitor-only bank can lose those discharge paths. Before choosing B/C, document the charged assembled, powered-off, standby-open, partially disconnected and completely removed states; identify which resistive paths remain on each side. Set the allowable residual voltage and service interval from the applicable requirements, then calculate worst-case decay using capacitance/resistance tolerances and verify it on hardware. Specify accessible test points and a controlled discharge procedure before touching or unmating. An additional bleeder would be a separately reviewed circuit change, not an assumed packaging detail. Do not add one in this study or claim the current arrangement meets a service time.

Panasonic's handling precautions warn against sudden charge/discharge and specify resistance of at least 2 kΩ for that operation. Treat this as a candidate-application/handling gate, particularly for C26 after the choke; it is not permission to insert a new resistor into the amplifier. Clarify compatibility of actual startup/standby pulses before selection. [Panasonic R9, p.23](https://industrial.panasonic.com/content/data/CP/PDF/ezpv_je.pdf).

## Voltage, thermal and insulation gates

For **each** node, establish maximum DC, ripple peak and spectrum, startup/no-load/standby transients and relevant fault stress under the intended 120 V/60 Hz and 220 V/50 Hz conditions, transformer regulation and component tolerances. The 600 V source requirement and 900 V alternative rating are not measured operating voltages. Assess capacitor RMS current and self-heating in the final placement. Panasonic's 19.1 A figure is at 70°C/10 kHz; its voltage derating above 85°C, case-temperature limit, ripple-voltage limit and neighboring heat sources still apply. Its 10 mm neighbor recommendation concerns heating, not an HV insulation distance. Lead-root forces and fixing-resin compatibility also require checks. [Panasonic R9, pp.3, 21–24](https://industrial.panasonic.com/content/data/CP/PDF/ezpv_je.pdf).

Build an insulation matrix for each unlike-node pair and each node to PE-bonded metal, accessible parts, nearby low-voltage circuits and any floating hardware. Include terminal bends, solder protrusions, underside copper, connector contacts, fasteners/washers, brackets and support surfaces in every service orientation. Record working RMS/DC and peak/transient voltages, insulation function, environmental pollution, material group/CTI, altitude, tolerances and any claimed solid-insulation system. Manufacturer component withstand tests do not establish this assembly's distances; neither solder mask nor an unspecified plastic spacer is automatically a qualified barrier.

Select the applicable product requirements and edition before extracting distances. The [IEC 60664-1 consolidated publication](https://webstore.iec.ch/en/publication/107319) is an insulation-coordination reference; its official [scope](https://webstore.iec.ch/en/publication/59671) covers clearance, creepage, solid insulation and testing. This research did not acquire or review its full normative tables and does not determine product certification applicability. [TI's reference calculator](https://dev.ti.com/gallery/view/Isolation/creapage_and_clearance_calculator/ver/1.0.0/) shows why working voltage, pollution, insulation/material class, impulse conditions and altitude are separate inputs; it is not an approval or a replacement for the applicable requirements.

Unresolved voltage/environment/insulation inputs block released spacing and final populated fit. Preliminary A/B/C views may retain explicit unknown separation parameters, but cannot score unqualified empty space as feasible. Record the resulting justified requirements in native rules and the mechanical envelope only after review, then check the populated assembly and required physical insulation/bond tests.

## Verification receipt and handoff

Read-only check used the installed KiCad CLI's documented `sch export netlist --format kicadxml` command, writing into an automatically removed temporary directory. All eight capacitor endpoints above matched the source; native discharge-path endpoints also corroborated the stated paths. SHA256 comparison of files in the native `cad/` directory before/after export was unchanged. No simulation, ERC/DRC rerun, energized measurement or fit verification is claimed.

Source identities at inspection:

- `reverb-600/circuit.json`: `db5b9a017341f2fd2177c22abc38ab8601df6684107af37d732cf3f0933b756a`
- `reverb-600/cad/05_supplies.kicad_sch`: `6b2712d4db26559e9aa2af7dfb5bfb99851e0622be72759492e570365086d547`
- `reverb-600/grounding-contract.json`: `78c78abd2fc688f94eb134d98e1f1d9f9ea3823169abf17f83cab42701c706b6`

Next integration action: carry this reference map into the common A/B/C comparison; make disconnected discharge-path retention and insulation inputs explicit holds. A remains the lowest-interconnect baseline, not a proven fit. Only this research file was authored by this worker; shared registers and final plan integration belong to the parent owner.
