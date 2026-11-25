# Reverb ground-plane candidate — held by voltage-domain review

Updated November25. Owner: PCB integration. No active board changed. This follow-up to VAL-059 tested a bottom-layer GND plane, then rejected adoption when the circuit review disproved a blanket low-voltage assumption.

## Geometry evidence

KiCad10.0.6 generated and filled one B.Cu GND region with four mounting-zone exclusions. It occupies14,061.69mm² of the160×100mm board (87.89%), one native filled polygon, not an isolated island. All25 existing GND pads remain in the unchanged net inventory. The four mounting centers have a provisional9mm copper-free diameter; native samples through4.49mm radius pass. Actual washer/insulator selection remains open. No tracks, pads, footprints, net names, holes or vias were added or moved; only five zone nodes were added.

The full-board KiCad save initially rounded existing arc coordinates. The factory therefore transplants only API-produced zone nodes into the original text. Independent token comparison verifies exact preservation of every old board object and30 native companion files. This is stronger than accepting a small coordinate tolerance. Strict native DRC with refill and all-track checks gives0violations/0unconnected items, with no project exclusions or ignored checks hiding findings. Command and hash receipts are in results/native-run.json. Final bottom/overlay plots were inspected: one broad fill, preserved original routing and clear mounting corners. Long existing bottom routes still interrupt local return paths and need the complete routing review; area percentage is not noise qualification.

## Why the candidate is not adopted

The op-amps use±15V, but **the dry path is not bounded by those rails**. Native J4 normals FX_SEND into FX_RETURN. JR1 carries that node; C601 feeds its attenuator branch, while R612 directly carries it toward MIX_OUT/JR5. R618 couples MIX_OUT back toward WET_AC/C607. Prior generic-model heavy-overdrive cases record FX_SEND−135.094/+97.777V in effects-loop/solver-review.md and return-headroom-review.md. Those cases are protection evidence, not the normal clean specification or a guaranteed all-condition maximum.

Consequently JR1/JR5's “Low voltage only” source ratings, the board's “LV DRAFT” label and globally0.25mm custom rule are insufficient evidence for this interface. A0.5mm plane clearance that passes those rules is **not** voltage qualification. C607's63V selection also requires its actual differential transient voltage to be checked; its voltage cannot simply be equated with either ground-referenced node swing. No capacitor failure is inferred from that single-node observation.

The candidate remains outside active CAD. `checks.json` explicitly says adoption_allowed=false and voltage_domains_qualified=false despite passing geometry/DRC checks. All active source/schematic/board hashes still match the baseline. No fabrication output or new purchase item was released.

## Return-path evidence and scope

The existing T03 grounding contract already establishes the logical permanentGB1 signal/chassis bond and independent protective earth. It remains the authority; do not redo or replace it. The proposed local map has JR6 supply return and JR2 tank-drive return in the upper/right region, quiet JR3/U11 recovery at lower left and U12/JR5 mix at lower right. K3 coil current goes through+12V/COIL_REV and localD341, not intentionally through the audioGND plane; its grounded contacts are audio mute references. Actual JR1/JR5/JR6 shield/supply harness loops remain unresolved.

[TI OPA2134 RevB](https://www.ti.com/lit/ds/symlink/opa2134.pdf), section7.4, supports a ground reference and short feedback/input routing; it recommends local low-ESR ceramic bypassing. The existing film bypass choice/placement therefore needs a specific high-frequency loop review, especially C611's long negative-supply route. This does not authorize replacing the sockets or using generic ground splits. [ADI grounding guidance](https://www.analog.com/en/resources/analog-dialogue/articles/staying-well-grounded.html) supports low-impedance planes with explicit current-return management. Neither source proves the amp's high-voltage clearances or assembled EMI.

## Next actions

1. Correct the misleading voltage-domain metadata; derive dry/interface normal, overload, startup and fault envelopes from the native source and selected RETURN architecture.
2. Qualify connector voltage/pitch/insulation and C601/C607/R612/R618 stress, then encode actual board-specific clearance/keepout rules.
3. Rebuild a domain-aware plane, inspect real filled return paths and solve new native violations; only then adopt it. Continue control/power/audio routing and populated three-board fit.

Reproduce candidate generation into a new temporary directory, then run run_native_checks.py, inspect_fill.py with KiCadPython and check.py with ordinaryPython. Candidate copies are disposable and not source products. Human check: compare the final filled copper and actual hardware/insulation against the voltage domains and complete return map before fabrication. All six scopes remain incomplete.
