# Local wet-contact correction — native integration

D603/D604, R616 and R618 are now implemented in the authoritative circuit, readable sheet 07c and Reverb PCB. This applies the bounded VAL-067 correction while preserving the passive dry/wet architecture, all board mounts and the outline. It does not resolve the independent buffered-loop headroom, high-voltage spacing or three-board chassis work.

## Exact implementation

| Reference | Exact part | Implementation |
|---|---|---|
| D603/D604 | Vishay BZX55C27-TAP | Opposing series, common anodes WET_Z_JOIN; cathodes WET_AC and GND. Both glass-body bands face pad 1. |
| R616 | Vishay PR01000101000JA500 | 100 ohm, 1W at70C, **5%** pulse-rated PR01. The previous generic 1%/0.25W assumption is superseded. |
| R618 | Yageo MF0207FTE52-1M | Unchanged1M value and connection; exact0.6W/350V part synchronized. The former250V requirement was insufficient under the expanded fault screen. |

Manufacturer sources are the retained [BZX55 PDF](../wet-protection/sources/Vishay-BZX55.pdf), page5, and [PR01 PDF](../wet-protection/sources/Vishay-PR01.pdf), pages9/16. Sourcing and electrical limits remain in [VAL-067 review](../wet-protection/review.md). This is exact Vishay identity; a different manufacturer's BZX55 is not automatically interchangeable.

## Hole and assembly geometry

Both new footprints use12.7mm hand-formed pitch,1.8mm copper pads and0.9mm round finished-hole targets. BZX55 has0.6mm maximum round leads,3.9mm maximum glass length and1.7mm diameter. PR01 has0.63mm maximum round leads,6.5mm body,8mm coated length and2.5mm diameter. No oval slot is appropriate for these round leads. With a provisional minus0.1mm finished-hole tolerance, diametral insertion allowances are0.20mm and0.17mm respectively. Nominal annular ring is0.45mm; finished-hole tolerance and drill registration still require the fabricator's acceptance.

R616 pin2 stays at141.16,60mm; pin1 moves from131 to128.46mm. This gives2.35mm between each pitch endpoint and the maximum coated PR01 end, before hand forming. Diode body-end-to-hole-center length is4.4mm; this does not independently prove the datasheet's controlled lead temperature. R618 retains its0.8mm holes and10.16mm pitch. Check actual parts and lead forming before fabrication.

## Verification

`tools/check.py` independently compares source rows, native connected-pin partitions, declared object deltas, rendered pages and exported Excellon hits. It rejects an antiparallel diode negative control. The only electrical addition is the two-diode shunt and its internal common-anode node. Existing component values and signal paths are preserved.

Current results:20 other native files byte-identical;17 of18 schematic pages pixel-identical; one unchanged existing GND/PE naming warning; zero Reverb DRC findings and zero opens under the **existing** rules.140 prior drill hits unchanged, four new diode holes, two resized R616 holes. All mounts/outline preserved. Eight added0.4mm straight/45-degree track segments; the new routes have45-degree bends, not a right-angle dogleg. Existing routing elsewhere is not requalified by this statement. The signal/chassis bond cut-wire negative control is refreshed separately.

The independent native source/netlist comparison must also pass. A192-case linear loading sweep extends the prior normal-audio screen to the PR01's5% plus temperature endpoints93.8125–106.3125ohm. Maximum gain difference from100ohm is0.000193552dB; maximum combined wet-node amplitude is19.186495V, below the20V allocation. This is a passive loading check with ideal sources, not an IC stability or full-amplifier simulation. VAL-067's capacitor-energy and pulse-resistor bounds remain applicable because all relevant nominal values/pins are preserved. Its direct diode-capacitance peak, relay arcing/bounce/contact-life and full-system fault exclusions remain open.

## Visual review and remaining gates

The07c branch is wired directly from C607/R617/R618's shared node through the opposing diode symbols to ground. Horizontal reference/value labels and a nearby note explain the common-anode topology and resistor ratings. The lower diode's initially overlapping fields were repositioned; inherited resistor supplier fields were replaced with the actual part identities or explicit unknowns. Board silkscreen shows both diode cathode bands.

DigiKey China has own indexed exact-part listings and quantity-one evidence; no live stock or Shanghai-address checkout confirmation is claimed. The selected BOM's approximately10.09RMB diode/resistor subtotal uses those dated indexed prices and excludes R618, taxes/freight. No purchase or supplier contact occurred.

Before release: finish voltage-specific clearance/creepage and connector selection, actual contact-life/fault checks, full power sequencing and loop/expression integration, remaining board routing, the requested three-board physical arrangement, populated CAD and measured drill body/reach access. Current native board remains an engineering draft; all six scopes remain incomplete.
