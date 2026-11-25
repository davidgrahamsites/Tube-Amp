# Analog-rail reverb inhibit — candidate screening

2026-11-25. This circuit is **not adopted**. It extends the VAL-046 final wet-output contact repair; it does not replace the user latch, +5V supervisor, or reverb block.

## Proposed connections

Use a socketed TI LM393P powered from +12V/GND, with local 100nF bypass. Both open-collector outputs join REV_GATE. Change the candidate gate series resistance to 4.7k; retain the existing 100k gate pull-down and REV_Q control. Thus no added pull-up can override a user OFF command. Do not add these changes to native files until the following limits are resolved.

| Comparator input | Candidate network |
|---|---|
| A positive, PSENSE | +15V through38.3k;4.99k toGND;330k feedback fromREV_GATE |
| A negative, PREF | +5V divider30k/10k |
| B negative, NSENSE | CLAMP through30.1k;10k toGND |
| CLAMP | +5V through10k;-15V through51k;Schottky cathode here, anodeGND |
| B positive, NREF | +5V through91k;10k toGND;2M feedback fromREV_GATE |

The split negative divider follows the topology in TI SNOAA35F §6.9.3.2.1, visually checked on page21. It attenuates the diode clamp voltage before the comparator input. A conditional1V clamp allocation produces a worst input magnitude below0.256V in the budget. An exact diode must still satisfy that allocation over temperature and leakage; this is not a selected-diode guarantee. The comparator's negative input is outside normal common-mode range during this fault, so its logical output is not assumed correct there. Loss of +5V must independently inhibit the relay through the existing reset/latch path.

## Static result and rejected limits

`rail-monitor-contract.json` is the editable circuit/limit interface. `tools/rail_monitor_budget.py` enumerates resistor endpoints, reference4.75–5.25V, classic-device offset±9mV and input-current magnitude250nA. It uses a provisional healthy-gate lower bound3.5V, derived conservatively from the existing HC74 VOH3.84V limit and added loading, not an ideal5V logic output. Full DC gate/sink verification remains open.

| Screen | Positive rail magnitude | Negative rail magnitude |
|---|---:|---:|
| Enable threshold range | 9.955–12.029V | 9.229–12.662V |
| Disable threshold range | 9.394–11.620V | 8.576–12.204V |
| Minimum same-unit hysteresis | 0.353V | 0.391V |

Only4 of7 provisional engineering screens pass. Both maximum enable thresholds exceed the12V screen; the negative minimum disable threshold falls below9V. These limits were not relaxed to obtain a passing result. The1% resistor budget also omits temperature/endurance additions, so nominal1% purchasing would be insufficient to claim these bounds for life. Comparator delay, reference startup, coil release with flyback diode, socket leakage, actual clamp behavior and simultaneous faults remain unqualified.

Next revision: compare a better controlled reference/ratio network against tighter sourceable resistor grades, then prove the gate bounds and threshold hysteresis with the actual parts. Preserve the failed initial candidate as evidence. Avoid adding a capacitor directly to a hysteresis feedback input; TI describes how that can defeat immediate hysteresis. Rapid rail shorts still require a separate evaluation of the interval before a mechanical contact releases.

## Source and model identity

[TI LM393 data](https://www.ti.com/lit/ds/symlink/lm393.pdf) distinguishes the classic PDIP part from B variants. [TI comparator application guidance](https://www.ti.com/lit/an/snoaa35f/snoaa35f.pdf) covers negative input protection and startup limitations. Retained PDFs and hashes are in evidence/ and results/rail-monitor-source-observation.json.

The TI product page's [SLCJ016 download](https://www.ti.com/lit/zip/SLCJ016) contains `lm393.lib`, but the file header and top-level subcircuit identify **LM2903B**, with3.5nA/0.37mV nominal input parameters. It was rejected as qualification evidence for LM393P. No model was renamed or modified to hide this mismatch. The static budget uses datasheet bounds and does not claim a manufacturer-model transient result.

[Chinese LCSC LM393P/C5209](https://item.szlcsc.com/5630.html) exposes minimum buy1, stockNumber331 and validStockNumber66 on2026-11-25. Both stock fields are retained because they differ; neither is a reservation. Domestic courier service supports a Shanghai route in principle, while address-specific checkout remains unverified. Exact resistors, clamp diode, socket and final quantities are not yet approved for purchase.

All native files remain at the verified VAL-046 repair. This candidate changes no PCB, socket footprint, chassis or mounting access.
