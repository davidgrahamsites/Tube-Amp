---
id: VAL-031
type: validation
domain: pcb
status: documented
updated: 2026-11-24
---
# U12 rounded fork and complete copper inventory

[Repair review](../../engineering/whole-amp/pcb-measured-r/review/u12-routing-review.md) records the adopted two-arc U12 fork and eight enlarged chamfers. Exact native delta, tangent geometry, exported drills, native DRC and visual checks pass. All widths, footprint/pad geometry and functional blocks preserved. Reverb has zero violations and zero unconnected items; this does not qualify all board routing.

Fresh socket checks verify both the socket correction and this follow-up delta. Mechanical source hashes refreshed; support-plane fit and actual drill access still fail or remain pending. The 46 mm user-measured chuck diameter remains recorded with a proposed 2 mm radial allowance.

The read-only copper audit includes 134 board/net entries and independently checked pad coverage, including wholly unrouted nets. Eleven other branch candidates outside pads/vias remain for review. Per-path current/stackup/thermal and voltage-drop qualification remain open; no default-width approval or build-ready claim.

Next: repair remaining branch geometry, establish current envelopes from the actual supply/load/fault cases, and complete exact supervisor/carrier and populated three-board placement. China/Shanghai purchase readiness for the complete BOM remains unproven. No procurement or fabrication release.
