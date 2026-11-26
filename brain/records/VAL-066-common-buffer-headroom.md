---
id: VAL-066
type: validation
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Common buffer: retain overload headroom

[Owned review](../../engineering/whole-amp/effects-loop/common-buffer/review.md) separates normal power from overload under DEC-016. An assumed loaded-transformer fixture reaches 25.713 W at 6.602% THD with 4.276 V peak internal send; a 12 V ideal ceiling leaves that point nearly unchanged. It does not establish 25 W at 1% THD or hardware performance.

Fourteen of sixteen 10/12 V-ceiling comparisons fail the declared waveform/THD/gain preservation screen; clean-bass waveform error reaches 53.61% for 12 V. Retain higher overload headroom instead of silently adopting low-voltage clipping. 24 base cases, 3 half-step repeats and 2 power probes complete. Four initial 90 s timeouts finish with 300 s wall allowance and unchanged decks/numerics. Independent waveform/source audit and negative controls pass. Active circuit/boards unchanged; no device or topology adoption.

Next: discrete high-voltage return gain/follower from existing B+, exact China-source devices and protection; targeted wet-contact clamp investigation addresses VAL-065 separately. LND150 is still a lead, with own-item stock/MOQ and Shanghai delivery unverified. All six scopes, harness/three-board populated fit and manufacturing release remain open.
