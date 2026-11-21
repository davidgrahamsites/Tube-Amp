# Measured-resistance update — 20 November 2026

Owner: reverb electrical integration. Revision: 600R-1, engineering draft.

## Electrical result

The factories now read coil DC resistance from the canonical [received-hardware register](../../mechanical/fit-register.json). The user reported 76 Ω input and 235 Ω output using the DT9205A 2k range. Measurement provenance and the register hash are embedded in [results.json](../simulation/results.json). Earlier assumed-resistance results remain in [the historical run folder](../simulation/prior-assumed-2026-11-19/CONTEXT.md).

The rerun completed 18 dry/wet AC cases, 12 input-coil sensitivity cases and six large-signal transient cases. All eight existing scoped criteria passed: two checks of dry gain remaining constant with wet control/mute, plus six driver-headroom checks. This is not eight tests of tank safety.

The nominal surrogate still assumes the seller's 600 Ω input and 2250 Ω output impedances apply at 1 kHz. With measured DC resistance, the resulting series inductances are 94.724 mH and 356.140 mH. These inductances are calculated assumptions, not measurements.

For a 20 V peak source behind 100 kΩ, full send trim and the nominal surrogate, input-coil current peaks at **6.728 mA RMS at approximately 356 Hz**. Corresponding modeled input-coil copper loss is about 3.44 mW; maximum normal-signal R605 loss is 9.96 mW. Across all sensitivity cases, including older assumed resistances, the largest current is 7.996 mA RMS. Neither figure establishes allowable drive current or authorizes full trim on the real tank.

The [drive-response plot](drive-response.png) and [numerical data](drive-response.json) retain the frequency dependence. Models do not establish spring acoustic transfer, actual wet loudness, distortion onset, coil thermal limits, real power-supply behavior, tube/output-transformer performance or cabinet fit. The expression-pedal circuit remains pending.

## Parts and PCB progress

Selected two exact KNSCHA film capacitor parts covering 13 positions. The [part dossier](../../../component-selection/evidence/lv-film-selection-2026-11-20.md) links manufacturer drawings, voltage/temperature conditions and dated mainland purchasing evidence. Selection now covers 117 positions across 36 MPNs and 48 of 127 groups. Supplier prices/stock retain their original dates; no fresh stock claim or purchase was made.

A separate [four-board integration draft](../../pcb-measured-r/CONTEXT.md) preserves the historical native boards. It applies 93 footprint replacements/additions and reconciles the reverb to 600R-1, including R618 and the passive dry path. New exact film-capacitor footprints use maximum body dimensions and documented lead geometry.

Final native pad/net checks cover 444 numbered pads across all four boards, including 10 explicitly unconnected pins. No mismatches were found against the current electrical contract. This is a contract audit, not KiCad paired-assembly schematic parity. Source boards remain unchanged. See [hashed checks](../../pcb-measured-r/review/final-checks.json).

| Draft board | KiCad DRC violations | Unconnected items |
|---|---:|---:|
| Main | 0 | 103 |
| Power | 0 | 38 |
| Control | 0 | 95 |
| Reverb | 0 | 0 |

KiCad 10.0.6 ran the checks after actual courtyard, redundant-via and label corrections. No reported finding was suppressed to obtain these results. The [reverb rendering](../../pcb-measured-r/review/Reverb-layout.svg) was inspected. The other boards need routing after package changes. Provisional outlines, unselected parts and missing expression controls prevent fabrication release. R605 procurement/package qualification and R616 fault rating remain open.

## What AC impedance testing changes

It replaces an assumed electrical load with measured impedance versus frequency and phase. That informs driver voltage/current and headroom, R605's series isolation value, low-frequency shaping and coupling capacitance, and recovery-input loading/noise. It does not establish a maximum safe current, acoustic decay or final wet gain by itself. Keep the existing cabinet and tank; refine the surrounding electronics from evidence.

Next checks: acquire low-level AC characterization when equipment is available; resolve remaining exact packages and protection ratings; implement expression control; complete integrated board routing and populated cabinet-fit review. No equipment purchase is required to continue the independent work.
