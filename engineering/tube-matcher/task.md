# TM-001 — EL34 / 12AX7 benchtop matcher, revision 0.1

Updated October 4, 2026.

- **Owner:** root agent, single editing owner; no delegation.
- **Inputs:** user requested a plug-in matching/binning instrument, BLE to macOS, or Raspberry Pi with integrated bench display; user corrected EL84 to EL34. Amp handoff and source inspection establish V4 phase inverter and two EL34 output tubes. Manufacturer sources are registered in `sources.md`.
- **Outputs:** system/electrical interface design, socket maps, measurement sequences, proposed limits, bin/pair rules, display and BLE design, mechanical constraints, calculations and brain capture.
- **Dependencies:** no purchase approval needed for this design. Exact amp operating points and selected tube manufacturer variants are unavailable. They affect amplifier-specific profiles, not the generic comparison architecture.
- **Automation:** Python 3.13.2, standard-library calculations, profile consistency checks and synthetic pairing checks. No hardware control, firmware, circuit simulation, KiCad capture, ERC/DRC or CAD fit validation in this revision.
- **Human evidence:** tube identity; intended maker/variant datasheets; bench resources; selected component drawings; reviewed schematic and protection design; calibration and actual tube measurements.
- **Done condition:** internally consistent, source-linked concept with explicit interfaces and uncertainty rules, checked calculations, and documented next gates. Not a manufacturing release.
- **Estimated downstream effort:** rough engineering allowance: 2–4 working days schematic/part review, 2–4 days board/layout/enclosure work, 3–7 days firmware/UI, 3–7 days assembly/calibration/fault testing. Work overlaps; procurement and corrections are additional. Confidence low until actual bench resources and selected parts are known.
- **Stopping boundary:** complete this system-design revision; do not invent supplier footprints, claim hardware accuracy, or release an unreviewed HV build.
