# K3 fast-clamp candidate — bounded design checkpoint

Owner: control-switching integration. Task: replace the slow diode-only release assumption with a sourceable clamp candidate; lower the raw-warning threshold and rerun the failed low-line/endurance cases. Inputs: native baseline1d005196, VAL-051/052/053 and fast-clamp-contract.json. Outputs: tools/fast_clamp.py, tools/check_fast_clamp.py and results/fast-clamp. Done condition for this checkpoint: reproducible coil/supply evidence, retained failures, native preservation, source identity and explicit next integration gates. Estimated effort: one bounded research/calculation/simulation checkpoint. This is not the six-scope completion gate.

## Proposed circuit

Use **ST SMBJ16A-TR**, cathode to K3 driver drain/COIL_REV and anode to driver-source ground. Remove **both** existing ordinary K3 flyback diodes D341 and D342 in the candidate; leaving either parallel coil clamp defeats the higher release voltage. The short local TVS/driver return loop and coil harness become explicit placement/routing requirements. The board files have not been changed.

The clamp holds the drain above the positive coil supply during turnoff, dissipating coil energy faster. Unlike a TVS directly across the coil, this connection also draws energy from the held supply while the current decays; the calculation includes that contribution. Coil current is not a model of mechanical contact closure.

The accompanying raw-warning trial uses2.94kΩ/1.01kΩ/1MΩ, changing the former3kΩ upper divider resistor. All reservoir, load, transformer, temperature and tolerance sensitivities remain those of VAL-053, including10000µF positive reservoir,6000µF post-test sensitivity and5mA leakage allowance. Existing REF5 bleeder6.8k remains a trial, not a native change. The preceding failed3kΩ comparison is preserved.

## Manufacturer and sourcing evidence

[ST current datasheet](https://www.st.com/resource/en/datasheet/smbj170a.pdf), DS1283Rev14April2026, was read online. The retained distributor-hosted original STPDF is **Rev12April2021**; its SMBJ16A table/formulas match the current web table. Its exact bytes and source are hashed in results/fast-clamp/source-observations.json. No mislabeling of the retained revision.

[Chinese LCSC listing](https://item.szlcsc.com/144979.html): STSMBJ16A-TR/C133672/SMB(DO-214AA); November25 raw page fields stock8873, minBuyNumber1, convesionRatio5. Structured offer¥0.7304 is not a confirmed small-quantity price. Domestic courier policy gives a Shanghai sourcing route; delivered cost and availability remain checkout-dependent. No order or supplier contact occurred.

The part has16V stand-off, safely above the screened12.6V coil supply. The cold minimum breakdown calculation uses the1mA test point and maximum positive temperature coefficient. Below1mA the timing calculation deliberately uses a zero-reverse-voltage exponential tail rather than extending the published breakdown minimum down to zero current. Hot maximum voltage uses both published current/clamp equations and150°C. The2V transient-overshoot allowance remains an allocation requiring actual layout/harness verification, not a measured bound.

## Results and limits

The24 coil cases give a worst5%-current time of **7.446ms**, compared with13.947ms for the preceding ordinary-diode screen. The hot current/clamp formula peaks at21.834V, leaving6.166V below the30V driver limit after the allocated2V overshoot. Screened clamp energy including the conservative tail is at most1.293mJ. These calculations are not thermal qualification or a MOS switching waveform guarantee.

All32 rerun brownouts have positive modeled enable/timing margins. Minimum healthy enable margin is **163.49mV**; minimum conditional mute reserve is only **0.480ms**. Half-step worst-case timing agrees within0.1ms. This clears the particular simulated low-line failure, but the remaining timing reserve is thin and depends on the unverified5ms contact/logic allocation. Keep qualification false.

The independent audit integrates coil current numerically, compares two coil extremes in SPICE at two timesteps, retains a negative control with an ordinary diode left in parallel, checks source/input hashes, and confirms native files unchanged. The completed audit is clean:24 numerical integrations (maximum timing discrepancy0.691µs), four SPICE runs, an ordinary-diode negative control returning13.940ms, three corruption controls, and91 unchanged native/source CAD identities. See checks.json for receipts; a passing audit verifies this evidence, not the assembled amplifier.

## Next concrete work

1. Combine the selected rail, AC-loss and raw-warning inputs with the real REF5/inhibit/reset network; check startup, reference-off backfeed, loading, hysteresis and short pulses. The existing separate-model assumptions are not yet an integrated control schematic.
2. Resolve the thin margin through that complete timing budget and actual relay suppression/contact characterization. Do not silently enlarge capacitors or treat current decay as contact closure.
3. Select exact sourceable resistor/socket-carrier/TVS footprints, then adopt with readable schematic, netlist/ERC/DRC and assembly checks. Route the local clamp return away from audio ground paths and account for both removed diodes.
4. Resume the three-board populated chassis/harness fit; body/reach dimensions of the drill remain missing. All six build scopes remain incomplete.
