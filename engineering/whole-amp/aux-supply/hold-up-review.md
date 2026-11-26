# Auxiliary hold-up for advance relay muting

Owner: auxiliary-supply integration. Status: feasibility evidence, not native adoption or a purchasing choice. Baseline: `4d9c265cf332a89eb38b5b48a764804ab6264c96`. Task: determine whether the raw supply can provide useful advance warning before the audio rails lose their documented headroom, preserving the existing relay and functional blocks. Completion of this screen means a reproducible comparison and honest rejection boundaries; it does not complete the mute circuit.

The 25 VA reference fails the proposed 20 ms total detection/contact allowance at the low-winding sensitivity corner. Increasing capacitance alone to 6,800 µF does not resolve it. A lower-resistance 50 VA reference with the same secondary voltage and capacitance passes the sampled shutdown screen, but neither transformer is selected. The 25 VA Chinese listing is out of stock; no exact Chinese stocked route has been verified for the 50 VA reference.

## Contract and implementation seam

[Editable contract](hold-up-contract.json) owns the candidate regulator set, supply/load assumptions and test grid. [Primary results](results/hold-up/screen.json) retain 134 cases and four half-step checks. [Comparison](results/hold-up/comparison.json) retains 28 targeted 50 VA cases and one half-step check. Factories replace these outputs in place; they never regenerate CAD. [Evidence audit](results/hold-up/checks.json) checks arithmetic, flags, coverage, dependency hashes, independent discharge physics and preservation of 22 native files. Six deliberate corruptions must be rejected.

ST LM317T-DG for U4/U6 and LM337SP for U7 are candidate replacements for the fixed regulators. Using the documented 1.2–1.3 V reference interval, 0–100 µA adjust current and a conditional ±0.4% total resistor allocation gives U4 11.2754–12.4846 V and each audio rail magnitude 14.2948–15.8363 V. R1 is 110 Ω throughout; U4 R2 is 931 Ω and U6/U7 R2 is 1,210 Ω. Divider current is at least 10.8656 mA. A conservative 3 V differential gives an audio raw-rail floor of 18.8363 V. This is a documented-headroom boundary, not a simulated regulator dropout transfer curve. Manufacturer sources: [ST LM317 table 4](https://www.st.com/resource/en/datasheet/lm317.pdf), [ST LM337 table 4](https://www.st.com/resource/en/datasheet/lm337.pdf).

The regulator output bounds fall within the earlier ±15 V candidate range, but U4's low endpoint is below the prior fixed-regulator 11.4 V bound. Relay pickup, logic input and precision-reference interfaces must be explicitly reconciled before adoption. Regulators need new pin mapping, minimum-load resistors, stable local capacitors, discharge protection, removable contacts and a qualified heatsink. TO-220 tabs are not assumed interchangeable or isolated. No socket exception is authorized.

## Supply and shutdown cases

Both references have dual 18 V secondaries, 115/230 V primaries and 12% typical regulation. The model uses 120 V/60 Hz and 220 V/50 Hz operation, ±10% mains, a resistive winding surrogate, a generic rectifier and explicit constant raw loads. The 25 VA reference has 0.69 A series rating; the 50 VA reference has 1.39 A. Their derived per-half resistances are 3.1304 Ω and 1.5540 Ω respectively. These are typical-regulation surrogates, not measured DCR or guaranteed winding regulation. [Triad 25 VA](https://catalog.triadmagnetics.com/Asset/VPT36-690.pdf), [Triad 50 VA](https://catalog.triadmagnetics.com/asset/vpt36-1390.pdf).

Reservoirs are screened at 80% nominal capacitance, 0.15 Ω assumed ESR. The original load profiles retain R215, cold relay current and conservative divider loads, plus a provisional 20 mA positive control/reference reserve. Worst raw loads are approximately 235 mA positive and 112 mA negative. This is still not the completed signal/fault current budget.

Minimum time from loss of secondary excitation to the first raw-headroom violation, across both mains modes and six shutdown phases:

| Reference | Reservoir per rail | Nominal winding sensitivity | 5% low winding sensitivity |
|---|---:|---:|---:|
| 25 VA | 1,000 µF | 1.148 ms | Already inadequate in some cases |
| 25 VA | 4,700 µF | 19.433 ms | 0.754 ms |
| 25 VA | 6,800 µF | 29.681 ms | 2.647 ms |
| 50 VA | 6,800 µF | See retained cases | 29.552 ms minimum across all 24 shutdown cases |

The 25 VA matrix retains six cases with inadequate steady-state headroom; these are all low-winding, 1,000 µF shutdown cases. For the 6,800 µF/25 VA option, the 20 ms allowance passes 18/24 shutdown cases. The 50 VA comparison passes 24/24, including the 5% low-winding assumption. Its targeted comparison includes high-line/high-winding idle and stress cases; it is not the full 25 VA matrix repeated at 50 VA. A 5% sensitivity assumption is not supplier tolerance qualification.

Excitation is removed over 1 µs. Transformer magnetic storage, parasitic ringing and real regulator dynamics are absent. Only the first loss of documented headroom is meaningful; the constant-current load model beyond dropout is not physical. A null crossing means no crossing in the 120 ms observation interval, not unlimited hold-up.

The independent RC discharge solution after the winding sources reach zero agrees within 0.1 µs for finite crossings. Full results include KCL, winding RMS, conditional heat and numerical refinement. The targeted 50 VA comparison reaches 6.617 W total conditional regulator dissipation. This needs a real shared-sink/insulator calculation and enclosure-temperature check; a larger transformer does not remove regulator heat. Raw voltage remains below the proposed 35 V design ceiling in this model. Reservoir voltage rating is proposed as 50 V; actual capacitance, ripple, ESR, surge, dimensions and terminal fit require an exact part. No mains transient withstand or thermal qualification follows from this screen.

## Purchase and integration status

[Source observations](results/hold-up/source-observations.json) retain exact domestic listing fields and URLs dated 25 November 2026: LM317T-DG C18718 stock 13,210, LM337SP C118272 stock 156, both minimum buy and sales ratio 1. VPT36-690 C17563193 stock 0. Listing stock is not allocated stock; Shanghai checkout and delivered price are unverified. The seller-linked LM317 PDF is older Rev18 (2012); calculations use ST's Rev22 (2021). No substitute was inferred from the old drawing.

The 50 VA reference body is up to 83 mm diameter and 36 mm high before mounting hardware; it must join the populated three-board CAD fit, mounting/field-orientation check and cost comparison. It does not establish a chassis fit. Functional blocks and the independently removable wooden back are unchanged. Drill body/bit/reach remains pending beyond the measured 46 mm chuck.

## Next concrete action

Design the actual secondary-loss detector and budget its worst detection delay plus the existing coil decay, contact travel and bounce against the supply reserve. The 20 ms value here is hypothetical, not a relay specification. Include slow brownouts, short interruptions, reference/logic sequencing and restart inhibit; keep the analog rail monitor for rail-specific failures. Resolve a Chinese-stocked transformer or supplier-confirmed winding specification, exact reservoir and thermal implementation before selecting the supply or editing native CAD. All six through-chassis scopes remain open; no fabrication release, purchase or supplier message.

## 25 November load update

R619/R620 now add up to1.836735mA per rail in the declared load allocation. The hold-up factory consumes it for future runs; the results reported above remain historical. [VAL-064](../reverb-600/rail-load-integration/review.md) separately reruns all32 VAL-054 brownout cases with only this added load and retains a0.38320ms conditional timing reserve. Neither screen qualifies the complete power system.
