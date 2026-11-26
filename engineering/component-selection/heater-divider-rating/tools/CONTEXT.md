# Rating factory
Owner: heater-divider rating. Inputs: ../contract.json and hashed canonical source/evidence. Process: execute screen.py; use the existing ngspice runtime for independent RC checks. Outputs: ../results only. Human check: audit a corner using voltage division and V²/R; these scripts cannot establish actual cabinet temperature.

For the tube-interface boundary, interface_screen.py uses ../interface-contract.json and the existing whole-amp fixture. check_interface.py independently intersects per-terminal limit intervals and checks receipt/source/native hashes. Both write only ../results; neither selects tubes or changes the circuit. Human check: compare the exact sourced tube's heater-cathode definition with the conservative instantaneous interpretation before adopting a remedy.

HD-003: correction.py consumes correction-contract.json; analytical reference bounds and ngspice/audio adapters remain separate functions. check_correction.py independently enumerates extreme states and traces each cathode DC return to GND. Both write only ../results and preserve native source hashes. Human check: include the cathode return resistor when reviewing heater-to-cathode resistance.

HD-006: pass_topology.py consumes ../pass-contract.json and unchanged manufacturer model bytes, generates simulator-only adapters and writes ../results. check_pass.py independently checks terminal current balance, case coverage, model applicability and retained waveform/source receipts. Human check: never interpret numerical completion as qualified stability or operation beyond absolute ratings.

HD-007: series_protection.py owns dual-pass deck changes behind the frozen HD-006 deck adapter; check_series.py independently checks output current balance, minimum regulator current and the deliberately failing absolute-output probe. Outputs remain in ../results. Seeded DC solutions are not startup simulations.

HD-008: absolute_authority.py consumes frozen series/pass adapters and absolute-contract.json; check_absolute.py independently reconstructs DC current balance, actuator demand, coverage and detector-window arithmetic. Both write results only. Human check: forced control does not prove detection, timing, peak limits or real-part authority.

HD-009: detector_candidate.py coordinates threshold calculations, series-adapter DC runs and existing supply-adapter AC sweeps using detector-contract.json. check_detector.py reconstructs interval endpoints, coupled current balance, monitor reserve and native/model dependency hashes independently. Outputs are results only. Human check: ideal rail current balance and continuous control do not qualify a real supply, latch or fault transition.
