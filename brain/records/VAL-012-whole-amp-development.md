---
id: VAL-012
type: validation
domain: cross-domain
status: proposed
updated: 2026-11-12
---
# Whole-amplifier development and unresolved checks

The [v0.5 work area](../../engineering/whole-amp/README.md) extends board coverage to Main, Power and Control; the v0.4 reverb remains preserved. Native assembly netlists match mapped PCB pad partitions (Main167,Power67,Control157). This verifies logical pad mapping only, not route completeness, audio layout, component choices or cabinet fit. Final native Main/Power/Control DRC reports each have zero violations, unconnected items and schematic parity issues; their assembly ERC reports are clean. Integrated native pin partitions match all143 v0.4 net groups. The integrated ERC retains the documented PE/GND alias warning. Rendered board previews were inspected. No fabrication files are released.

[Simulation report](../../engineering/whole-amp/simulation/README.md) records generic valve model restrictions, ideal magnetics/supply limits, completed OP/AC and four transient cases,24 supply cases, a historical failed dirty transient subsequently completed in the November12 numerical-sensitivity runs, excessive predicted overdrive screen dissipation and dry-path clipping. No selected-component integrated validation or hardware measurement is claimed.

[Supplier contact](../../engineering/whole-amp/evidence/supplier-contact-log.md) was explicitly authorized and sent from the selected account, verified in Mail Sent. Cabinet geometry, availability and spring-tank documentation await response. No order or source upload occurred.

Next checks: functional layout/routing and native checks; resolve large-signal and protective-parts issues; integrate exact parts and fit evidence into a coherent release. Current status is development, not build-ready.

November12: dirty20mV/200mV runs now complete at1µs maximum timestep and increased iteration limits. A tighter20mV tolerance run also completes and preserves the excessive screen-dissipation finding. See the simulation report for scoped results. No PCB changes or build release.

November12 extended work: [80ms screen comparison](../../engineering/whole-amp/simulation/screen-tradeoffs/README.md) confirms the original1k screen circuit is a larger concern than40ms suggested.2.2k still exceeds8W;4.7k is a conditional simulation candidate with4.35W resistor heating, not a qualified fix. Passive dry mixing/attenuated send is being tested to avoid opamp dry-path clipping; AC attenuation is documented and integrated convergence remains unresolved. Results and limitations are captured in the simulation report. Native CAD has not been altered during this component/model work.

The [combined headroom candidate](../../engineering/whole-amp/simulation/reverb-headroom/README.md) now completes80ms/838226points with100ns maximum step and globalcshunt=0, retaining clamp protection and unmodified device models. Last10ms screenA/B4.13777/4.15928W; screen resistors3.93927/3.79398W; reverb input1.65135Vpeak.18AC cases pass six dry-control-independence checks. Numerical completion is scoped to nominal400V/-40V and ideal magnetics; high-line, settled stress, tube-model correlation, actual tank and transformer remain unresolved. Failed diagnostic variants are retained; no native circuit mutation or construction release.

**Later waveform review limitation:**~412kHz ringing is visible in the80ms candidate. A50ns5ms rerun changes mix peak by17.50%; feedback-zero still rings. Thus completion is not numerical qualification, and the provisional screen/headroom averages must not be used as release evidence. Diagnostics in simulation/candidate-hf retain the results. Source/model isolation continues; no physical protection or feedback changes adopted.

Further isolation: ringing remains in the tube-only fixture and shifts172/416/584kHz as the assumed transformer coupling changes. A separate [ideal-transformer low-frequency reference](../../engineering/whole-amp/simulation/ideal-transformer-candidate/README.md) passes ratio/impedance/power-balance checks and an80ms run. A5ms200ns→100ns sensitivity check changes mix peak0.0055%; this does not qualify the80ms settling or real HF behavior. Final-window B+current225.77mA strengthens the need for larger-magnetics quote options. The old inductive-transformer results and failures remain preserved; no arbitrary damping fix adopted.
