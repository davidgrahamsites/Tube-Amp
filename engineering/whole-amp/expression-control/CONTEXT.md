# expression-control contract

Owner: Renegade integration agent. One job: provide wet-only expression level control with a protected low-voltage pedal interface.

## Inputs
Paths in this contract are project-root-relative unless named as local. Read `engineering/whole-amp/expression-control/requirements.md`, `brain/records/DEC-016-buffered-loop-expression-selector.md` and `engineering/whole-amp/reverb-600/circuit.json`. Local edit surfaces are requirements.md, selector-review.md, ota-review.md, supply-bias-review.md and trim-isolation-review.md.

## Process
User requested PANEL / EXPRESSION selection; exact control circuit and PCB integration are pending. tools/ota_screen.py screens the isolated audio gain cell; tools/audit_ota.py checks its retained evidence. models/ contains manufacturer model inputs and acquisition manifests; results/ contains repeatable run products. supply_probe.py isolates solver behavior; bias_screen.py owns the practical bias candidate; audit_supply_bias.py validates retained evidence while exposing circuit holds. trim_screen.py owns the nominal trim comparison; bias_continuation.py and bias_isolation.py diagnose initialization and settling; audit_trim_isolation.py audits this evidence. No native CAD mutation belongs to these factories. Pedal control/protection is a separate interface from audio gain-cell evaluation within this module.

## Outputs
ota-review.md interprets results/ota-screen.json and ota-audit.json; selector-review.md defines the proposed control interface. The current experiment is not an implemented expression feature. `brain/catalog/FILES.json` indexes roles and hashes; `brain/materials/register.json` identifies the owning material route.

## Human check
Open the local output with its source/reference and confirm revision, unresolved limits and actual part or circuit identity before using it for the build. For native CAD, inspect the render and pin/geometry checks; for runs, inspect assumptions and logs.

VAL-045: tools/settled_bias.py owns powered steady-DC initialization and late-window measurements; tools/audit_settled_bias.py independently validates stationary behavior, KCL, refinement and counterexamples. settled-bias-review.md interprets results/settled-bias.json and settled-bias-audit.json. No cold-start qualification follows from this method.

The protected control-only interface proposal is pedal-port-design.md. It separates selection, smoothing, polarity mapping and existing mute priority, and explicitly retains the passive-pedal tip/ring fault ambiguity and domestic sourcing hold.

references/ owns retained manufacturer jack drawings and the visually checked geometry observation. Exact-part drawing holes remain candidate dimensions until finished-hole/lead tolerances and sourcing are qualified.

VAL-046: power_sequence.py owns diagnostic rail ramps/losses; results retain two failed runs and model limits. integrate_final_mute.py is an explicitly mutating, baseline-guarded native adapter for the spare K3 contact only. audit_final_mute.py verifies the declared two-pin delta and geometry preservation. final_mute_loading.py owns the passive dry-loading calculation. final-mute-review.md is the current interpretation; automatic rail-fault inhibit remains unimplemented.

VAL-049: wet-fault-contract.json owns the passive disturbance scenarios. tools/wet_fault_transfer.py reads and guards native topology; tools/check_wet_fault.py independently checks three cases and timestep refinement in bounded SPICE subprocesses. wet-fault-review.md interprets the current results and rejects a delayed shunt as a complete quiet-fault solution. No CAD mutation belongs to these tools.
