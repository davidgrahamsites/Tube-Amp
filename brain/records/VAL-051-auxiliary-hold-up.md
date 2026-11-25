---
id: VAL-051
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Auxiliary supply reserve for advance relay mute

[Owned review](../../engineering/whole-amp/aux-supply/hold-up-review.md) records134 primary raw-supply cases,28 targeted lower-resistance comparison cases and five timestep refinements. The25VA/6800µF candidate fails the hypothetical20ms mute allowance at low winding voltage (2.647ms minimum); the50VA reference has29.552ms minimum in24 shutdown cases. Neither is adopted. Independent discharge/KCL/hash checks preserve failures; six corruptions are rejected and22 native CAD files remain unchanged.

Exact domestic listings show stock for ST adjustable-regulator candidates, but the25VA transformer is out of stock and no50VA Chinese stock route is verified. Actual loss detection/contact timing, precise transformer/capacitor sourcing, regulator protection/sockets/heat and Shanghai checkout remain open. Next: actual secondary-loss detector timing against retained supply reserve, then native interface and populated three-board checks. All six scopes remain active; no manufacturing release or purchasing action.
