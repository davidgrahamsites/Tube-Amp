# Mechanism catalogue
Source-backed operations, not novelty claims. All implementation states are current project evidence or unadopted hypotheses. Updated with bottom-enclosure research before candidate selection.

| ID | Concrete mechanism and intended benefit | Provenance | Assumptions / limits / state |
|---|---|---|---|
| M1 | Close rectifier/reservoir and return loop locally to limit loop impedance | Current circuit and capacitor-bank-fit/interface-research.md; TI power-loop guidance linked there | Exact current/pulse model needed; raw reservoir is C29/C30, not four film filters; current topology retained |
| M2 | Keep stage filter supply/return near the load to avoid extending its recharge/load loop | Current B_SCREEN→B_PRE→B_EARLY topology; same interface research | Physical loop effect is an engineering hypothesis until modeled/measured; no new capacitor values |
| M3 | Carry transformer mass through structural metal into fixed cabinet supports | mechanical/CONTEXT and three-board concept; [mechanical research](../bottom-power-enclosure/mechanical-research.md) | Floor material/load and fasteners unknown; not a qualified structure |
| M4 | Compare magnetic source orientation/distance against sensitive receiver pickup under matched load | [magnetic research](../bottom-power-enclosure/magnetic-research.md), Jensen/Magnetic Shield/Accutronics sources there | No arbitrary safe distance or metal-box immunity; exact magnetics/tank required |
| M5 | Route supply with its return and account for full loop resistance/contact loss | [harness research](../bottom-power-enclosure/harness-research.md) and grounding contract | Twisting does not cancel voltage drop or establish insulation; heater groups unresolved |
| M6 | Separate permanent protective bonds from deliberate circuit returns | reverb-600/grounding-contract.json | Physical bonding/tests open; no chassis-as-normal-return or audio-connector PE |
| M7 | Provide independently accessible module connectors/fasteners and controlled discharge sequence | capacitor interface and mechanical service contracts | Exact connectors, touch protection and retained paths must be qualified; no hot swap |
| M8 | Rotate a supported board to trade depth for height without lead reforming | capacitor-bank-fit/geometry-research.md and mounting-research.md | Candidate-specific height/retention/orientation unresolved; local geometry not whole fit |

Missing evidence: actual magnetics, speaker and common cabinet frames; temperature/noise/mechanical qualification; exact harness/connectors. Catalogue deliberately excludes DSP, switching-power redesign, active noise cancellation and novel materials because those would broaden the requested packaging scope.
