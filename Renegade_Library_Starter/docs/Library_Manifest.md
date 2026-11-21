# Component-library manifest

**Status: planning inventory, not a finalized parts list or completed installation.**

The two custom reverb symbols and generic control port are bundled. Standard libraries listed below are to be supplied by the official, version-matched KiCad installation. Exact symbol and footprint names must be checked in that installation before placing production components.

| Circuit item | Planned library / symbol | Status and required check |
|---|---|---|
| Existing 12AX7 and added 12AX7 | Official `Valve`, ECC83 symbol | Official symbol family identified. Confirm tube pin numbering; do not assume its default footprint matches a Chinese socket. |
| Added 12AT7 reverb driver | Official `Valve`, ECC81 symbol | Official symbol family identified. Operating circuit and heater load calculation are not included here. |
| Existing EL34 output valves | Official `Valve`, EL34 symbol | Official symbol family identified. Socket terminals and physical orientation remain to be verified. |
| Tube sockets | Official `Valve` footprints only when the selected socket matches | Prefer off-board/chassis treatment where applicable; no socket footprint is approved in this starter. |
| Hardware debounce | Official `74xx`, 74HC14 symbol candidate | TI Schmitt-trigger part proposed. Choose actual package/order code and verify every power and signal pin. |
| Two toggle latches | Official `74xx`, 74HC74 symbol candidate | TI dual flip-flop proposed. Include deterministic reset; do not leave unused logic inputs floating. |
| Channel/reverb relays | Official `Relay`, with `G5V-2`/split symbol as a candidate | Omron G5V-2 is a documented candidate, not a confirmed procurement choice. Match voltage, contact arrangement, switching ratings, coil current and footprint. |
| Relay drivers/protection | Official `Transistor_BJT`/`Transistor_FET`, `Diode`, `Device` | Actual driver and clamp parts are not selected; no footprint assigned. |
| Logic/control power | Official `Regulator_Linear`, `Device`, `power` as applicable | Isolated supply architecture, regulation, reset and decoupling remain to be designed. |
| Resistors, capacitors, pots, switches | Official `Device`, `Switch` | Values, power/voltage ratings and body/lead dimensions must match the final circuit and parts. |
| Main/output transformers and choke | Official `Transformer` / `Device` or new project symbols after specifications | Main primary must be suitable for 220 V, 50 Hz. Exact winding arrangement, ratings and supplier lead mapping remain open. |
| Spring-reverb tank | Bundled `Renegade_Custom:SpringTank_4Terminal_Offboard` | Generic symbol only. Approved direction: the previously discussed MAGT0034A/L2AB3C1B-style long tank; current stock and exact specifications are not reverified by this package. |
| Reverb transformer | Bundled `Renegade_Custom:ReverbTransformer_1P1S_Offboard` | Generic symbol only. Previously discussed 23–25 kΩ : 8 Ω class remains an electrical target, not a purchase approval. Verify DC operation and insulation. |
| TRS control jack | Bundled `Renegade_Custom:TRS_Control_Port_Offboard` | Generic functional connection. Actual jack, lug map, insulation and insertion/detection behavior remain open. |
| RCA connections / wiring headers | Official `Connector` / `Connector_Generic` | Actual physical models and wiring interface not selected. |

## Custom PCB libraries

No `.kicad_mod` footprints are supplied because no nonstandard board-mounted component has yet been dimensionally confirmed. The three bundled custom symbols represent off-board parts. There is therefore no fabricated or empty footprint library advertised as complete.

When a part needs a custom footprint, obtain its manufacturer drawing, check the bottom/top-view convention, compare every pad number with the symbol, and make a 1:1 fit check against a real sample. Record the source and revision with the footprint. Keep that `.pretty` library inside the final project and register it with a project-specific `fp-lib-table`.

## Source provenance

The three custom symbols were newly authored for this starter; they were not downloaded from a manufacturer or presented as manufacturer-verified CAD.

Official library distribution and current repositories:
https://www.kicad.org/libraries/download/

Official historical symbol indexes used to identify existing symbol families (these are not the latest library downloads):
https://kicad.github.io/symbols/Valve.html
https://kicad.github.io/symbols/Relay.html

Texas Instruments SN74HC14:
https://www.ti.com/lit/ds/symlink/sn74hc14.pdf

Texas Instruments SN74HC74:
https://www.ti.com/lit/ds/symlink/sn74hc74.pdf

Texas Instruments SN74HC74-Q1 application example for converting a debounced momentary button to a toggle:
https://www.ti.com/lit/gpn/sn74hc74-q1

Omron G5V-2 manufacturer data (candidate only):
https://components.omron.com/system/files/datasheet_pdf/K046-E1.pdf

KiCad project-local library management:
https://docs.kicad.org/9.0/en/eeschema/eeschema.html#managing_symbol_libraries
