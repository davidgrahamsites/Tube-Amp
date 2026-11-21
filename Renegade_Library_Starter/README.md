# Renegade — KiCad library starter

**Revision 0.1 — library preparation only. Not a construction schematic.**

This package registers three newly authored, generic, off-board symbols in a project-local KiCad library. It also contains a preview schematic and the component-library plan for the proposed 220 V / 50 Hz, tube-reverb modification.

## Open the library

1. Extract the entire folder, preserving the `libraries` subfolder and `sym-lib-table`.
2. Open `Renegade_Library_Preview.kicad_pro` in KiCad. The files use older native formats intended to be readable by KiCad 9 and newer, but **they have not been opened or tested in the KiCad application**.
3. In the Symbol Editor, browse `Renegade_Custom`. Alternatively, open the preview schematic. It contains three disconnected example symbols, not an amplifier circuit.

The library table uses `${KIPRJMOD}` rather than an absolute path. No global KiCad configuration, existing library, or user project is overwritten. There is no executable installer to run.

For a later amplifier project, place the custom library in that project's folder and add the entry in `sym-lib-table` to its project-specific symbol-library table. **Do not overwrite an existing table containing other project libraries.**

## Included now

- `libraries/Renegade_Custom.kicad_sym`: a four-terminal spring tank, an isolated reverb transformer, and a TRS control port. Each is marked off-board and has no assigned PCB footprint.
- `Renegade_Library_Preview.kicad_pro` and `.kicad_sch`: a native project and explicitly nonfunctional symbol preview.
- `sym-lib-table`: registration of the custom library in this project only.
- `docs/Library_Manifest.md`: standard-library candidates, custom-library boundaries, and outstanding verification.
- `docs/Design_Decisions.md`: proposed reverb and footswitch behavior.
- `tools/verify_bundle.py`: basic syntax, path, and identifier checks using Python's standard library.
- `docs/Validation.txt`: the checks actually performed and their limitations.

## Deliberately not included

The original amplifier has **not** been redrawn or electrically revised in this package. There is no finished reverb circuit, footswitch circuit, PCB, BOM for ordering, SPICE model, mains safety approval, or manufacture-ready footprint library.

The standard KiCad libraries are **not downloaded or redistributed** in this archive. Install the official libraries supplied with the same KiCad major version as your application. The manifest identifies the libraries to use; it is not evidence that those libraries are installed on your computer.

Supplier-specific footprints remain unassigned until part numbers, terminal mappings, and mechanical drawings are confirmed. A schematic symbol that looks right does not establish PCB compatibility. No files in this package should be used to order a PCB or wire a live amplifier.

## Symbol terminal conventions

**SpringTank_4Terminal_Offboard:** logical terminal 1 = input signal; 2 = input return; 3 = output signal; 4 = output return. These numbers are project identifiers, not numbers stamped on a tank. The two returns are not joined by the symbol. Tank-case bonding, connector insulation, mounting orientation, and transducer impedances must be checked against the selected supplier's documentation. No fifth case lug is assumed.

**ReverbTransformer_1P1S_Offboard:** P1/P2 are the primary pair and S1/S2 the secondary pair. These labels are not supplier wire colors or physical pin numbers. Winding phase, ratio, DC-current capability and insulation ratings are unspecified. No SPICE transformer behavior is encoded.

**TRS_Control_Port_Offboard:** T = tip/channel, R = ring/reverb, S = sleeve/control return. This represents an off-board connection, not a selected jack model. Normal contacts and plug-detect contacts are not modeled. TRS is an assumption pending clarification of the user's term “TLR.”

## Validation and safety

Only generic file-structure, relative-path and pin-identifier checks were run. The KiCad application and `kicad-cli` were unavailable in this working environment, so no application-open, ERC, rendering, DRC, or circuit simulation test was run. Passing the included script is **not** proof that KiCad will load the project or that a circuit is correct.

The completed tube amplifier will contain hazardous mains and high-voltage circuitry. It requires separate review of isolation, protective earth, fusing, capacitor discharge, component voltage ratings, construction spacing, wiring and commissioning. The proposed footswitch cable is restricted to low-voltage control; tube plate voltage and mains must not be routed to it.

## Official references

KiCad library downloads: https://www.kicad.org/libraries/download/

KiCad project-specific libraries and `${KIPRJMOD}`: https://docs.kicad.org/9.0/en/eeschema/eeschema.html#managing_symbol_libraries

KiCad native symbol format: https://dev-docs.kicad.org/en/file-formats/sexpr-symbol-lib/

KiCad native schematic format: https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/

See the library manifest for additional primary sources. No third-party CAD download or plugin is required for the three included custom symbols.
