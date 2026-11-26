# Proposed physical allocation interface

Owner: /root electrical/mechanical integration. Status: research contract, not released schematic/pinout. Actual endpoint evidence: ../capacitor-bank-fit/interface-research.md and ../bottom-power-enclosure/harness-research.md. Existing electrical nets and values remain canonical in circuit.json. A functional power block may span physical boards; its ownership remains explicit.

| Interface / function | Hybrid lower side | Upper side | Open dependency |
|---|---|---|---|
| Rectifier/raw reservoir | T1 HV/D3–D6/F2/C29/C30/R501/R502/CT return local | No rectifier pulse route through quiet audio | Exact transformer/currents and layout |
| B_MAIN | From B_RAW via S2 | T2 center tap | S2 location or long HV loop not resolved |
| Screen and downstream feed | L1/C26/B_SCREEN and controlled return | R41/R42 and R35 inputs | Real current/voltage/return routing |
| B_PRE | Hybrid generates locally above | R35 with C13/C25, both50uF on B_PRE/GND | Physical region and return topology; no merging |
| B_EARLY | Hybrid generates locally above | R17 with C12,50uF on B_EARLY/GND | Same |
| All-filter-lower variant | R35/R17 and all four filters below | Remote B_PRE/B_EARLY load feeds/returns | Extra harness and applicability tests |
| Output transformer | Not moved below in first comparison | T2 with output tubes and secondary/feedback interface | Exact magnetics and loaded stability |
| Heaters/reference | Winding/reference allocation pending | Actual tube sockets/pilot loads | HD-002; no frozen pair count or connector |
| Bias | Ownership pending | BIAS_OUT/grid network; adjuster location pending | Loss of bias/return while B+ remains |
| Auxiliary/control rails | Rectification/reservoir location proposed below | Regulator/rail ownership pending | Preserve local input/output caps and load-end reset timing |
| Mains selection/power | Inlet/fuse/selector/PE and both T1/T3 primaries grouped below candidate | Existing S1 control if retained would require routed mains | Concrete control alternatives before adoption; no remote relay assumed |
| PE/GB1 | Independent lower protective bond | Upper exposed metal independently bonded; existing GB1 intent preserved | Exact bonding hardware, sole normal signal/chassis bond, continuity |
| Service charge | Raw/film/bias/aux stores depend on allocation | Upper stores may remain charged independently | Both halves, partial opens, no hot/unverified-charge disconnect |

No connector family/cavity count, conductor gauge, circuit modification or billable fabrication is selected. Every physical seam requires sourced voltage/current/insulation, routing and service qualification. No connection to removable rear wood is permitted.
