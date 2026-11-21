# Renegade 220 V /50 Hz + tube spring reverb

**Revision 0.3 - editable wired engineering draft.** Created October 4, 2026 at the user's request. Open `Renegade_220V_Reverb.kicad_pro` in KiCad 10 and open its schematic. Keep this whole directory together: child sheets and the local library are required. The original PowerPoint and library starter are unchanged.

The root and fourteen child sheets form an electrically connected schematic. Continuous orthogonal wires show connections within each sheet. Global labels are retained for sheet interfaces, with standard ground symbols and explicit junction dots. The PDF draws hops at wire crossings. All eight tube envelopes, physical heater pins, relay coils/contacts, logic package units and normalled effects return are captured. Native netlist pin checking verifies those connections against the design register.

| Sheet | Responsibility |
|---|---|
| 01_clean | Original clean gain, tone and volume stages |
| 02_dirty | Original dirty gain stages |
| 02b_dirty_tone | Cathode follower, dirty tone stack and master |
| 03_routing | Input selection, inactive-grid grounding and normalled effects loop |
| 04_output | Original phase inverter/EL34/output/feedback with draft bias/test changes |
| 04b_output_transformer | Original transformer, speaker selector and feedback tap |
| 05_supplies | Both-pole mains switch, HV rectifier, reservoir, standby and filtering |
| 05b_bias_reverb_supply | Negative bias, heater elevation and proposed reverb rail |
| 06_heaters | All heater pins, protective earth and single chassis/audio bond |
| 07_reverb | Parallel 12AT7 driver, physical tank, 12AX7 recovery and dry/wet mixer |
| 08_control_supply | Separate 220 V /50 Hz control supply and 12/5 V regulators |
| 09_controller | Protected local/pedal contacts, RC filters and Schmitt debounce |
| 09b_latches_drivers | Toggle flip-flops, supervised reset and relay drivers |
| 10_logic_power | Package power, unused gates and IC bypassing |

The source capture is separately editable under `baseline/`. Baseline references map unnumbered valve envelopes as V1 clean, V2 early dirty and V3 dirty gain/follower. Source V4/V5/V6 are retained. A native ECC83 unit B has pins 1/2/3 while unit A has 6/7/8; physical numbers, not letters, are authoritative. RV1-10 map the source's named controls; see the register and review notes.

The reverb shares the effects-return signal between a continuous dry mixing path and a parallel spring path. K3 de-energized mutes the AC-coupled wet level. The passive TRS pedal uses two momentary contacts, with matching local buttons. Logic resets to clean/reverb off. TRS interpretation and immediate wet muting are draft assumptions. The source 4/8/16-ohm output selector is retained. Connect the pedal with power off until jack insertion/inhibit behavior is resolved.

The main transformer uses Hammond 372HX as an electrical reference (220 V /50 Hz, 300-0-300 V, 230mA HV and 6.3V/6A heater winding). T3 is specified separately for 220 V /50 Hz and 15 VAC. These are not approved Chinese supplier selections or cabinet-fit claims. The output transformer retains the source 1650F reference; its 25W rating is not a measured amplifier-power result. Full schematic parts, ratings, provenance and statuses are in `design-connectivity.json`; `bom-draft.csv` is for review, not purchasing.

## Actual checks and remaining work

See `validation/validation-summary.json`, native netlists/ERC reports and `simulation/explorations.json` for revision-specific results. The bias circuit was changed after an insufficient-negative-voltage result; corrected nominal reference range is approximately -33.6 to -48.1V. A modeled bounce sequence generated two clock edges for two presses. Neither result establishes a safe EL34 bias point or qualified switch behavior with actual parts.

Complete build-component selection/model qualification, baseline/audio/reverb/integrated simulations, fuse/standby ratings, transient/thermal checks, relay pop suppression, tank connector/case/mounting verification and chassis fit remain pending. **Do not use this draft to order a PCB or energize an amplifier.** This is the same electrical review boundary required by the canonical handoff.

Edit in KiCad for follow-ups. The initial v0.2 generator is retained for provenance and its guard prevents overwriting the redraw. `wire-layout.json` and `tools/wire_layout.py` describe the v0.3 presentation; `wire-layout-files.json` guards later native edits. `validation/label-layout-v0.2.zip` preserves the earlier view. Exact native-export comparison in `validation/layout-equivalence.json` confirms identical references, values and pin partitions. Compact visible Display fields are used where needed; original full Value fields remain in the native schematic and BOM. Edit the native schematic for circuit follow-ups; do not regenerate over native edits. The local library and generated files are portable and do not replace global KiCad library tables.
