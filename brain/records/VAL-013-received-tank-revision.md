---
id: VAL-013
type: validation
domain: cross-domain
status: verified
updated: 2026-11-19
---
# Received 600/2250 tank — scoped circuit revision checks

## Claim
Native600R-1 captures the received-tank interface and the previously studied attenuated-send/passive-dry change. All230 references/597 connected pins match the contract;25 modeled R/C values/endpoints match the native circuit. ERC has zero errors and one retained GND/PE alias warning. Verification applies to these checks and the bounded electrical fixture, not actual hardware, tank tone, full amplifier behavior, PCB parity or cabinet fit.

## Evidence
[Revision review](../../engineering/whole-amp/reverb-600/review/review.md) links the editable18-sheet native project/PDF, pin check, ERC, provenance and33 simulation cases:18AC,9coil-load,6transient. All8 stated pass criteria passed. Dry control variation is below2.21e-15 in the linear fixture. The original13 amp/supply/control sheets remain byte-identical to v0.5.

The tank impedance frequency and R/L are explicitly assumed, not seller-confirmed. Full send trim can deliver up to8mA RMS under the20Vpeak/100k source scenario; this does not establish the actual tank's allowed drive. Set send by actual-tank measurement. The passive mix has fixed insertion loss, documented separately from knob/mute dry independence.

## Parts and integration
Nine more positions now have exact resistor choices in canonical coverage:104selected refs/34MPNs/46groups. Existing dated mainland prices retained; no fresh stock claim. R6052W flameproof candidate lacks closed domestic stock; R616fault envelope remains conditional. Other exact parts and changed footprints require further work.

## Next check
Implement protected expression control; resolve actual cabinet/tank geometry and speaker/magnetics envelopes; repack the boards against that assembly. The old routed boards do not implement600R-1. Repeat complete selected-part amplifier simulation and physical checks. No fabrication/purchase/energizing release.
