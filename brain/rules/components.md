---
id: RULE-CMP
type: rule-set
domain: components
status: documented
updated: 2026-10-03
---
# Component selection

Scope: reusable workflow guidance, not evidence of verified circuitry.

## CMP-001
Select against explicit circuit requirements and dated evidence. Record exact manufacturer part number and a component dossier; listing titles do not establish suitability.

## CMP-002
For transformers, document winding requirements, frequency, loaded behavior, current, insulation and mechanical constraints. For tanks, distinguish impedance from DC resistance and verify mounting and connector grounding.

## CMP-003
Validate symbol pin mapping and footprint against the selected part's drawing. Document chassis parts through wiring without inventing PCB footprints.

## CMP-004
Record alternatives and tradeoffs. A selected part remains unverified for any rating or interface lacking evidence.

## CMP-005
For tube matching, preserve actual electrode conditions, tube family/variant, profile revision, calibration identity and measurement uncertainty. Match power-tube current and response under common conditions; evaluate dual-triode sections and noise/gain/headroom according to circuit role. A coarse bin, equal cathode currents, or a single typical datasheet value does not establish a healthy matched pair. See [DEC-006](../records/DEC-006-tube-matcher.md) and its manufacturer sources; test limits and performance remain proposed until measured.

## Basis and exceptions
Seeded from [the handoff and discussion](../sources.md) and this requested engineering workflow. Record supporting evidence and exceptions as work proceeds. Project-specific values and results belong in [records](../records/CONTEXT.md).
