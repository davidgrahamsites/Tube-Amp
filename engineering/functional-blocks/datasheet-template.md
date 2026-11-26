# <stable block ID> — <one functional purpose>

Status: DRAFT / SIMULATION-QUALIFIED WITH LIMITS / BENCH-CHARACTERIZED / RELEASED.
Revision/date/owner: <...>. Compatible source revision and hash: <...>.
This template is not a completed datasheet; replace placeholders with evidence
or an explicit unknown. Never turn a typical value into a guaranteed limit.

## Function and boundaries

One job, signal/control flow, included circuit references and excluded jobs.
Link readable schematic, editable source, PCB region or board, exact BOM,
manufacturer datasheets, test fixtures and results. Name shared dependencies
(supply, reference, ground, feedback, cooling, mute timing). Distinguish logical
module boundaries from physical PCB boundaries.

## Pin and interface definition

| Port/pin | Direction | Function/net | Reference/return | Connector and mate | Insulation/contact requirement |
|---|---|---|---|---|---|
| <...> | input/output/power/control | <...> | <...> | <exact parts> | <...> |

Specify polarity, phase, DC coupling, cable shield termination, mating order,
wire and crimp requirements, permissible cable length/capacitance and whether
connection or disconnection while powered is supported.

## Electrical and operating characteristics

| Parameter | Minimum | Typical | Maximum | Unit | Conditions/corners | Evidence type and link |
|---|---:|---:|---:|---|---|---|
| Supply voltage and ripple | | | | V | <frequency, load, temperature> | |
| Supply current per rail | | | | A | <idle, signal, startup, overload> | |
| Input DC range and signal swing | | | | V | <peak/RMS definition> | |
| Input impedance | | | | Ω | <frequency and control settings> | |
| Output DC offset and signal swing | | | | V | <load and distortion> | |
| Output impedance / source and sink current | | | | Ω / A | <frequency> | |
| Resistive and capacitive load limits | | | | Ω / F | <stability condition> | |
| Gain, polarity and phase | | | | V/V, dB, degrees | <controls/frequency> | |
| Bandwidth / frequency response | | | | Hz, dB | <treble response included> | |
| Noise and distortion | | | | specified units | <bandwidth/weighting/input/load> | |
| Clipping and overload recovery | | | | V / s | <specified stimulus> | |
| Dissipation and temperature | | | | W / °C | <ambient, ventilation, mounting> | |

Separate **recommended operation** from **absolute maximum / damage limits**.
Include component tolerances and part/model applicability. Supply-current
budget must include local bypass/bleeders, controls, sockets/adapters and
transient demand; state which currents may flow into a rail as well as out.

## Required and preferred companion blocks

| Interface | Required allowable range | Preferred characteristics | Compatibility calculation / margin | Failure if violated |
|---|---|---|---|---|
| Upstream signal source | <level, DC, impedance, bandwidth> | <headroom/loading margin> | <...> | <...> |
| Downstream load | <R, C, signal/DC range> | <...> | <...> | <...> |
| Power supply | <V, ripple, current, sink ability, sequencing> | <...> | <...> | <...> |
| Control/mute | <levels, thresholds, drive, timing, default> | <...> | <...> | <...> |

Do not require universal impedance matching: describe the actual need for
voltage bridging, a specified load, or transformer impedance transformation.
Check loading effects on gain, tone, noise and stability. A physically mating
connector alone does not establish compatibility.

## Startup, shutdown and fault behavior

Allowed supply order, ramp rates, brownout behavior, mute/enable sequencing,
unpowered signal injection, rail backfeed, hot-plug limits, discharge times,
short/open load, clipping and defined faults. Specify required external
protection and what this block cannot protect. Cite tested scenarios; do not
generalize a limited fixture into a universal fault guarantee.

## Physical and implementation requirements

Dimensions, mounting, sockets/extraction, heat and drill-tool envelopes,
keepouts/voltage clearances, critical component placement, return paths,
shielding and grounding, sensitive/high-current loops, cable routing and
required heatsinking. Document layout constraints that a reused schematic
alone would fail to preserve.

## Verification and reuse checklist

For each claim retain source/model revision, setup, stimulus, load, temperatures,
supply corners, result and margin. Label measured vs simulated explicitly.
Link unresolved checks and acceptance criteria. Record regression checks that
must be repeated if a component, supply, source, load, PCB or enclosure changes.

The final companion compatibility matrix uses one row per actual connected
port pair: producer revision/output envelope → consumer revision/allowed
envelope, source/load interaction, return/control/power dependencies, numerical
margin, evidence and PASS / FAIL / UNKNOWN. UNKNOWN is not release acceptance.

## Adapter applicability, when relevant

State the precise mismatch bridged: level, impedance, DC bias, balanced versus
unbalanced signals, power or control interface. Specify both interface envelopes,
conversion/transfer behavior, noise, bandwidth, headroom, stability, latency if
applicable, and protection. Validate both connected pairs and the complete chain.
An adapter is itself a versioned block with the same evidence requirements.
