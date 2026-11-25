---
id: VAL-044
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Expression trim margin and controller isolation

[Owned review](../../engineering/whole-amp/expression-control/trim-isolation-review.md) records33 trim cases, five causal isolation cases and a failed267-node continuation attempt. A150k trim-feed candidate moves nominal adjustment from98.872% to56.980% travel with sampled audio THD below0.060%, but retains seven failed operating points including a new±12V midpoint failure. It is not adopted into native CAD.

A solver-success counterexample is retained: the isolated controller's transient-fallback OP differs from its1ms settled output by2.38756V. Future acceptance must check settling as well as physical rails. The previous complete VAL-043 runs did not use that fallback.152 evidence checks pass with circuit qualification explicitly false.

Exact Bourns3296W-1-104LF has Chinese LCSC stock9831/MOQ1 evidence; price tier, footprint/tolerance and exact Shanghai checkout remain open. The Hotone manual establishes a10k passive expression interface with tip wiper; it is not the100k volume pot or a verified accessory purchase. No orders, fabrication release, block changes or six-scope completion.
