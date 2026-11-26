---
id: DEC-021
type: decision
domain: cross-domain
status: documented
updated: 2026-11-26
---
# Maintain a Luna-authored amplifier design journal

User decision FB-142: retain a Luna agent during active engineering to document problems and the decisions that follow, in sufficient detail to become a design guide or a long series of posts alongside the eventual build.

The journal lives in [docs/design-journal](../../docs/design-journal/CONTEXT.md). Its owner writes narrative accounts derived from canonical ICM records and engineering evidence. The coordinator continues to own engineering decisions, verification and integration. Use a problem → evidence → options → decision → checks → remaining work sequence, with source paths, revision, assumptions, authority and status. Distinguish proposed alternatives, adopted native changes, simulated behavior and measured hardware behavior. Preserve rejected approaches and corrections when they explain the eventual choice.

At each meaningful checkpoint, pass the new evidence and exact decision to the Luna worker, inspect its account, and update its index/handoff. Reuse that worker while available; on a later session, resume from the saved handoff with a new Luna worker if necessary. This is an active-work assignment, not a claim of unattended background execution. Initial older material is a backfill queue, not already-written history. Actual assembly photographs, measurements, and commissioning results will be linked when they exist. No publication is authorized by this documentation request.
