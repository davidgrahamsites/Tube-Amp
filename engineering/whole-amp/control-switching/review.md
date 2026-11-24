# Control switching checkpoint — 24 November 2026

Q1/Q2 are now AO3400A in the source circuit, native schematic and Control PCB. D333/D342 add local drain-to-+12 V suppression while retaining the remote relay diodes. Functional signal names and all unrelated board copper were preserved by the scoped edit. Independent preservation and native drill-export checks now pass; this remains an incomplete amplifier draft, not a fabrication release.

## Simulation evidence

The final driver screen completed 26 cases and six timestep-refinement runs. Its conservative MOSFET/diode surrogate, temperature-adjusted coil resistance and engineering harness-inductance sweep found a 31.03 V peak with remote-only suppression in the worst tested case, above the candidate MOSFET's 30 V rating. Adding the local clamp reduced the largest tested peak to 13.41 V. Refined peaks converged within 1%; steady-state KCL error was approximately 2 nA. This is bounded model evidence, not a measured transient rating: the diode model is generic, coil inductance is reference data, and the +12 V return is ideal. Final harness impedance, relay pickup/release and audible switching need validation. A further 13-run sensitivity screen includes finite positive-harness/feed inductance, 80µF bulk plus80nF ceramic capacitance, and0.05–2Ω bulk ESR. Decoupled cases peak at13.4665V; removing both local capacitors raises the tested peak to30.7778V. Limiting refinements converge within1%. These impedance/ESR assumptions are engineering sweeps, not measured or guaranteed bounds; simultaneous third-coil switching and regulator-loop dynamics remain excluded. Early switch-model and trapezoidal-integration pilots stalled or failed numerical checks; the retained final runs use tighter tolerances and second-order Gear integration.

The candidate TPS389001DSER supervisor remains unadopted. Ten nominal manufacturer-model runs completed, but the manual-reset case did not reapply the capacitor delay, contrary to the datasheet behavior. Fast rail collapse also crossed 4.5 V before reset asserted. These are unresolved model/application limits, not passing qualification. The original manufacturer model is retained unchanged. The threshold divider has little residual margin in the stated resistor-endurance sensitivity, and the reset edge requires conditioning before driving HC74 reset inputs. A removable supervisor carrier and its socket still require qualification.

## Native checks so far

The latest Control DRC has the same 13 existing violations and 84 unconnected items, down from 90. Existing routing is incomplete. The final schematic render was inspected for diode orientation, reference/value readability, notes and wire crossings. Manufacturer package drawings were visually checked for AO3400A G1/S2/D3 mapping and land geometry. Whole-amplifier fabrication readiness remains false.

The process-start outage was resolved on November24. Final native XML export and independent preservation/drill checks now pass. The six old TO92 holes are replaced only by four 1.2mm local-diode PTH holes and two 0.4mm drain vias; unrelated holes/slots remain unchanged. Source, coverage and board-plan entries were synchronized, including the prior R215 board-plan omission. See results/adoption.json for current native state; contract.json intentionally remains the frozen pre-adoption simulation input. Catalog/commit status is recorded in the handoff.

## Primary sources and purchasing limits

- [AOS AO3400A datasheet](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf) and [SOT23 package drawing](https://www.aosmd.com/sites/default/files/res/package/SOT23.pdf).
- [TI TPS3890 datasheet](https://www.ti.com/lit/ds/symlink/tps3890.pdf), [unmodified model download](https://www.ti.com/lit/zip/SLVMBN4), and [HC14 datasheet](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf).
- [Omron G5V-2 datasheet](https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v2.pdf) and [onsemi 1N400x datasheet](https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf).
- Domestic AO3400A C20917 and TPS389001DSER C1509297 retail listings were observed on 24 November. Exact supervisor divider/timing-capacitor domestic stock and current clamp-diode stock remain unverified. Distributor mainland delivery policy is not confirmation of an exact Shanghai address, freight or checkout availability.

## Next work

Finish this native checkpoint, then qualify the reset interface, removable adapters and actual supply-collapse behavior. Apply FB-117: IC sockets remain the default, with documented performance-based exceptions permitted; none adopted. All tubes retain proper sockets. Discrete relay MOSFETs are not substitutes for socket qualification of the ICs. Keep drill clearance pending the actual tool dimensions on 25 November. All six amplifier scopes remain open, especially the populated three-board chassis and exact Shanghai-sourceable parts.
