# Transformer and feedback diagnosis — 24 November 2026

Owner: electric integration. Authority: FB-112. **No compensation change adopted; fabrication remains held.**

## Task card
Inputs: electric-guitar-amp checkpoint ea77e662c6cf801690a0636259f917fad01ad92c, current 4.7k screen-resistor circuit, retained generic tube models, actual native PCB files and measured cabinet register. Outputs: independent magnetic-parameter fixture, return-ratio/compensation comparison, amplitude and HF-resolved burst tests, native board geometry and FreeCAD fit diagnostic. Dependencies: exact China-source transformer, parasitics/load response, populated packages and mechanical datums. Owner: integration; estimated effort one bounded engineering pass. Done for this checkpoint: separate numerical and physical uncertainties with reproducible evidence; preserve blocks. Exact transformer/compensation selection and full populated fit remain subsequent work. Drill-tool envelope is deferred by the user until November25, not assumed.

## Findings and disposition
The earlier 40H-per-half, k=.995 model corresponds to approximately159.6H full-primary open inductance and **1.196H full-primary shorted-secondary inductance** in its three-winding matrix. Changing L and a common k changed both effects together. It is retained as an extreme sensitivity case, not evidence that a real transformer has those parameters.

The new fixture separates full-primary magnetizing inductance, series leakage, winding resistance, a lumped primary capacitance and output load. Eighteen independent terminal impedance measurements verify the requested open/short inductances. The matrix remains a simplified model: no saturation, losses versus frequency, winding asymmetry, distributed capacitance, actual speaker impedance or complete supplies. Its ideal proportional 4Ω feedback tap does not model tap loading/impedance. The 10/40/160H,5/20/80mH and50/250/1000pF values are sensitivity assumptions, not supplier specifications.

Return ratio T is measured by replacing the existing unilateral ideal tap source with a1V AC injection at OT_4, zeroing other AC stimuli and preserving the DC point. With the sign convention T=−Vspeaker/√2, the independently measured transfers satisfy Hclosed=Hopen/(1+T) in all **83 AC cases**. DC points are preserved. This validates the measurement in this fixture; it is not a general physical loop-breaking method for a loaded transformer tap. All unity crossings and negative-real crossings are retained. The reported unsigned angular distance is not a signed phase-margin certificate; negative gain margins explicitly reject a candidate. No simple one-crossing criterion is used to approve every case.

| Comparison | Result | Disposition |
|---|---|---|
| Earlier extreme transformer at20kHz | Small drive THD1.29%; historical larger drive41.12% | Strong amplitude dependence; the old41% result alone does not prove small-signal oscillation |
| Independent nominal assumption:40H/20mH/250pF/.2Ω secondary | At20kHz, small drive THD0.078%; larger original drive4.734%, about12.28W fundamental | Better behavior in a different assumed transformer, not a hardware fix or new25W rating |
| Existing C22=47pF;80mH/250pF; Presence fraction0 | HF peak17.81dB; gain margin2.77dB | Reject as robust design envelope; actual transformer must be characterized |
| C22 increased to470pF | High-leakage peaking suppressed, but up to2.72dB loss at5kHz for tested Presence settings | Not adopted: substantial voicing tradeoff |
| Add47pF across R31 | High-leakage/Presence0 gain margin14.62dB, downward unity crossing about36.86° from−180°, peak5.87dB | Burst decays, but margin/peaking still inadequate for a blanket approval; not adopted |
| Add220pF across R31 | High-leakage/Presence0 negative gain margin−0.737dB | Rejected; HF-resolved transient confirms oscillation |

The protection acceptance matrix from the preceding checkpoint remains a finite stress result at its recorded parameters. This pass does not extend that claim to all new transformer assumptions or compensation candidates. Current native C22/R31 and all block interfaces remain unchanged.

## Treble requirement added during this checkpoint — FB-113
The user explicitly values treble for occasional acoustic-guitar use through this electric build. This applies here without replacing the electric architecture or assuming a particular acoustic pickup, added tweeter or flat20kHz specification. Compare changes against the matched existing C22=47pF/R31 baseline, not only against a normalized1kHz curve.

`results/feedback-treble-comparison.csv` contains48 matched comparisons across the tested20/80mH and Presence0/.5/1 settings. `feedback-treble-summary.json` pins its input/factory hashes. Ranges below are changes from the matched unchanged circuit, not speaker acoustic response:

| Experimental change |5kHz change |10kHz change |20kHz change |
|---|---|---|---|
| C22=470pF |−2.97 to−0.79dB |−6.64 to−2.38dB |−10.25 to−5.10dB |
| C22=100pF |−0.21 to−0.04dB |−0.77 to−0.12dB |−1.85 to−0.29dB |
| Add47pF across R31 |−0.10 to−0.05dB |−0.41 to−0.04dB |−1.66 to−0.02dB |

The larger C22 change is not adopted; the smaller options also remain experiments because treble retention alone does not meet the worst-case stability requirement. The user has not specified a numeric tonal limit. Actual pickup loading/clean headroom, RETURN and selected speaker response remain separate checks. Prior guitar names do not establish pickup technology. This priority must carry into speaker choice rather than being treated as an electronics-only result.

## Numerical failure control
Five additional full0.5s diagnostics complete. However, their1kHz burst tests use a maximum10.42µs step, which is unsuitable for establishing stability around65kHz. They are retained and explicitly **excluded from HF stability acceptance**. Merely reaching the end of a transient is not enough.

A separate10ms local burst test uses156.25ns maximum steps, then78.125ns for refinement. For the deliberately rejected220pF candidate, the late speaker oscillation reaches0.9343V peak and0.9355V peak respectively (about0.12% difference). The10.42µs coarse-step run hides this, reporting only1.72µV late peak. The47pF candidate decays to below1µV in the corresponding fine-step local test; that bounded result does not override its insufficient worst-case margin or qualify power-up, clipping recovery or faults. Generic models and Gear integration still need correlation with measured hardware.

`results/feedback-audit.json`: **283 checks pass**, covering provenance,83 AC comparisons, retained decks, five long diagnostics and expected negative-control behavior. This means the evidence is internally consistent, not that every tested circuit passes. [Plots](results/feedback-diagnosis.pdf) show the parameter sensitivity and timestep failure control.

## Transformer selection and PCB consequences
[China sourcing and required transformer data](../../component-selection/evidence/output-transformer-screen-2026-11-24.md) separates an actual domestic listing from a qualified part. Mable MATR0233 advertises selectable4–6.6k primary impedance, so it is not a documented7.6k replacement. No unsupported MPN, price quotation, mechanical envelope or compensation value has been locked. No supplier contacted and no purchase made.

Obtain or measure exact winding/tap ratio and phase, full/half-primary DCR and open/short inductance with terminal/test conditions, frequency/phase response under expected load, winding capacitance or a measured response fit, DC/AC current and insulation ratings, and mounting/lead envelope. Recheck both mains/supply operating corners and fault/clipping limits. Low-frequency transformer testing must cover the intended guitar range and saturation;25W nominal does not cap clipped power. The preceding stress matrix reaches approximately48W in an assumed high-rail overload.

Keep R31/R32/C20/C21/RV9 in the Output/Presence block; keep the speaker-feedback harness away from input/grid wiring and preserve its intended return. Reserve access to existing C22/R31 for qualification, but do not add a guessed snubber or route around an unselected part. Current routing remains unfinished. No new PCB DRC run is claimed: native board bytes match the prior checked checkpoint, so its234 unconnected items/68 provisional courtyards remain applicable.

## Mechanical continuation
[FreeCAD diagnostic and next repack](../mechanical/review/board-fit-review.md) uses actual PCB outlines and16 nominal3.2mm NPTH mounting holes. Native/STEP solids, volumes, positions and rotations are verified. This is a current-four-board diagnostic, not the desired final three-board layout or a chassis ready to fabricate. Construction/flange allowances are trial inputs; drill clearance remains pending. Fixed cabinet supports and independent wooden rear-cover removal remain requirements.

## Sources and reproduction
- [TI SLOA020A](https://www.ti.com/lit/an/sloa020a/sloa020a.pdf), sections2 and4: feedback equations and stability analysis. Applied here through explicit fixture checks, not copied op-amp component recommendations.
- [Hammond1650F manufacturer data](https://www.hammfg.com/files/parts/pdf/1650F.pdf):7.6k/25W reference with separately specified DCR and open/short inductance test conditions. Reference evidence only; not selected or assumed stocked in China.
- [ngspice manual](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf): AC and transient analyses and integration controls. Actual runtime remains45.2.

From the workspace root run `python3 engineering/whole-amp/effects-loop/tools/feedback_checks.py`, then `feedback_sweep.py`, `feedback_transient.py`, `feedback_ringdown.py` and `audit_feedback.py` from that same tools directory path. `plot_feedback.py` renders retained data. Long workers have600s wall limits; failure/timeout is explicit. Sources and model coefficients are unchanged. Source/factory/deck hashes accompany evidence. Next work is exact magnetics data and a qualified compensation envelope, followed by populated three-board repacking/connector assignment and routing; no blanket stability or build-ready claim.
