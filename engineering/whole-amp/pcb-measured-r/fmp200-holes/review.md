# FMP200 insertion-clearance correction

The 13 existing Main/Power FMP200 footprints now use 0.9 mm round holes and 1.8 mm pads. This closes an insertion-clearance defect; it does not qualify the resistor stress or release either board for manufacture.

## Evidence and geometry
The [manufacturer FMP V9 datasheet](../../../component-selection/evidence/Yageo-FMP.pdf), January 13, 2026, pages 2–3, specifies standard FMP200 leads of 0.55 ±0.05 mm and a 9 ±0.5 mm by 3.9 ±0.3 mm body. These dimensions apply to the standard lead option, not every available suffix. With the proposed ±0.1 mm finished-hole allocation, the new minimum hole is 0.8 mm: 0.2 mm diametral allowance over the maximum 0.6 mm lead. A maximum 1.0 mm hole leaves 0.4 mm annular ring before registration. The fabricator must confirm its actual tolerances.

The pad-end courtyard and silkscreen lead starts were enlarged to match. Misleading generic 0.5 W tags were corrected to the FMP200 2 W at 70°C identity. Formed pitch remains 15.24 mm; all placements and nets remain unchanged. Nominal body drawings remain nominal; the courtyard contains the maximum body. Watts alone do not determine package suitability: voltage, local temperature, pulse/fault stress and lead dimensions still apply.

## Verification
[Independent checks](results/checks.json) compare complete parsed native trees against baseline a9219369401b868150e0a1bfe19516dc134bc848 after undoing only the permitted edits. All 22 circuit/schematic and other-board files match that baseline. Tracks, vias, mounts and board outlines are unchanged. A disposable baseline replay produced all three outputs byte-for-byte identically; see [receipt](results/replay.json).

Native Excellon exports confirm exactly 18 enlarged Main holes and 8 enlarged Power holes, with total drill counts unchanged at 178 and 79. Every other drill hit is unchanged. Before/after native DRC reports are identical: Main has 43 existing findings and 105 unconnected items; Power has 12 existing findings and 39 unconnected items. There are zero new findings, not zero total findings.

The [package envelopes](results/package-envelopes.json) carry manufacturer maximum body dimensions at the native positions. Standoff and installed height remain null until assembly design establishes them. Refreshed socket and mechanical inventories reference the current native hashes; socket checks still pass their limited body/drill comparisons, and missing 3D models remain explicit. These checks do not establish populated cabinet fit.

## Remaining work
Confirm finished-hole/registration limits and purchased suffixes; establish standoff and thermal clearances; qualify operating, transient and fault stresses; complete routing and three-board consolidation. The 46 mm chuck measurement alone cannot close screw access. Objective 6 remains incomplete.
