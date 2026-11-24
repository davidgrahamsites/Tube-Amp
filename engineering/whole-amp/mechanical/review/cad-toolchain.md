# CAD toolchain and local automation check

Owner: mechanical integration. Updated November 24, 2026. User asked which program produces chassis models/files, whether KiCad covers everything, and whether FreeCAD is already installed and controllable (FB-110).

## Responsibilities

KiCad owns electrical schematics, native boards and PCB fabrication outputs. Export populated board STEP geometry to the mechanical assembly, with missing component models/envelopes explicitly identified. FreeCAD is the planned mechanical authoring tool for the chassis, panel, brackets and full cabinet assembly. Mechanical coordinates/measurements remain owned by fit-register.json, not by a decorative rendering. Labels/artwork remain separate from cuts and bend geometry.

The eventual handoff is editable FCStd plus STEP solids, and process-specific dimensioned drawings/flat-pattern DXF and finish artwork after their export and manufacturability checks. A STEP file alone does not describe bend allowances, tolerances, material or finish. No complete populated amplifier model, unfolded sheet-metal drawing or fabrication release exists from this tool test.

## Installed and tested

FreeCAD 1.1.4, Git revision 4fd3bf320d9566a27e60069fc8387448aaa3a094, is installed at /Users/appleadmin/Applications/FreeCAD.app. It is absent from the ordinary executable PATH and was not returned by Spotlight. Use Contents/Resources/bin/freecadcmd for console automation. The main MacOS launcher prints its environment: do not invoke it with inherited credentials. Run the console binary with a minimal environment and temporary user/system configuration files. Sandboxed Qt startup aborted with CPU-feature detection failure; the same installation's console works outside the sandbox.

[Receipt](freecad-automation-check.json): six checks pass on a synthetic 80 × 40 × 2 mm plate with one 4 mm hole. This coupon is deliberately not amplifier geometry. Python created a valid solid with analytical volume; saved and reopened the FCStd with editable primitive parameters; exported and reimported STEP with matching dimensions, volume and solid validity. Native and STEP automation are verified. GUI rendering, DXF unfolding, sheet-metal add-on and TechDraw/PDF exports still need version-specific trials.

Factory: ../tools/freecad_probe.py, run inside FreeCAD with RENEGADE_CAD_SMOKE_DIR pointing to a temporary writable directory; output FCStd, STEP and receipt.json. Keep only the receipt in project evidence after verification and remove temporary coupon products. Do not use this synthetic coupon as a chassis template or production drawing.

FreeCAD's [Python interface](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FreeCAD_Scripting_Basics.md) supports document and geometry automation. [KiCad's PCB manual](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) documents board 3D viewing/export and PCB manufacturing outputs. Local execution above, rather than those general capabilities alone, establishes what was actually tested here.

## Next mechanical check

T10 builds the populated assembly from verified cabinet and exact-part dimensions, including independent rear-cover removal, tube/connector service paths, cable bends and heat clearance. T11 adds the actual drill/driver envelope. Prove native/STEP and drawing agreement before releasing chassis files. Human check: reopen the complete model and compare its datums, clearances and full-scale drawings with the actual cabinet before manufacture.
