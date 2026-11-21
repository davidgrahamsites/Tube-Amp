---
id: DEC-010
type: decision
domain: schematic
status: selected
updated: 2026-11-21
---
# Retain the original electric tube input without an added buffer

## Question and scope
Does the original electric input need a JFET-input op-amp buffer for conventional passive magnetic single-coil and humbucker pickups? User instruction, November21: check the actual circuit, keep the electric build simple and log the decision. This applies to electric-guitar-amp only. The separate acoustic buffer requirement remains in force.

## Task card
Owner: integration agent. Inputs: preserved OpenValve/AX84 Renegade v1.2 slide1 and current600R-1 native circuit. Outputs: traced input path, repeatable small-signal loading calculation and this decision. Dependencies: native KiCad export and original source image. Operations: inspect source, export native nets, check pins/values and calculate the resistive limit. Human evidence: eventual listening, noise and overload checks with actual pickups/cable. Done condition: determine whether loading requires an added buffer; preserve explicit limits. Effort: one bounded L0/L1 review; no full amp simulation or PCB regeneration required.

## Evidence
- [Original schematic image](../../sources/original-ppt/slide-01.png), visually inspected in this review: J1 → R1 68k → relay1a → either clean input with R2 1M or dirty input with R10 1M, each grid leak to ground.
- [Current circuit contract](../../engineering/whole-amp/reverb-600/circuit.json).
- [Native routing sheet](../../engineering/whole-amp/reverb-600/cad/03_routing.kicad_sch), [clean sheet](../../engineering/whole-amp/reverb-600/cad/01_clean.kicad_sch), [dirty sheet](../../engineering/whole-amp/reverb-600/cad/02_dirty.kicad_sch).
- [Calculation and native check results](../../engineering/whole-amp/reverb-600/review/electric-input-loading-2026-11-21.json); includes SHA256 hashes of the circuit/native sheets and fresh exported netlist.
- [Repeatable checker](../../engineering/whole-amp/reverb-600/tools/check_electric_input.py).
- [BOSS manufacturer explanation](https://articles.boss.info/why-buffers-are-important-for-great-tone/), consulted November21: passive pickup/cable loading, buffering after the buffer location, and onboard buffering of active pickups. This supports the cable-placement discussion, not a claim that our complete amp is validated.

## Findings
The fresh KiCad10.0.6 XML export confirms J1.T→R1.1, R1.2→K1.4, K1.6→R2.1/V1.2 and K1.8→R10.1/V2.2. Both resistor bottom terminals and J1 sleeve/normal contact are grounded. The source uses a changeover contact, selecting only one grid input. R2 and R10 are therefore NOT a parallel500k load in either steady channel state.

With a plug inserted and negligible grid current, the low-frequency resistive input is 68k + 1M = 1.068M ohms. The grid receives 1M/(1M+68k) = 0.9363 of the jack voltage, or approximately −0.57dB. This is a conventional high-impedance tube input suitable in principle for both passive magnetic pickup types. There is no demonstrated low-resistance loading defect requiring an active buffer.

The stored source-resistance examples are deliberately limited voltage-divider calculations. A pickup is frequency-dependent and inductive; winding DC resistance is not its audio-band source impedance. Do not label those examples as measured Strat/Tele/LesPaul responses. Actual high-frequency loading also includes cable, wiring and tube Miller capacitance. Thus 1.068M is not the complete input impedance at every frequency, and different pickup/cable combinations will retain different resonances and tone.

A buffer at the amp input could change that interaction, but adds an active stage, supply dependence, protection and additional clipping/noise considerations. A unity-gain buffer does not reduce a hot pickup's voltage or cure first-triode overload. The channel volume/gain controls occur after the first triode, so turning them down does not necessarily prevent that first triode clipping. Exact clean input headroom remains unqualified and must be checked once bias/supply/tubes are fixed. If necessary, assess a simple input attenuation option against real requirements then.

## Decision and authority
Engineering decision under the user's simplicity instruction: RETAIN the original J1/R1/K1/R2/R10 tube-input arrangement. OMIT an added discrete-JFET or JFET-input op-amp buffer from the electric build. No extra buffer PCB, supply branch, selector or purchasing item is introduced. This is a documented choice to preserve existing CAD, not a claim that a buffer was removed from an already implemented design.

For a demonstrated long-cable/pedal loading problem, assess an external buffer near the guitar and downstream of any pickup-sensitive fuzz as appropriate. An amp-mounted buffer does not undo the upstream pickup/cable response. Do not add one speculatively.

## Reproduce and next check
From the project root:

```sh
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli sch export netlist --format kicadxml -o /tmp/renegade-electric-input-2026-11-21.xml engineering/whole-amp/reverb-600/cad/Renegade_220V_Reverb.kicad_sch
python3 engineering/whole-amp/reverb-600/tools/check_electric_input.py /tmp/renegade-electric-input-2026-11-21.xml
```

Native input connectivity/value checks and bounded calculations support this decision. They do not establish flat frequency response, specified clean headroom, hum/RFI performance, channel-switching transients or fabrication readiness. Preserve short, shielded sensitive input wiring and review physical grid-stopper placement during socket/chassis layout; the shared pre-relay stopper requires care with the following grid leads. Revisit buffering only if a defined interface, measured loading/noise problem or new feature justifies it. Validate both channel states with the actual instruments and cable at commissioning.

Follow-up21November: [VAL-015](VAL-015-electric-headroom-and-parts.md) records the completed scoped hot-signal headroom sweep. The no-buffer decision remains; assumed large sine signals show progressive tube distortion and do not establish an actual pickup limit.
