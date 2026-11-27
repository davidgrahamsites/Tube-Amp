# Renegade amplifier design journal

This journal follows the engineering work toward a physical Renegade tube-amp build. It is a narrative index for a later design guide and long-form build series. It is derived from the canonical requirements and evidence; it does not replace them or serve as another requirements register.

## How to read it

Read each chapter alongside its linked validation record, review, contract, and result files. Dates describe the source checkpoint. Labels distinguish user authority, engineering analysis, native implementation, simulation, and physical evidence. A passing script or CAD check is not a physical test. An option discussed or bounded is not an adopted design.

## Chapters

- [VAL-070–072: packages, fit evidence, and rating coverage](chapters/01-packages-and-rating-coverage.md)
- [VAL-073–074: regulator contacts and rectifier integration](chapters/02-contacts-and-rectifier-integration.md)
- [VAL-075: heater divider fault boundary](chapters/03-heater-divider-fault-boundary.md)
- [VAL-076: shared heater-reference compatibility](chapters/heater-interface-boundary.md) — diagnostic checks passed; engineering qualification remains false.
- [HD-003: corrected heater-reference candidate](chapters/heater-reference-correction.html) — 39 kΩ reference candidate; normal margin only, no fault qualification.
- [HD-004: preamp supply load](chapters/preamp-supply-load.html) — passive-feed and behavioral-regulator screen; no regulator adopted.
- [HD-005: preamp ceiling feed](chapters/preamp-ceiling-feed.html) — conditional feed and dropout screen; semiconductor acceptance remains open.
- [HD-006: preamp pass-stage model](chapters/preamp-pass-model.html) — model translation and fault boundary; no circuit qualification.
- [HD-007: series-pass protection screen](chapters/series-pass-protection.html) — sampled device-short cases; regulator-short protection remains open.
- [HD-008: absolute output protection authority](chapters/absolute-protection-authority.html) — forced-on actuator screen; no automatic protection adopted.
- [HD-009: precision detector and setpoint](chapters/precision-detector-setpoint.html) — 512 static cases; 267.11 V remains a candidate.
- [HD-010: large-signal setpoint comparison](chapters/preamp-setpoint-headroom.html) — paired 1 kHz models; no clean-power or supply-dynamics qualification.
- [HD-011: monitor supply and fault hold](chapters/monitor-fault-hold.html) — 182 scoped evidence checks pass; engineering qualification remains false.
- [HD-012: monitor reset floor and startup boundary](chapters/monitor-reset-floor.html) — reset range is positive in allocated endpoints; startup and hardware remain unqualified.
- [HI-004: harness header datum and mated envelope](chapters/harness-mating-datum.html) — nominal geometry checks pass; no actual placement or assembled-fit approval.
- [HI-005: pot harness wire reserve and service slack](chapters/pot-harness-wire-reserve.html) — 12.70 mm nominal reserve; no placement or service-fit approval.
- [HI-006: pot harness DC fault screen](chapters/pot-voltage-fault-screen.html) — 1,050 normalized cases plus 12 generic-tube probes; exact pot and insulation limits remain open.
- [HI-008: Reverb pot connector candidate](chapters/reverb-pot-connector-candidate.html) — CU-003/VS-002 candidate has zero ordinary DRC violations/opens; C607 ground gap is nominally 0.85 mm, while 47 conditional dry-path reports and electrical, insulation, fabrication, and fit limits remain. FB-173 clarifies that the 1.5× target is finished width, not a current rating.
- [CB-002/003: composite recovery stage feasibility and solver follow-up](chapters/composite-return-feasibility.html) — 18 design cases and 20 operating-point diagnostics complete; solver guidance recovers valid points but does not qualify startup, devices, or hardware.
- [Bench planning: test equipment and requirements](chapters/test-equipment-plan.html) — staged HTML guide and offline export; no equipment models approved and no physical tests claimed.
- [FB-143–145: capacitor-bank fit and tool access](chapters/capacitor-bank-and-driver-access.html) — standalone and combined five-pass reviews complete; no adoption.
- [FB-146/147: lower power packaging and Alien Method](chapters/bottom-power-packaging.html) — four review cycles complete; no lower allocation adopted.
- [FB-148: current power-packaging calculations](calculations/current-power-packaging.html) — step-by-step KaTeX-ready derivations; historical math remains to backfill.

## Backfill status

The entries above are an initial recent-history tranche, not a complete project history. See [HANDOFF.md](HANDOFF.md) for the queue and the next append/update procedure.
