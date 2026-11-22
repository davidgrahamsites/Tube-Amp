---
id: VAL-016
type: validation
domain: cross-domain
status: verified
updated: 2026-11-21
---
# Service, panel and selected-package checkpoint

## Claim and limits
Six exact packages are integrated into the existing electric PCB drafts. Native pad/net and DRC checks pass within their stated scope. The revised control envelope passes a rectangular opening screen using received measurements. Status verified applies to these checks only: no populated cabinet fit, complete routing, chassis strength, tool access or fabrication approval.

## Received evidence
FB-073 supplies P1=307–308mm and P2-clear approximately53mm under rear-cover-ON instructions. FB-074 supplies P3=38.3cm=383mm under rear-cover-OFF access instructions, fixed top underside to inside floor top. These are user measurements without stated tolerance or independently verified setup. Canonical values are in the [fit register](../../engineering/whole-amp/mechanical/fit-register.json). Total inside height is not available chassis height once parts are installed. Supplier420mm external height and received383mm internal height have different endpoints; their37mm difference does not establish individual board thickness.

## Panel and service result
The former60mm-deep knob envelope fails the received53mm clear opening. A staggered two-row proposal preserves all ten controls and existing candidate pot/knob types. Its215×48mm sweep fits a307×53mm rectangle, with minimum nominal4.414mm knob gap,2.5mm edge gap and5mm lug/wire-box-to-other-pot-body gap. Curved opening shape, finger access, shaft/nut/washer seating and panel elevation are still open. The30-terminal electrical interface is unchanged. [Panel checks](../../engineering/whole-amp/mechanical/review/panel-study-checks.json), [full-size study](../../engineering/whole-amp/mechanical/review/panel-study-face.pdf).

The [service proposal](../../engineering/whole-amp/mechanical/review/chassis-service-layout-2026-11-21.md) uses fixed-wood supports and an independently removable metal cassette. Rear cover has no chassis attachment. Rear-facing retainers and bench-accessible PCB carrier flanges are proposed; actual screws, tool envelope and withdrawal sweep remain unverified. Original board outlines total109900mm² against a reported467×160mm plane of74720mm², so unchanged outlines cannot share one plane. No fictitious dimensioned chassis is released. Main, Power, Control and Reverb ownership remains intact. Natural tube visibility stays conditional on the full assembly review.

## Native PCB changes and checks
Baseline e6811e6; KiCad10.0.6. R303/R313 use selected YageoMF0207FTE52-15K packages; R39/R503 use explicit YageoFMP100 packages; C321 uses explicit KNSCHA82CL0120 geometry; C602 uses KYETKP223J2J1001 at10mm pitch. Nets and electrical values are unchanged. C602's existing SEND_TOP trace endpoint follows the new pad. Larger C321 pads initially caused two clearance findings; moving it0.5mm left and1mm up cleared them.

All444 connected-pad checks match the circuit contract; ten explicit no-connect pads are retained. Historical source boards are unchanged. Native DRC: Main0violations/105unconnected; Power0/39; Control0/99; Reverb0/0. All four board drafts were parsed. Reverb and Control copper/silkscreen previews were inspected. This is pad-contract verification, not an assembly-schematic parity claim.

Diff review caught KiCad SaveBoard overwriting paired project settings when loading a temporary baseline without its project file. The original project files were restored byte-for-byte from e6811e6, both new mutation factories now preserve project bytes, and fresh native DRC was run under the restored rules. All four project-file byte comparisons pass. No rules or exclusions were relaxed. Initial interrupted report serialization and the intermediate C321 placement were corrected before this checkpoint.

- [Package change manifest](../../engineering/whole-amp/pcb-measured-r/review/service-wave-package-integration.json)
- [C321 correction history](../../engineering/whole-amp/pcb-measured-r/review/c321-clearance-repair.json)
- [Final native check](../../engineering/whole-amp/pcb-measured-r/review/final-checks.json)
- [Final board/project/DRC hashes](../../engineering/whole-amp/pcb-measured-r/review/service-wave-validation.json)
- [Component LV evidence](../../engineering/component-selection/evidence/electric-lv-parts-2026-11-21.md) and [resistor evidence](../../engineering/component-selection/evidence/electric-bias-resistors-2026-11-21.md)

## Next work and human check
No further ruler measurements requested at this checkpoint. Select/qualify remaining speaker, magnetics, sockets and major hardware; allocate their actual envelopes, heat and removal paths with the tank, controls and intact functional blocks. Then fix the cassette/carrier geometry, repack board outlines and complete routing. Verify full drill/driver approach and withdrawal against the actual tool. Check the paper panel with installed knobs before drilling. Existing expression-control, semiconductor corner and full-amp ringing issues remain open. No new electrical simulation or powered test is claimed by this package/layout checkpoint.

## ICM verification
Scoped ICM checks are clean for mechanical, PCB integration, selected footprints and brain modules. Catalog validation reports no errors; feedback IDs and component references are valid. Factories, canonical register, generated views and evidence retain separate ownership. Native pad checks emit KiCad wxApp/image-handler diagnostics but complete successfully with no pad mismatches.
