---
id: DEC-006
type: decision
domain: cross-domain
status: proposed
updated: 2026-10-04
---
# Standalone EL34 / 12AX7 matcher with Pi display and BLE

## Question and scope
Design a pre-installation plug-in tube matcher/binner for two power tubes and four 12AX7s. User explicitly corrected EL84 to **EL34**, and suggested a Raspberry Pi with integrated benchtop display in addition to BLE result transfer to macOS. This instrument is a supporting project, not a change to the amplifier circuit.

## Options and tradeoffs
Prefer one tube at a time under regulated conditions, a Pi touchscreen/database, separate measurement controller and independent hardware inhibition. Keyed octal EL34 and noval 12AX7 cartridges reduce routing complexity. BLE transmits results; it does not authorize HV. A six-tube fixture adds supply/channel complexity without being necessary for initial matching.

Match EL34 current and gm at common fixed bias, then multi-point response and stability. Characterize each 12AX7 section; internal balance and appropriate gain/noise/headroom determine role suitability. Equalizing all four preamp tubes is not required. Bins retain numeric fingerprints and profile/calibration identity; adjacent bins may still contain better pairs.

## Evidence
[System design v0.1](../../engineering/tube-matcher/design.md), [source register](../../engineering/tube-matcher/sources.md), [profiles](../../engineering/tube-matcher/profiles.json), [calculation report](../../engineering/tube-matcher/calculation-report.json), and [original V4/source inspection](../../sources/original-ppt/inspection.md). Manufacturer typical values are descriptive, not pass minima. No measured tube data exist.

## Decision and authority
Tube families and desired benchtop/macOS functionality are user requirements, October 4, 2026. Pi 4/7-inch display, Pico controller, measurement electronics, supply envelope, test voltages and matching thresholds are root-agent proposals. No purchase, fabrication or energization authorized by these artifacts. Canonical amp requirements stay in the handoff.

The user asked whether test data can be tracked and sent to an app we write here. [App/data contract v0.1](../../engineering/tube-matcher/app-data-contract.md) proposes native macOS inventory/history, immutable acquisition records, local persistence on the Pi, resumable BLE and file import/export before hardware exists. The [synthetic record](../../engineering/tube-matcher/example-result.json) is excluded from real matching. No working app is claimed.

## Open questions and next check
Exact tube maker/variant; amp operating points; available bench resources; instrument budget; selected HV and guard hardware. Schematic, stress/error budgets, physical dimensions, qualified calibration and fault measurements precede hardware release. Audio noise/microphonics, working firmware/UI/BLE and amp-specific profiles remain unimplemented. See [TM-001](../../engineering/tube-matcher/task.md).
