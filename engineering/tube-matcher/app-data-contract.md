# Tube inventory and macOS app — interface v0.1

October 4, 2026. **App design and data contract only; no working app or BLE link yet.** The user asked whether measurements can be tracked and sent to an app we write here. Yes: logged results can be synchronized into a Mac inventory without changing the instrument's measurement/protection architecture.

## Product and screens

Propose a native Mac application using [SwiftUI](https://developer.apple.com/documentation/swiftui) and [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth), with a local database. Actual minimum macOS version, packaging and signing depend on the user's Mac and available development tools. First implement JSON file import; add a BLE adapter using the same record format when hardware exists. Transport must not own the matching logic.

| View | What the user can do |
|---|---|
| Inventory | Search tube ID, family, maker/variant, bin, location and notes; optional photograph. |
| Tube detail | View both 12AX7 sections or one EL34, raw curves, current/gm/bias, conditions/calibration and explicitly unperformed tests. |
| Compare | Overlay compatible curves and calculate uncertainty-aware pair/section matching; include candidates from adjacent bins. |
| History | Compare repeated tests of the same bottle under compatible conditions; separate profile changes from possible aging. |
| Amp sets | Save dated tube-ID assignments to V1–V6, amp/circuit revision, commissioning/bias measurements and user observations. |
| Export | Preserve raw versioned JSON; export flat CSV for analysis; retain bin/matching rule version with recommendations. |

Operating hours are manual annotations unless a separate amp usage counter exists. The tester cannot know them by itself. A changed tube set creates a new dated assignment, preserving previous sets.

## Transfer and recovery

```text
Controller samples → Pi commits immutable run → BLE result manifest
→ Mac requests unseen run / missing chunks → byte count + SHA-256 check
→ record validation → transactional import by run UUID
→ inventory / history / curves / derived matching
```

Both devices retain results. Live status is separate from stored runs. BLE interruption does not erase the Pi's record; Mac resumes or restarts transfer by run/chunk identity. Do not import a fragmented record until the full digest passes. Same run UUID/digest received twice is idempotent. Same UUID/different bytes is a conflict, not an overwrite. Incomplete runs may be displayed but are ineligible for qualified matching. Hash original transfer bytes; reformatted exports have a different digest.

The Pi owns acquisition records. The Mac owns editable labels, notes and amp-set assignments. Keep annotations separate; initial version can make annotation editing Mac-only. Raw measurements never change when a bin width or matching threshold changes: derived recommendations are recalculated and identified by rule revision.

## Entities and record conventions

| Entity | Stable identity / contents |
|---|---|
| Tube | Tube UUID plus editable sticker ID, family/markings and notes. Operator links the ID to the physical bottle. |
| Run | Run UUID, tube UUID, instrument/firmware revision, UTC time, clock validity, sequence, profile ID/hash, calibration ID, completion state and data origin. |
| Section | A/B/P identifier, actual electrode values/current components, raw slopes/curve points, derived values and uncertainties. |
| Calibration | Immutable snapshot: coefficients, ranges, uncertainty, validity, date and reference equipment. |
| Assessment | Faults, health checks, stability, censored points and explicitly unavailable/unperformed tests. |
| Recommendation | Input run IDs, compatibility result, mismatches/uncertainties, policy version, bin and role. Recomputable. |
| Amp set | Amp/circuit revision and dated socket assignments, commissioning and user notes. |

- Integer `schema_version`; reject unsupported versions informatively while preserving original bytes.
- `data_origin` distinguishes `synthetic-example` and `physical-measurement`. Demo data must be visibly labeled and excluded from real inventory decisions.
- Field names carry units: `_v`, `_ma`, `_ma_per_v`, `_kohm`, `_pct`, `_s`, `_c`. Finite numbers only. Unknown is null/absent with availability status, never a misleading zero.
- Record actual electrode voltages relative to the measured cathode, not just commanded setpoints. Retain Ik/Is/Ig so derived plate current can be audited.
- Preserve raw slope/curve samples. Censored/fault points do not enter matching; save the reason and requested/measured conditions.
- Uncertainty includes absolute bounds and coverage meaning. Importing data does not confer calibration validity.
- UTC plus a separate clock-validity flag and sequence counter; an offline Pi still creates unique ordered runs even if its clock is uncertain.
- Immutable profile/calibration snapshots or synchronized content hashes accompany archival exports. Mutable profile names alone are insufficient.

The [example result](example-result.json) is a **synthetic, uncalibrated** format illustration. It is not an acquired result or complete JSON Schema and is excluded from real matching. The sample 12AX7 gm uncertainties intentionally make the 5% section-balance gate uncertain despite close central values.

## Pairing and history gates

Require compatible family/qualified variant, fixture purpose, immutable profile, valid calibration, actual electrode conditions within qualified tolerance, warm-up/stability, completed required health tests, uncensored required points and uncertainty. Explain failed gates instead of inventing a score. Initial implementation compares only common measured curve conditions; interpolation requires a later qualified policy. A profile change starts a separate trend series rather than implying sudden wear.

Architecture: **transport → validator/store → matching/history domain → views**. HV settings and permission remain in the reviewed measurement controller. The v1 Mac app receives results/status and requests transfers; it does not start HV remotely.

## Implementation and acceptance

1. Inventory, versioned JSON import, tube/run detail, compatible comparisons, history and JSON/CSV export. Check duplicate/conflicting imports, incomplete/unsupported records and demo exclusion. Reproduce analytic mismatch/uncertainty examples in `calculations.py`.
2. BLE discovery/pairing/status and resumable results. Test on actual Mac/Pi for disconnects, missing chunks, truncated/corrupt bytes, digest mismatch, reconnect, duplicate runs, unsupported protocols and uncertain clocks. No fabricated connected-device state.
3. Integrate actual acquisition after controller/hardware qualification. Add audio results when the fixture exists, keeping untested labels until then.

This interface makes app implementation concrete. Working app creation, hardware acquisition and actual BLE transfers remain uncompleted.
