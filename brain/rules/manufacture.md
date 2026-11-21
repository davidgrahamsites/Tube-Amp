---
id: RULE-MFG
type: rule-set
domain: manufacture
status: documented
updated: 2026-10-03
---
# Manufacture and release

Scope: reusable workflow guidance, not evidence of verified circuitry.

## MFG-001
Capture the manufacturer's actual stackup, materials, tolerances and fabrication/assembly capabilities before finalizing constraints.

## MFG-002
Record the release revision and required fabrication data, drills, board specification, assembly documents, BOM and placement data where applicable. Include chassis wiring documents.

## MFG-003
Inspect exported outputs and reconcile schematic, PCB, BOM, footprint choices and assembly notes to one revision. Keep a release manifest and check evidence.

## MFG-004
Track prototype inspection, measurements and corrections before promoting a design to repeatable production. Preserve the review boundary in the canonical handoff.

## MFG-005
Create a vendor-specific fabrication package from reviewed canonical outputs; confirm merged/separate drills, slot encoding, finished holes and CAM alignment with that vendor. PCB drilling does not produce chassis, panel or cabinet holes. See [KiCad PCB documentation](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) and [JLC export instructions](https://jlcpcb.com/help/article/how-to-generate-gerber-and-drill-files-in-kicad-9).

## MFG-006
For products intended for sale, classify the finished product and accessories, price applicable conformity and support work, and keep a commercial-release gate separate from prototype engineering acceptance. Do not infer a small-batch exemption or buyer demand from a supplier listing. See [commercial decision record](../records/DEC-003-commercial-feasibility.md).

## Basis and exceptions
Seeded from [the handoff and discussion](../sources.md) and this requested engineering workflow. Record supporting evidence and exceptions as work proceeds. Project-specific values and results belong in [records](../records/CONTEXT.md).
