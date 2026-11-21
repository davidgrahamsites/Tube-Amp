---
id: DEC-002
type: decision
domain: cross-domain
status: documented
updated: 2026-10-04
---
# Combo, Shanghai sourcing and automation requirements

## Decision and authority
The user selected a combo amp with a built-in speaker and Shanghai sourcing/delivery, and requested free companion CAD software and the Circuit Design Skill Ladder. Requirements are recorded in the [canonical handoff](../../Renegade_Codex_Handoff.md).

On October 4, the user clarified that the cabinet should have its main operating controls on the top or front. Both orientations are accepted; the final layout is not yet selected. A top-facing panel near the rear edge is treated as top-mounted.

The user also explicitly authorized delegating product-specification and related sourcing research to Claude when useful. Use an available Claude interface or task; do not imply research was dispatched without an actual tool result.

## Consequences
Mechanical and sourcing tasks must include a speaker, baffle/cabinet, tank mounting, ventilation, chassis, front panel and printed artwork. Compare low-volume cabinet/panel manufacture independently from PCB fabrication.

Evaluate usable panel dimensions, visibility and knob access for top-facing or front-facing controls. Keep control-face orientation explicit in drawings and shared geometry. The preferred 5E3 shell remains a conditional candidate until its actual geometry and selected components establish fit.

Claude research should return exact manufacturer/part identities, source URLs or documents, retrieval dates, supported specifications and unresolved gaps. Verify consequential claims against primary evidence before component selection or release. This delegation permission covers research coordination; supplier contact and purchases retain their existing authorization requirements.

## Evidence
User replies in this Codex chat on October 3–4, 2026, including “controls on the top or the front.” The [active prototype plan](../../plans/renegade-working-prototype/plan.md) captures current work packages; the [five-unit planning run](../../plans/renegade-five-unit-build/CONTEXT.md) is a future reference.

## Open choices
Power, target budget, exact bench resources, intended use, speaker voicing, final top-versus-front layout and visual direction. The accepted orientation range is resolved. The October 4 scope correction makes one working prototype the current milestone; see [DEC-004](DEC-004-prototype-first.md). Five-unit planning is deferred.
