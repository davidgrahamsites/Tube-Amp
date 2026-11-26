# Wet-contact native integration
Owner: amplifier integration agent. One job: apply the VAL-067 local wet-contact correction to authoritative source, schematic and Reverb PCB.

## Inputs
Adjacent wet-protection/contract.json and review.md; manufacturer PDFs there; hash-bound native inputs in contract.json. Prior rail-load-integration tools supply only explicit CAD utilities/export conventions.

## Process
Stable tools generate exact package footprints, patch declared native objects, export KiCad witnesses and independently check explicit net/geometry/drill deltas. Preserve functional blocks, board outline and mounting holes. Do not rerun old whole-board factories over this incremental revision.

## Outputs
Native D603/D604 opposing-series clamp; R616 pulse-rated PR01; R618 350V MF0207; results with ERC/DRC/netlist/drill/render receipts; review.md. This is an engineering draft, not fabrication release or relay contact-life qualification.

## Human check
Read the two diode cathode bands against the schematic, verify PR01 formed leads and finished-hole tolerance, then inspect 07c and board routing. Procurement stock/Shanghai delivery and full-system protection/spacing remain open.
