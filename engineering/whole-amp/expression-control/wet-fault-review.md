# Passive reverb fault transfer and fast-shunt feasibility

## Task contract
Owner: expression-control integration. Inputs: native reverb-600/circuit.json at baseline1c2e5c8, wet-fault-contract.json and the onsemi MMBFJ113/D Rev.5 datasheet. Outputs: results/wet-fault-transfer.json, wet-fault-crosscheck.json and wet-shunt-source-observation.json. Automated work: read-only topology guards, passive transfer calculation, bounded independent SPICE runs and timestep comparison. Done-condition for this checkpoint: quantify the disturbance before relay closure and establish whether a proposed shunt merits further work. Human evidence still required: exact assembly, rail-collapse measurements and audibility/bench validation. This is a small L1/L2 investigation, not native integration or manufacture approval.

## Finding
The native K3 contact is not fast enough to be credited as immediate fault suppression. An additional shunt closing even50µs after a forced output fault leaves the initial spike. Reject any claim that the proposed delayed shunt alone solves quiet fault switching. First establish whether rail warning can reliably precede loss of valid audio output; hard faults may provide no such warning. Keep the final K3 mute and functional blocks intact.

The native passive network is R616100Ω, C6071µF, R617/R6181MΩ, R612100kΩ and R2410MΩ. The analysis ends at MIX_OUT. The real C19/R25 bootstrapped phase-inverter input is not represented by a resistor; optional1MΩ loading is only a sensitivity case.

Thirty AC and120 transient cases cover return source resistance0/10k/100kΩ, optional added1MΩ load, incremental fault changes16.5/33V and1/10ms duration. A33V change represents a transition between opposite16.5V limits, not a33V supply. Sources are imposed fault scenarios, not invalid extrapolations of a manufacturer op-amp model.

## Candidate and tradeoffs
An unadopted47kΩ R616 replacement could current-limit a J113-family shunt at WET_AC. At the100Ω maximum on-resistance test condition, a33V incremental step gives at most70.1mV across the shunt. Native100Ω and a22kΩ alternative fail the chosen100mV low-level screen. These limits are at25°C; they do not establish hot or bilateral fault behavior, gate-bias limits or pulsed-device qualification.

- Worst imposed MIX_OUT peak:5.409V native versus4.980V with47kΩ and assumed50µs shunt. Neither is a speaker-voltage prediction.
- Candidate wet gain changes−0.751 to−0.717dB across the sampled cases. Recalibration would be necessary if adopted.
- Dry gain perturbation stays below0.0613dB; candidate mute changes dry gain by less than0.0614dB, within the0.1dB screen.
- Added20kHz versus1kHz wet response change is−0.00320 to−0.00318dB with the5pF off-capacitance assumption. This says nothing about actual harness capacitance or complete amplifier treble.
- With50µs shunting, the integral of squared MIX_OUT voltage is0.00429–0.04246 times the15ms-contact scenario. This quantity is not acoustic energy or a perceptual silence criterion.

The candidate uses the datasheet100Ω on-resistance and5pF off capacitance only at their stated test conditions. No actual gate circuit, optocoupler, detector or JFET model has been qualified. No part or socket exception is adopted.

## Independent verification
check_wet_fault.py builds an independent six-element SPICE network, rather than calling the analytical transfer function. Three cases run at2µs and0.5µs maximum timestep: no mute,15ms contact and47kΩ/50µs shunt plus15ms contact. All six complete in bounded subprocesses. Maximum peak relative error is4.63e−7; maximum squared-voltage-integral relative error is0.000310. Maximum integral timestep delta is0.0000156. Small differences include the100ns input/switch edges. Four analytical screens and four cross-check screens pass; circuit qualification remains false.

The switches are ideal resistances. Their timing is assumed, with no real gate charge, off-capacitance transient, contact bounce, transformer, speaker or tube-grid response. Tests do not remove these limitations.

Reproduce using KiCad's bundled Python:
```
python3 engineering/whole-amp/expression-control/tools/wet_fault_transfer.py
python3 engineering/whole-amp/expression-control/tools/check_wet_fault.py
```
The second command requires the installed KiCad libngspice adapter. Decks and solver logs are retained inline in the generated JSON. Files overwrite their current outputs.

## Chinese sourcing observations
The [manufacturer datasheet](https://www.onsemi.com/pdf/datasheet/mmbfj113-d.pdf) covers both exact parts. The older j111-d.pdf does not cover J113 and was excluded. The retained reference and source observation carry hashes.

On25November2026, the domestic [J113 C274643 listing](https://item.szlcsc.com/262861.html) reports TO-92-3L,963 raw stock and minimum-buy1; [MMBFJ113 C891686](https://item.szlcsc.com/957156.html) reports SOT-23,10779 raw stock and minimum-buy1. Both also report ratio/conversion5 and different valid-stock fields. Treat1 as a sales-unit field, not proof of one loose physical part. Global listings give different stock snapshots; domestic fields are retained without averaging. Exact physical minimum, current unit price and Shanghai address-specific checkout remain unverified. No order or supplier contact occurred.

## Next action and release boundary
Establish the minimum valid audio rail/headroom envelope and actual collapse slopes, compare warning lead time with worst-case switch closure, and only then choose the fast-mute/gate topology. Include gate feedthrough, hot limits, abnormal bipolar excursions and smooth recovery. Retain pending exact sourcing/footprint/socket checks. This checkpoint makes no native schematic/PCB/chassis change and closes none of the six build scopes.
