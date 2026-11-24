# FC6136 power-capacitor fit rejection

Owner: PCB integration / component selection. Reviewed November 24, 2026. Scope: candidate FC6136 against the current Power board, not all-component fit acceptance.

P057 mixed the CRC candidate identity with the old Panasonic dimensional requirement. The coverage entry is corrected to distinguish the baseline minimum voltage requirement from the CRC candidate's actual dimensions/rating. The native board still contains `Renegade_Whole:Panasonic_EZPV60506MTC` at C12, C13, C25 and C26. It has not been relabeled as CRC or silently rerouted.

The retained [CRC approval drawing](../../../component-selection/evidence/CRC-FC6136.pdf), page 1, was visually inspected. It states 50 microfarads, 900 VDC, body W57.5 × T35 × H50 mm with ±1 mm tolerances, pitch 52.5 ±1 by 20.3 ±0.5 mm, nominal round leads of diameter 1.2 mm and length 4 ±1 mm. The drawing extraction is the editable [fit contract](../../../component-selection/fc6136-fit-contract.json). The part remains a candidate; its electrical suitability is not established merely by voltage and capacitance.

| Feature | Current native geometry | CRC candidate | Result |
|---|---|---|---|
| Four-pad grid | 52.5 × 10.2 mm | 52.5 × 20.3 mm nominal | Row pitch incompatible on all four capacitors |
| Round drilled holes | 1.8 mm | 1.2 mm nominal lead, diameter tolerance unstated | Hole acceptance pending; enlarging holes cannot repair the pitch mismatch |
| F.Fab body rectangle | 58 × 26 mm | Maximum body 58.5 × 36 mm | Native outline understates candidate width/depth |
| Candidate height | Not qualified by native 2D drawing | Maximum 51 mm before installation allowance | Must enter populated chassis/thermal fit |

Even zero-diameter straight leads could span at most 10.2 + 1.8 = 12.0 mm between the outside edges of the present row holes, below the candidate's minimum 19.8 mm row pitch. This is a definite rejection for straight insertion, independent of the missing lead-diameter tolerance. Do not bend these short leads to force a match.

Projecting maximum candidate bodies onto the existing four-pad centroids produces two overlap pairs: C26/C13 and C25/C12, each 0.95 mm in the row direction. This is an explicitly centered, same-orientation placement screen; it is not a complete body-to-pin tolerance stack or a check of every neighboring component. Merely replacing the footprint would not repair placement. Extra spacing, support, copper clearances, harness and tool access are still needed.

## Resolution and next work

The corrected coverage record blocks interpreting FC6136 as a drop-in replacement. [The machine-readable receipt](fc6136-fit.json) reports `candidate_can_drop_into_native: false`, five passing diagnostic controls and unchanged native board bytes. Successful audit execution means the defects were detected, not that the capacitor fits.

Before adoption: confirm terminal grouping and maximum lead diameter; choose finished-hole/slot geometry using the fabricator's actual tolerances and documented insertion allowance; create and visually inspect a new source-backed footprint; repack the Power block using the full body/support envelope; reroute affected copper and rerun pad/net parity, DRC and populated chassis checks. The drawing does not require oval leads for this part. Other parts still need their own round/rectangular/oval lead checks. No candidate fabrication footprint is generated from missing tolerances.

Reproduce with KiCad's bundled Python:

```sh
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 engineering/whole-amp/pcb-measured-r/tools/check_fc6136_fit.py
```

The KiCad binding emits its existing wxApp diagnostic during read-only loading; the script completes, checks the expected four footprints and preserves the board hash. No manufacturing release is made.
