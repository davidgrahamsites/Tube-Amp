# R605 power-package correction — 25 November 2026

Owner: PCB integration. Baseline: `306efaababa3f2b540b784946750ee91faff9552`. Scope: R605 package and its local connections, with FB-141 rating requirements retained. This is a conditional package integration, not a fully selected part or fabrication release.

R605's native 6.3 × 2.5 mm outline and 10.16 mm pitch could not represent the proposed FMP200. The current board instead uses `Yageo_FMP200_P15.24_Drill0.9`, preserving 220 ohms and the DRIVER/DRIVE_CAP pin map. Both source JSON files and the hidden schematic footprint/rating metadata agree. R605 pin 1 is now at (75.76,50) mm and pin 2 at (91,50) mm. A front-layer connection and one 0.8/0.4 mm via avoid the existing back-layer ground route and front-layer WET_MUTE route. All original DRIVER segments and all unrelated routing remain unchanged. Three old DRIVE_CAP segments are replaced by one, and two DRIVER extension segments are added. Functional blocks are unchanged.

## Package and rating evidence

[Yageo FMP V9, 13 January 2026](https://yageogroup.com/content/datasheet/asset/file/YAGEO-FMP_DATASHEET), pages 2–4, supports FMP200FRF52-220R: 220 ohms, 1%, 100 ppm/K, 2 W at 70°C with linear derating to zero at 155°C. The maximum body is 9.5 × 4.2 mm and maximum round lead diameter 0.60 mm. The 52 code denotes tape dimensions, not board pitch. The maximum voltage is also limited by dissipation; flameproof does not mean an approved fuse.

The new 15.24 mm hand-formed footprint uses 0.9 mm finished drills and 1.8 mm pads. With the provisional −0.1 mm finished-hole tolerance it leaves 0.20 mm diametral insertion allowance. A +0.1 mm hole tolerance leaves 0.40 mm annular ring before registration error. Fabricator tolerances remain to be agreed. The maximum body plus a provisional 3 mm underside standoff reserves 7.2 mm above the PCB surface. This is an assembly allocation, not a tested thermal clearance. The source-bound [package envelope](results/package-envelope.json) is an input to later populated fit; it does not certify the chassis.

The older FMP200 library entry and its existing Main/Power instances are not silently replaced by this edit. Their 0.8 mm holes still need review against the same maximum lead/finished-hole allowance. The new name prevents treating those embedded copies as updated.

## Power calculation and remaining limit

Including 1% initial tolerance and a conservative full-range TCR allowance gives 214.9686 ohms minimum. The 10 V peak sine/68.4 ohm tank-resistance resonance screen dissipates about 0.13386 W. That supports the normal-signal package margin, subject to the stated ideal-driver and unmeasured-tank assumptions.

At 100°C ambient the candidate permits 1.29412 W. A direct 16 V RMS across the resistor would dissipate 1.19087 W (92.02% utilization); 18 V RMS would dissipate 1.50720 W and **fails**. The 18 V RMS case is a conservative direct-voltage/shorted-load diagnostic, not an assertion that an intact C603 passes DC or that the op amp can sustain that voltage/current. Typical op-amp current limiting is not credited as guaranteed protection. Actual local temperature, overload waveform, driver dissipation and short duration must close before release. A larger resistor alone does not protect the tank or driver.

Manufacturer/package evidence does not close purchasing. The [Mouser China FMP200 listing](https://www.mouser.cn/ProductDetail/YAGEO/FMP200FRF52-220R?qs=EiYF7fRZytyh2xGsCnyIzQ%3D%3D) remains an indexed four-month-old quantity-one lead, not live stock or Shanghai delivery confirmation. The investigated [Vishay PR03 220-ohm 1% alternative](https://gr.mouser.com/en/ProductDetail/Vishay-BC-Components/PR03000202200FAC00?qs=sGAEpiMZZMsPqMdJzcrNwnG0iq6vnlPNlc%252Bke8Skd6U%3D) is indexed non-stocked with 14-week lead time; it was not adopted or represented as a Chinese low-quantity supply solution.

## Verification and handoff

`tools/check.py` verifies 240 components, 145 unchanged nets, exact source/native metadata-only circuit delta, 54 unchanged other Reverb footprints, unchanged mounts/settings/outline, and all 18 unchanged schematic page rasters. Fresh KiCad 10.0.6 Reverb DRC has zero violations and zero opens under unchanged existing rules; ERC findings are unchanged. Drill export preserves every other hole: two R605 holes move and grow from 0.8 to 0.9 mm; one 0.4 mm via is added. The count changes from 146 to 147. Scope does not qualify all-board high-voltage spacing or copper ampacity.

Rendered board inspected: the new R605 body/label fits in the free area below the driver, with no overlapping component courtyard. The source-bound current-budget calculation is rerun after the metadata change and gives identical currents. The 72-case auxiliary supply sweep and four refinements are rerun; 42 cases retain engineering flags, with unchanged worst winding current/heat results. Their independent checks pass. Scoped ICM is clean.

Next: apply the per-part stress/package gate to the remaining power parts and legacy FMP200 holes; close driver short/thermal limits with exact sourceable parts, then continue three-board placement and populated chassis fit. No rear-panel attachment or mounting hole changed. Full drill body/bit dimensions, actual cabinet/assembly checks, remaining routing and all six-scope completion remain open.
