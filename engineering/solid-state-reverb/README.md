# Renegade v0.4 — original amp plus solid-state spring reverb

Updated November 11, 2026. **Editable engineering package, not a build/procurement release.** The new reverb PCB is fully routed and passes native DRC/parity. The complete amplifier still has unresolved electrical/component/fit gates; see the build plan. Original source and v0.3 files remain preserved.

## Open these

- `Renegade_220V_Reverb.kicad_pro` — integrated 18-sheet amplifier/reverb/control schematic.
- `validation/Renegade_0.4.pdf` — readable exported schematic.
- `pcb/Renegade_Reverb.kicad_pro` — standalone three-circuit-sheet reverb PCB project, with native schematic and routed `Renegade_Reverb.kicad_pcb`.
- `bom.csv` — 229 unique schematic references plus 18 mechanical/harness rows; R100 is DNP. Not a priced/approved purchase order.
- `pcb/bom-reverb.csv` — 45 fitted PCB components; four mounting holes are mechanical features.
- `build-plan.md` — mechanical constraints, assembly/harness sequence and staged commissioning.
- `source-delta.md` — every intentional adaptation from the original circuit.
- `evidence/cabinet-research.md` — recovered Mable drawings and China sourcing evidence.
- `validation/summary.md` — checks actually completed and remaining limits.

Keep this entire folder together; child sheets, project-local symbols and linked files are required. Edit the native CAD files for follow-ups. Generation scripts are provenance and must not overwrite later native edits.

## What changed

Original six tube envelopes: four12AX7 plus twoEL34. The added12AT7/12AX7 and reverb transformer from v0.3 are removed. Three dual OPA2134 packages drive/recover a real type8 spring tank and mix wet audio into a continuous buffered dry path. Panel **REVERB** adds wet; it is not a dry/wet crossfade. The internal SEND trim sets tank drive. Existing debounced clean/dirty and reverb footswitch logic remains; reverb off mutes wet immediately.

The original preamp/phase/output topology is preserved, with explicitly documented220V/50Hz supply, bias, heater-reference and measurement adaptations. Dry gain is approximately unity, but the op-amp path has finite headroom and slightly different loading. Do not describe it as an electrically untouched dry wire.

PCB scope is the **160x100mm low-voltage reverb daughterboard**. Main tube stages are chassis/turret wired. The supply/controller have integrated schematics but no completed PCB here. Cabinet choice remains the preferred Mable5E3 shell; its recovered drawings show508mm width,420mm height,215/242mm depth and312mm top opening. Actual internal assembly fit and stock confirmation remain open.

## Evidence boundary

Native schematic checks, PCB DRC and bounded TI-model reverb analysis are complete for the stated revisions. Full selected-component amplifier simulation, exact protective parts, purchased-part body/lead verification, tank drive/acoustics, custom chassis integration and physical tests are incomplete. Gerber/drill files are engineering previews, not permission to manufacture or energize. No orders, uploads, supplier messages or production claims have been made.
