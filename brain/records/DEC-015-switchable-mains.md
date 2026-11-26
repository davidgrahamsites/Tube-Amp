---
id: DEC-015
type: decision
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Include switchable 120 V / 220 V mains in this build

## Authority
FB-106: after asking the incremental cost, the user said “I would like to build it in”. This supersedes FB-085 / DEC-012's deferral. Current electric build now requires selectable 120 V / 220 V operation. Existing 220 V CAD is the engineering baseline, not a completed dual-voltage design. No order, actual selector part or transformer has been approved by this scope decision.

## Implementation contract
Owner: electrical integration; mechanical and sourcing own dependent interfaces. Keep the six-tube circuit, reverb, effects, functional blocks and owned cabinet. Evaluate a recessed, clearly marked selector operated only with power disconnected. Select a transformer with documented appropriate primary taps/windings; account for every auxiliary mains-powered supply. Two nominal 115 V primaries do not by themselves establish correct secondary voltages at both requested 120 V and 220 V inputs.

Design/verification targets are 120 V / 60 Hz and 220 V / 50 Hz. Derive allowable line ranges and corner tests explicitly before release. Check primary current/inrush and voltage-specific fuse arrangement, switch ratings/contact sequence, wiring insulation/spacing, selected/incorrect/intermediate selector states, no-load/full-load secondary voltages, heater/HV/bias/control/reverb rails, temperature and markings. Protective earth stays permanently bonded and outside all switching/fusing. Do not infer that a switch alone converts a 220 V-only transformer.

[Hammond multi-primary guitar-amp transformer data](https://www.hammfg.com/electronics/transformers/classic/290) and [Schurter selector assemblies](https://www.schurter.com/en/part/4305.0048.00) establish available architectures, not suitable selected components or China quotations. Quote exact qualifying China-source parts before purchase; do not automatically buy these reference brands.

## Cost and task impact
Provisional incremental materials/fabrication allowance **¥150–400** if planned before parts and metalwork orders. Not a quote; paid engineering/testing and later retrofit costs excluded. Cost and fit must be reassessed after load budget and supplier drawings. [Cost record](../../engineering/component-selection/evidence/prototype-cost-allowance-2026-11-24.md).

Update T04–T06 supply/behavior corners, T08 magnetics/selector sourcing, T09 mains harness/fuses, T10/T11 selector placement/access, T12 insulation/rules, T13 schematic and T15–T18 release/physical tests. No reduction of required margins for cost. Scope is active; implementation/qualification is pending.

## Human check
Compare the final selector markings, fuse instructions and all mains-winding connections against the selected transformer drawing and the actual unit before energizing. Both supply settings need physical validation, not only simulation or label changes.

## Explicit fuse requirement — November25, FB-137

User: “we should have proper fuses for120 and220 volts, also”. Select and verify protection for each mains mode using continuous input current, worst-line loading, transformer inrush, time-current curves/I²t coordination, interrupting capacity, voltage rating, holder/contact/temperature ratings and exact obtainable parts. Do not size from25W audio output or simply assume a2:1 pair. Document the physical fuse arrangement, replacement instructions and selector/fuse mismatch behavior. No numerical fuse values are selected yet. Update schematic, BOM, panel markings and both-mode test procedure together; protective earth is never fused.
