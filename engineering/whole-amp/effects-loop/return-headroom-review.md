# RETURN headroom experiment — 23 November 2026

Owner: electric integration. Authority: FB-102 / DEC-014. **Not qualified; no RETURN circuit or PCB substitution adopted.**

## Fault and test boundary

The completed heavy-overdrive matrix reaches internal FX_SEND extrema of −135.094/+97.777 V. This is one generic-model fixture envelope, not an all-setting hardware maximum. A low-voltage unity RETURN buffer cannot reproduce it. A low-impedance return also changes the existing passive wet mix; voltage swing alone does not solve that interface.

Tested a three-OPA462 supply-bootstrap arrangement derived from [TI SBOA510, section 2](https://www.ti.com/lit/an/sboa510/sboa510.pdf). Two amplifiers move the third amplifier's supply rails with its output. The experiment uses ideal fixed rails ±166.6 V and ±173.4 V, gain 100, a 340 kΩ / 100 pF load and 1 kΩ output resistor. It is not a power-supply design. TI's example and our gain/load are different. The [OPA462 datasheet](https://www.ti.com/lit/ds/symlink/opa462.pdf) remains the component-limit reference.

Model: TI OPA462 final 1.3, 2022, unmodified five-pin macro-model from `https://www.ti.com/lit/zip/SBOMAV9`. SHA-256: `66a115944b72948befa0c0c03a4d7123a80253c1e706fca587686838b66ea4a8`. The model is fetched into temporary local storage, not redistributed here. Exact decks, logs, case metrics and summary are in `results/return-real-*`. ngspice 45.2 was used.

## Results

Eleven acceptance cases attempted: nine completed and two failed. A completed case is not necessarily an electrical pass: the fixed-supply comparator clips badly.

| Configuration | Stimulus | Result |
|---|---|---|
| One amplifier, ±85 V supplies | 1 kHz, 135.1 V requested peak | Clips near ±84.7 V; approximately 17.1% model THD; rejected |
| Three-amplifier bootstrap, both supply corners | 82.4 Hz, 135.1 V requested peak | Completes; approximately 134.567 V peak at port |
| Same | 1 kHz, 135.1 V requested peak | Completes; approximately 134.554 V peak |
| Same | 5 kHz, 135.1 V requested peak | Completes; approximately 134.275 V peak |
| Same | 1 kHz, 150 V requested peak | Completes; approximately 149.393 V peak |
| Same | 20 kHz, 135.1 V requested peak | Both fail with internal upper-amplifier timestep errors; no electrical result |

“Requested peak” is the source amplitude multiplied by nominal closed-loop gain. Input/output resistor losses mean it is not the delivered port peak. The 1 kHz / 150 V case shows margin over the checked 135.094 V negative excursion, but does not establish the full bandwidth or overload envelope. Minimum output-to-moving-rail margin is approximately 8.37 V in the low-supply / 150 V case. Maximum modeled main-amplifier supply span is approximately 173.4001 V. These checks do not replace rail, current, thermal or startup qualification. Very low model distortion is not a real audio-quality claim.

Initial bootstrap runs found invalid operating points. Explicit internal midpoint `.nodeset` guesses allowed finite, checked operating points without modifying the vendor model. Nodesets guide the solver; they are not clamps. Initial failures remain in the evidence. External output and moving-supply midpoint checks are mandatory in the factory.

## Failed-case diagnostics

At the 20 kHz low-supply corner, trapezoidal integration and tighter tolerances both still fail inside the upper amplifier. A 1 Ω series ESR experiment on the floating 100 nF bypass did not finish and was manually stopped after more than 60 seconds. A separate exponential 2 ms amplitude ramp also fails at approximately 112 µs. None counts as an acceptance pass or replaces the original failed cases.

`tools/return_diagnostics.py` preserves these deck substitutions and bounds future individual runs at 45 seconds. Earlier trap/tight/ESR receipts came from the same substitutions in a scratch runner; the ESR receipt explicitly records manual termination. The ramp is only a startup diagnostic, not a change to the acceptance stimulus. Exact diagnostic decks are retained.

## Decision and next work

Hold the bootstrap candidate outside the production CAD/BOM. Three high-voltage ICs, additional supply rails and an unresolved model fault do not yet meet this project's simple, low-cost objective. China-facing TI/LCSC pages are research leads only; stock, mainland small-order price and package fit are not qualified selections.

Next engineering step: establish the required clean and overload RETURN envelope with a physically valid output-transformer/load model and intended control settings. Compare a protected discrete high-voltage recovery stage at the existing interface against this bootstrap candidate. Preserve dry, spring-drive and wet transfers, relay functions and functional-block boundaries. No insertion-point relocation, additional tube or new supply is silently approved. Startup/shutdown, shorts, injected pedal voltage, isolation from tube DC, thermal limits and full integrated gain/mix checks precede native implementation.

Reproduce: `python3 tools/return_driver.py --fetch`, then `python3 tools/return_driver.py` from this folder. Individual cases are process-bounded at 45 seconds. Diagnostic example: `python3 tools/return_diagnostics.py ramp`. `tools/audit.py` checks evidence consistency, not hardware acceptance.

Human check: inspect the failed 20 kHz cases and compare delivered port voltage with the intended amp envelope. Do not infer build readiness from the aggregate audit.

November25 continuation: [supply/bypass diagnosis](return-supply-review.md) reproduces the original failures and records a different, unadopted50Ω rail-isolation fixture that retains100nF bypass. Ten regression cases and two refinements complete. The original evidence above remains valid for its unchanged topology; integrated RETURN, wet-mix, thermal/socket and exact China-sourcing qualification remain open.
