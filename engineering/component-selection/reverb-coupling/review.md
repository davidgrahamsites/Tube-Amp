# C607 voltage-rated coupling capacitor — VAL-062

25 November 2026. Engineering integration, **not fabrication release**.

The previous 1 µF/63 V C607 passed the limited normal-signal screen but failed
the conditional 153.422 V differential fault screen in VAL-061. C607 is now
KNSCHA **MPP105J2W10KN22605, 1 µF ±5%, 450 VDC polypropylene**. Capacitance,
OUT_AC/WET_AC connections and functional blocks are unchanged. The nominal
rating is 2.93 times that particular screened voltage; it is not proof of
complete fault, transient, temperature or ripple qualification.

## Source and package

[Manufacturer and domestic sourcing evidence](evidence/sourcing.md) retains the
exact drawing and dated ICKey listing. Minimum one, listed ¥0.7282 each at the
one-piece tier, with mainland delivery. The exact Shanghai address has not been
checked. Coverage P094 now contains C606 only; new P130 owns C607. Other uses of
the old 63 V part retain their existing selection and qualification status.

The new selected-library footprint uses a maximum 13 × 8.1 mm body courtyard
plus 0.25 mm on each side and records maximum height 16.4 mm. Pitch is 10 mm.
Both leads are round, maximum diameter 0.65 mm. Both finished holes are 1.0 mm;
with a provisional ±0.1 mm hole tolerance, minimum diametral clearance is
0.25 mm. Pads are 1.9 mm. Manufacturer pitch tolerance is ±0.5 mm, so the long
leads must be hand-formed to the board pitch before insertion; the hole cannot
absorb the whole pitch tolerance. Fabricator hole tolerance, plating and
as-received insertion still need confirmation. No 3D model or complete chassis
height check is claimed.

## Placement and verification

Final pad positions: OUT_AC at (131.5, 53) mm and WET_AC at (141.5, 53) mm.
Two original 0.3 mm front-layer escape segments become four segments with
45-degree changes of direction. All other footprints, tracks, arcs, vias,
zones and board settings are preserved. No ground pour is adopted.

Earlier positions collided with existing +15 V, MIX_OUT or GND copper; these
were rejected. Final `results/after-drc.json` reports zero violations and zero
unconnected items with all track errors enabled and no severity suppression.
The present rules do **not** yet qualify tube-interface voltage spacing.

`tools/check.py` independently confirms 144 nets and 236 component identities,
18 pixel-identical schematic pages, one unchanged existing ERC finding,
exactly two changed round drill holes and 136 unchanged other drill hits. The
Excellon outputs are a drill witness, not manufacturing deliverables.
The plotted placement was visually inspected: the larger C607 courtyard is
clear of R616 and JR5, with readable C607 identification. Its maximum height
remains a chassis input.

Factories are one-shot against the contract's baseline hashes; rerunning the
integration against another design fails before writes. The export adapter
also refuses to call a changed design the historical baseline.

## Remaining gates and next action

The existing D601/D602 already clamp SEND_IN to the ±15 V rails. Do not add
redundant diodes merely because the unclamped VAL-061 fixture exceeded a rail.
Next work must bound R601 input current and rail charge injection, including
unpowered/repeated startup, with the real clamp and supply behavior. Then set
net-specific voltage spacing and revisit the B.Cu ground plane. No claim that
the current 0.3 mm routes, connector insulation, whole reverb board or entire
amplifier is qualified follows from this component change.

BOM generation exposed two pre-existing selected parts without candidate rows:
AOS AO3400A (P074) and UNI-ROYAL MFR0W4F8200A50 (P129). Their existing
engineering selections are unchanged. The missing identity records are now
restored from exact catalog/evidence links, with unknown domestic price and MOQ
explicitly null. Same-name MOSFETs from other manufacturers are not substituted.
See [registry reconciliation](../evidence/registry-reconciliation-2026-11-25.md).
Selected-BOM generation now reports these as unpriced rather than failing or
silently treating them as free.

No purchase, supplier contact or fabrication upload occurred. All six build
scopes remain incomplete.
