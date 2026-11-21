# Revision review evidence
Inputs: native exports, simulator results and sourced component dossiers.
Process: retain check outputs and explain limits in review.md; separate dated supplier evidence from selected circuit values.
Outputs: review, native netlist/ERC reports, PDF, parts overlay and provenance hashes.
Human check: review unresolved cabinet fit and expression-pedal interfaces before integrating into the new board layout.

Electric input loading: electric-input-loading-2026-11-21.json is a generated scoped native check and resistive calculation. Decision and limitations are owned by brain/records/DEC-010-electric-input-no-buffer.md. Regenerate through tools/check_electric_input.py and a fresh native export.
