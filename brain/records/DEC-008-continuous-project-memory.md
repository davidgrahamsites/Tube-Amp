---
id: DEC-008
type: decision
domain: cross-domain
status: documented
updated: 2026-11-20
---
# Project-wide ICM backfill and continuous decision logging

## Decision and authority
On November20 the user requested: “backfill this whole project including materials and decisions into ICM architecture and continue collecting feedback as it occurs and log the decisions that are made”. This is explicit authorization for in-project record organization and ongoing active-session capture.

## Implementation
Use the existing engineering brain rather than a parallel requirements database. [Feedback ledger](../feedback/events.json) retains attributed events and links to canonical decisions. [Materials register](../materials/register.json) routes every design/evidence area; [workspace catalog](../catalog/WORKSPACE.md) and file inventory are generated. [RULE-MEM](../rules/feedback.md) defines startup, capture, supersession and checkpoint duties.

Native CAD, original attachments, libraries, manufacturer models and historical runs stay at their existing paths. Contracts and catalogs wrap the legacy snapshots. Existing historical directories may contain their original scripts and products; they are read-only reference revisions, not the template for new active work. New work keeps stable tools/templates separate from products/evidence.

## Limits and next check
Backfill covers available local files and the visible supplied conversation. It is an attributed event summary, not a claim that missing external messages or attachments have been recovered. Complete-amplifier build readiness is unchanged. Open the generated catalog cold and follow current schematic -> parts -> mechanical fit -> feedback before continuing engineering work.
