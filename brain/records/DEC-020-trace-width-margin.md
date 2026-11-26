---
id: DEC-020
type: decision
domain: pcb
status: documented
updated: 2026-11-25
---
# Trace-width margin and manufacturing tolerance

User asks for adequately sized traces throughout, questions whether present routes can be considerably wider, and supplies four references. [Research digest](../../engineering/whole-amp/pcb-measured-r/review/trace-width-research-2026-11-25.md) records source scope and corrections.

[Routing requirements](../../engineering/whole-amp/pcb-measured-r/routing-requirements.md) own the engineering policy: qualified finished-width minimum, separate fabrication compensation, 1.5× finished-width target for power/returns and 2× preferred where compatible with spacing and parasitics. These multipliers are engineering choices, not user-specified numbers or standards. At provisional 20% narrowing, those targets require 1.875× and 2.5× drawn widths respectively.

No native widths are changed by this research checkpoint. Current per-path budgets, minimum finished copper and thermal/drop/pulse checks remain required; the refreshed native inventory is not an ampacity approval. Next: quantify path currents and apply the policy without disturbing functional blocks or HV spacing.

FB-140 adds five references (VSE, Patsnap, ALLPCB audio, JLCPCB and Sierra). Their dispositions and independent skin-depth, resistance, propagation and RC examples are in the same research digest. Useful whole-path, return-noise and solderability checks are incorporated into routing requirements. Unsupported universal audio widths,50ohm matching, simple current tables and incorrect heat scaling are explicitly excluded. This strengthens validation without changing circuit blocks or claiming native-width completion.
