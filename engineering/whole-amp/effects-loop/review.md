# Effects-loop execution checkpoint — 23 November 2026

**Status: model screening only. No circuit, PCB or fabrication release.** Owner: electric-build integration. User authorization: FB-101. This executes the first stage of the [reviewed plan](../../../plans/effects-loop-optical-review/final.md).

## Findings and disposition

| Check | Result | Engineering action |
|---|---|---|
| Existing J3 SEND short | SEND shares the normalled internal signal node. A short suppresses dry signal and spring excitation. | Evaluate a separate SEND driver branch; retain the internal normal path. |
| Simple unity return buffer, 1 MΩ input / 1 kΩ output | Wet contribution at PI input changes −2.26 dB clean / −6.88 dB dirty at nominal controls near 1 kHz. | Reject this as a transparent drop-in. Low output impedance changes passive mixing. |
| Separate SEND branch: 9.9 MΩ / 100 kΩ pad, ideal follower, 100 Ω output | 108 AC cases; largest checked internal transfer change −0.134 dB, within the proposed ±0.5 dB screening limit. Includes external short. | Promising architecture experiment. No real amplifier or fault protection selected. |
| Original return input impedance | About 488 kΩ near 1 kHz, 340 kΩ at 20 kHz in this fixture. | Does not meet the proposed 1 MΩ midband target. Revisit recovery and mix together. |
| Feedback sign in ideal transformer fixture | Corrected sign reduces closed-loop small-signal gain; earlier sign gave positive feedback. | Correct the test fixture only. Verify actual transformer phase on hardware; no lead-colour conclusion. |
| Numerical sensitivity | Four bounded transient cases and two timestep refinements completed. Checked amplitudes changed at most 0.046%; THD changed at most 0.0075 percentage points. | Accept these scoped model results only. |
| Heavy-overdrive coverage | Clean, B_EARLY 240 V, 1 kHz, 1 V peak source fails before the retained window. | No maximum signal, clipping recovery or worst-case headroom qualification. |

The separate SEND branch provides **load decoupling, not galvanic isolation**. The ideal follower can supply unlimited current; its short-circuit test proves only the intended connectivity. A physical part still needs current limiting, clamp/fault analysis, capacitive-load stability and noise checks. A 100:1 pad is a trial ratio, not the final pedal level.

The original tube stages and all three audio transfers are represented: dry to PI, dry to spring-input divider, and wet to PI. The return still enters ahead of spring excitation and passive dry/wet mixing. It is not acceptable to move that point or silently change the wet balance to make a buffer pass.

## Signal evidence

At B_EARLY 278 V, B_PRE 313 V, electrical volume fraction 0.25, tone/gain fractions 0.5, 1 kHz:

| Selected channel | Source sine peak | FX_SEND minimum / maximum |
|---|---:|---:|
| Clean | 10 mV | −1.150 / +1.152 V |
| Clean | 100 mV | −11.360 / +11.413 V |
| Dirty | 1 mV | −1.344 / +1.333 V |
| Dirty | 10 mV | −5.931 / +7.900 V |

These are selected operating points, not maximum limits. Input source includes 20 kΩ series resistance and 470 pF cable capacitance. Pot fractions are electrical fractions, not knob rotation. Small-signal AC gains use unit excitation for linearization and must not be interpreted as actual unclipped output voltages at a 1 V guitar input. The PI grid has substantial DC bias; its absolute DC value is not the pedal signal voltage.

The ideal-transformer model can show DC offset under asymmetric clipping and omits magnetic saturation. Its distorted speaker waveform is diagnostic, not a real output-power or transformer rating prediction. Generic tube models, fixed bias and stiff supplies do not qualify the final amplifier.

## Parts research and current choice

Retain K1/K2/K3 and their 2N7000 drivers. An optocoupler in their shared-ground control path adds no system isolation. No optical substitution has been adopted.

- TI [OPA2134 datasheet](https://www.ti.com/lit/ds/symlink/opa2134.pdf): operating supply range ±2.5 to ±18 V; output/input headroom depends on load and common-mode range. The existing ±15 V reverb supply does not establish adequate loop recovery headroom. A padded SEND buffer is a possible application; return recovery remains unselected.
- Microchip [LND150/LND250 datasheet](https://www.microchip.com/content/dam/mchp/documents/OTH/ProductDocuments/DataSheets/LND150-LND250-N-Channel-Depletion-Mode-DMOS-FETs-Data-Sheet-20005454A.pdf): 500 V depletion MOSFET, IDSS 1–3 mA and VGS(off) −1 to −3 V. This is a candidate for high-voltage recovery, with large bias spread requiring corner analysis, dissipation and fault checks. A device voltage rating is not operating approval.
- Mainland LCSC indexed leads: [LND150N3-G](https://item.szlcsc.com/661514.html), [LND150N3-G-P003 / C629120](https://item.szlcsc.com/658919.html). The former indexed alternatives showed four P003 pieces at ¥4.19 and twenty P002 pieces at ¥7.30 on this research pass. The exact P003 page failed direct access. These are provisional search observations; quantity price breaks, stock, order minimum, exact suffix/package and checkout availability remain unverified. **Not a released BOM selection.**
- onsemi [MPSA42 datasheet](https://www.onsemi.com/pdf/datasheet/mpsa42-d.pdf): 300 V absolute VCEO. Reject direct exposure to the 320 V sensitivity rail; a lower regulated rail would require separate evaluation. Absolute maximum is not a design operating point.
- [ValveWizard tube-loop example](https://www.valvewizard.co.uk/fxlooppcb.html) illustrates substantial send attenuation and recovery gain. It adds tube circuitry and is not adopted into this build.

## Repeatable evidence

Run from the repository root:

```sh
python3 engineering/whole-amp/effects-loop/tools/run.py
python3 engineering/whole-amp/effects-loop/tools/send_isolation.py
python3 engineering/whole-amp/effects-loop/tools/audit.py
```

The recorded failure can be reproduced with `bounded_case('overdrive-coverage', dict(channel='clean', supply=240, freq=1000, amp=1))` from `tools/run.py`. `run.py --extended` attempts a larger matrix, with each nonlinear case limited to 30 seconds. A failed solve remains a failure in the output; process success alone does not mean every case passed.

[Audit](results/audit.json), [integrated results](results/summary.json), [SEND-branch results](results/send-isolation-summary.json), [failed overdrive case](results/overdrive-coverage.json) and [solver history](results/solver-attempts.md) are the evidence seams. Source/model hashes, exact decks, logs and the extracted input components are retained. To replay against the saved input instead of a subsequently edited circuit, set `RENEGADE_LOOP_INPUT` to the absolute path of `results/source-components.json`. Model files and ngspice runtime must also match the recorded hashes/version. Runtime uses the existing macOS KiCad ngspice adapter and NumPy. Model licensing limitations remain as stated in the original model files.

## Next engineering work

1. Resolve heavy-overdrive numerical behaviour using stage-by-stage comparison and a less ideal output transformer model. Verify feedback sign and DC operating points at each step; do not loosen tolerances until results appear plausible.
2. Establish the required return voltage and overload-recovery envelope across supply, controls, pickup level and pedal outputs.
3. Compare a high-voltage recovery stage against a compensated passive mix interface. Preserve dry, wet and spring-send transfers. Bias, clamp faults, noise and supply sequencing must be included.
4. Select exact China-source amplifier, protection and connector parts, then draw the readable native schematic and integrate the board interfaces.
5. Re-run ERC/net equivalence, all affected routing/DRC/current/insulation checks and the populated chassis fit. Rear-panel removal and actual drill access remain release gates. Nothing in this electrical fixture proves mechanical fit.

Human check: review the changed transfers and candidate headroom before accepting a recovery topology. No further permission is needed for the authorized engineering work; unresolved evidence is a technical task, not an approval request.
