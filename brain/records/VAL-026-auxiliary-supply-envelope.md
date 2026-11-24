---
id: VAL-026
type: validation
domain: cross-domain
status: documented
updated: 2026-11-24
---
# Auxiliary supply, replaceable regulators and thermal constraints

Owner: Renegade integration. Existing FB-114/115/116 authorize continued simulations, exact-parts-first work and socketed ICs/tubes. This checkpoint does not close any of the six through-chassis scopes.

The [supply review](../../engineering/whole-amp/aux-supply/envelope-review.md) records72 raw-rectifier/load cases,4 limiting-case half-timestep repeats and3 proposed-preload repeats. All finish; fixture KCL and thermal arithmetic pass, and4 intentional evidence corruptions are rejected.48 baseline cases have screen flags:24 below the5V regulator minimum-load condition,23 above the positive documented-input-range screen,4 above the negative range and16 above the provisional0.25A half-winding current. Counts overlap. Native source/schematics/boards remain byte-identical to a1ddf86; recorded preservation hashes support retaining prior ERC/DRC results without claiming new runs.

Maximum conditional regulator heat is4.04W, maximum assumed winding RMS0.279A. With the declared100°C junction target,60°C local ambient and interface assumptions, the tightest shared-sink budget is7.94°C/W. This is a design envelope, not a selected sink or measured cabinet temperature. Transformer/load assumptions and omitted regulator control, startup, short-circuit, reverse-current and safety behavior are explicit. Exact magnetics and the eventual effects-return load must replace these assumptions.

An unadopted820Ω±1%5V preload passes the initial5mA minimum-load arithmetic; its3targeted repeats add at most0.143W regulator heat. Exact China-stock part, temperature/ageing margins, native integration and reset behavior remain open. Do not report this proposal as a PCB fix.

The [contact review](../../engineering/component-selection/socketing/contact-review.md) narrows regulator contacts: obsolete Molex supply route rejected, TE/Harwin round-pin contacts not qualified for ST rectangular leads. All10ICs/6tubes remain socket-required. No purchase, supplier contact or upload occurred; no new part is claimed Shanghai-purchasable.

Next: qualify actual auxiliary magnetics and retained regulator contacts/heatsinks; integrate preload, local bypass and split-rail protection with source/native consistency and startup/reset checks. Continue transformer/RETURN and populated three-board fit. Real drill envelope remains pendingNovember25. No fabrication release.
