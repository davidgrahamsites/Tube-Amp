# Shared acceptance worksheet

November 26, 2026. Owner: /root integration; physical operator unassigned. Editable comparison worksheet, not certification or completed test. U=upper diagnostic, H=hybrid lower, L=all-filter lower. Each UNKNOWN remains a hold; no empty cell is a pass. A numeric limit must be sourced and frozen before testing, not chosen after a favorable trace.

| Requirement / metric | Limit or source basis | U / H / L current state | Next evidence / owner |
|---|---|---|---|
| Functional endpoints/values | Current circuit.json; no unreviewed changes | Source baseline mapped; all physical allocations UNKNOWN | Pin/return/component ownership table, integration |
| Output power, distortion and treble/stability | Approximately25W user target; exact test distortion/frequency/load and accepted response limits not finalized | UNKNOWN / UNKNOWN / UNKNOWN | Current output/feedback checks plus exact magnetics; electrical integration |
| Dual mains and protection | DEC-015,120V60Hz and220V50Hz; fuse/selector actual parts pending | UNKNOWN / UNKNOWN / UNKNOWN | Both operating/fault cases and source/fuse selection; electrical |
| Heater voltage/reference | Exact tube limits and HD-002; no final shared heater solution | Existing fault / inherited hold / inherited hold | Resolve reference/windings, load-end hot/startup cases; electrical |
| Bias loss with B+ present | Actual output-stage permissible fault envelope; not yet accepted | UNKNOWN / UNKNOWN / UNKNOWN | Bias/contact/return fault review; electrical |
| Hum/noise | Absolute dry/wet limits and uncertainty not yet frozen | UNKNOWN / UNKNOWN / UNKNOWN | Same actual loads/controls, tank orientation, mains modes, repeat baseline; electrical/builder |
| Supply filtering/reset | Load-end allowable disturbance/sequence from actual circuits, not invented proxy limit | UNKNOWN / UNKNOWN / UNKNOWN | Harness/parasitic models and applicable fixture; electrical |
| Insulation and exposed contacts | Actual working/transient/common-mode voltage, environment/material and applicable requirements pending | UNKNOWN / UNKNOWN / UNKNOWN | Pin/metal/creepage/clearance and unmated states; electrical |
| PE and normal returns | Existing grounding-contract: independent protective bonds, one GB1, no chassis normal return | Logical baseline documented; all assemblies UNKNOWN | Metal/bond schedule and physical tests; electrical/builder |
| Discharge/partial disconnect | Residual-voltage/time criteria and retained paths per store pending | UNKNOWN / UNKNOWN / UNKNOWN | Raw/film/bias/aux inventories, test points/procedure; electrical |
| Temperature and lifetime | Exact capacitor/transformer/regulator ratings and derating; no generic105°C acceptance | UNKNOWN / UNKNOWN / UNKNOWN | Enclosed heat budget, defined ambient/load and measurements; electrical/mechanical |
| Whole fit/cover/module extraction | No collision at sourced tolerance; independent wood removal; margins not released | Existing diagnostic overruns / UNKNOWN / UNKNOWN | Common frames/parts/cables/lids/tools, inert mock-up; mechanical |
| Actual driver and fabrication access |46mm chuck only; other dimensions expected Nov27 from Nov26 reply | UNKNOWN / UNKNOWN / UNKNOWN | User readings; bare-metal drill sequence and installed screw sweeps; mechanical |
| Floor/transport retention | Exact mass/CG, metal, floor/joints and justified handling load | UNKNOWN / UNKNOWN / UNKNOWN | Structural design and physical check; mechanical/builder |
| Acoustics/tank behavior | Retain horizontal/open-down tank; matched rear-radiation/acoustic comparison limits pending | UNKNOWN / UNKNOWN / UNKNOWN | Actual speaker/tank/mount/enclosure and comparison; builder |
| Installed cost/sourcing | Economical reliable China-source one-unit build; no numeric cap or qualified delta | UNKNOWN / UNKNOWN / UNKNOWN | Same BOM boundary, exact availability/MOQ/tax/freight/labor; integration |

Desk study completion is not an acceptance result. Physical work is unexecuted and operator/test prerequisites must be resolved before energization. See final.md for dependency order and research.md for evidence limits.

## Gate assignment
Gate D is desk comparison only. Gate P requires the chosen fixture's insulation, PE, retained-charge procedure, ratings/loads, mechanical retention and test-access review; heater/bias faults must be resolved where those circuits are active. It does not require already having the hum/thermal results the test is designed to obtain. Gate A requires a representative populated as-built prototype to satisfy architecture-dependent electrical, thermal, acoustic, noise, retention and service criteria above. Gate R adds manufacturing tolerances, finalized native/production files, assembly/incoming/end-test instructions and remaining production release checks. No gate is currently passed by this worksheet.
