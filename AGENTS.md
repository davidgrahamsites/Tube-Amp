# Renegade tube amplifier workspace

Start with [CONTEXT.md](CONTEXT.md) for the workspace contract.

| Task | Read |
|---|---|
| Active electric/acoustic build | [Build identity](BUILD_VARIANT.md) |
| Project-wide materials and current artifact map | [Workspace catalog](brain/catalog/WORKSPACE.md) |
| Capture new feedback, corrections and decisions | [Standing capture workflow](brain/rules/feedback.md), then [event ledger](brain/feedback/events.json) |
| Cabinet, speaker and tank fit | [Mechanical fit contract](engineering/whole-amp/mechanical/CONTEXT.md) |
| Current project state | [PROJECT_STATUS.md](PROJECT_STATUS.md) |
| Active working-prototype plan | [plans/renegade-working-prototype/plan.md](plans/renegade-working-prototype/plan.md) |
| Future five-unit build/sales reference | [plans/renegade-five-unit-build/final.md](plans/renegade-five-unit-build/final.md) |
| Requirements and architecture | [Renegade_Codex_Handoff.md](Renegade_Codex_Handoff.md) |
| Historical conversation | [CHATGPT_CONVERSATION.md](CHATGPT_CONVERSATION.md) |
| Ongoing design narrative and build-guide sources | [Design journal](docs/design-journal/CONTEXT.md), [journal decision](brain/records/DEC-021-design-journal.md) |
| Original schematic/BOM inspection | [sources/original-ppt/inspection.md](sources/original-ppt/inspection.md) |
| User design imperatives and applicability | [Design Imperatives/review/REVIEW.md](<Design Imperatives/review/REVIEW.md>) |
| Capture or retrieve engineering knowledge | [brain/CONTEXT.md](brain/CONTEXT.md), then [brain/INDEX.md](brain/INDEX.md) |
| Imported KiCad starter | [Renegade_Library_Starter/README.md](Renegade_Library_Starter/README.md) |

At startup, read the current material map and task-relevant feedback. Capture meaningful new user feedback promptly, before dependent work; link it to its canonical decision/evidence record. At checkpoints and turn end, update the handoff/status as needed and rebuild both brain catalogs. Follow [the standing workflow](brain/rules/feedback.md). Canonical project requirements remain in the handoff.

Use [Circuit Design Skill Ladder](/Users/appleadmin/.codex/skills/circuit-design-skill-ladder/SKILL.md) for electrical tool/evidence routing and [Physical Design Agent Ladder](/Users/appleadmin/.codex/skills/physical-design-agent-ladder/SKILL.md) for mechanical/CAD/graphics/fabrication routing.

User instruction, November 26: keep a Luna agent assigned to the design journal during active engineering work. Reuse the available journal worker or start a Luna replacement with the saved journal handoff. Feed it meaningful problems, options, decisions and verification checkpoints; review its technical claims before integration. Preserve enough source-linked detail for a future design guide/post series paired with the physical build. Canonical engineering records remain authoritative; do not invent bench evidence or imply background activity between sessions.

User instruction, November 26 (FB-148): preserve engineering mathematics alongside the choices log. Keep source-linked inputs/units, formulas and substitutions, nominal/tolerance/fault assumptions, results, checks and decision consequences. Canonical calculators/results stay in engineering modules; the Luna journal maintains readable step-by-step derivations and links, including failed cases. Track historical backfill explicitly; arithmetic, simulations and physical measurements are different evidence. See [calculation narrative contract](docs/design-journal/calculations/CONTEXT.md).

## Engineering document standard — FB-149–151
Use short, direct aircraft-maintenance English. State each instruction once. Author and read human-facing engineering reports in HTML; render equations with KaTeX and define technical terms in a vocabulary key. Start at [the engineering reader](docs/engineering-reader/index.html) and follow [the document standard](docs/engineering-reader/document-standard.html). Preserve old review evidence and machine-required routing contracts; migrate legacy reports when used or revised. Save calculations with choices. Do not count documentation or repeated review as hardware validation.
