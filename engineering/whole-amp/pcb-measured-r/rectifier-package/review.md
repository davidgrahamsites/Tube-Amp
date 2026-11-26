# Selected HV rectifier package reconciliation

November 26, 2026. Owner: PCB integration. D3–D6 now consistently identify the already-selected Vishay BY255P-E3/54 in the canonical source, connectivity record, readable supply schematic and native Power PCB. The old source said 1N4007 and the board said STTH112 with a DO-41 package. The two-series-diodes-per-half-winding topology is unchanged.

## Package and assembly contract

The retained Vishay document 88838, revision 19 December 2025, specifies DO-201AD maximum body 9.5 × 5.3 mm and round leads up to 1.32 mm. The custom footprint uses 30.48 mm pitch, 1.7 mm round plated holes and 2.6 mm pads. With the proposed ±0.1 mm finished-hole tolerance, the minimum hole leaves 0.28 mm diametral lead allowance; the largest hole leaves 0.4 mm annulus before registration tolerance. These remain fabrication requirements to confirm with the board supplier. Cathode band and square pad are pin 1.

The four diodes are vertical in the board plane, in the lower-left Power region. R501/R502 and two provisional interface headers move to maintain the existing HV clearance rule. No mounting hole or board outline changes. The 3 mm body standoff and 8.3 mm installed height are provisional assembly envelopes, not thermal approval. Lead forming must not stress the body seals. Maximum body envelopes and the new R501/R502 positions are exported in results/package-envelopes.json. Those positions supersede the historical FMP200 placement evidence, while its hole/body geometry is preserved.

## Native validation

The guarded candidate was exported through KiCad 10.0.6 and independently compared with baseline 061a72c. All 145 net partitions are preserved. ERC retains one existing GND/PE warning. Power DRC retains 12 existing findings and 39 unconnected items, with no new finding under unchanged rules. All 20 other native files are byte-identical. Only schematic page 8 changes its four diode value labels; the other 17 page rasters are identical. The supply page and board plot were visually inspected before adoption.

Excellon comparison accounts for all 79 holes: eight diode holes move and grow, and six supporting-component holes move; the other holes are unchanged. The exact 17 replacement segments on five declared nets are checked, with all other native board content preserved outside the declared footprint edits. Width remains 0.6 mm; this repair does not qualify ampacity. The mechanical inventory was refreshed against the adopted board hash. It remains an outline/mount inventory, not a populated assembly.

Factories and contracts are separate from evidence. tools/prepare.py produces a new guarded candidate only; tools/export_native.py saves baseline/candidate native exports; tools/check.py verifies the adopted files against results/integration.json and the declared baseline. Re-running a historical package check against later native edits is not evidence of a new electrical defect: use the revision-bound chain and current integration check. No broad regeneration of native boards was performed.

## Ratings and remaining gates

The existing selection review remains authoritative for the conditional 1300 V reverse-voltage screen and historical China sourcing. The manufacturer's 3 A rating, thermal resistance and surge rating depend on their stated mounting, temperature and waveform conditions. A 30.48 mm footprint provides lead-forming room but does not establish the datasheet thermal fixture. The generic rectifier simulation is not a BY255 manufacturer model. Actual transformer regulation/leakage, repetitive pulse RMS/average loss, startup/fault energy, hot junction temperature and transient reverse voltage remain to qualify. No prior simulation has been relabeled as qualification of the new package.

The November 11 LCSC observation is retained as dated evidence, not fresh stock or a delivered quote. No purchasing or fabrication submission occurred. Remaining routing, three-board consolidation, full harness/heatsink/tube envelopes, cabinet fit and drill-body/bit access are open. Objective 6 is incomplete; no fabrication release.
