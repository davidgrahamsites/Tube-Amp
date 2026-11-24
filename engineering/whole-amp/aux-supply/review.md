# Negative-regulator local capacitor correction — November 24

C212 is now **47µF /50V aluminium electrolytic**, replacing2.2µF in the circuit contract, native supply schematic and Control PCB value. P127 selects Panasonic **EEUFR1H470**, already used elsewhere in the BOM. Functional blocks, connectivity, copper and geometry are unchanged. This is an electrical-value checkpoint, not a fabrication release.

## Basis and limits

ST [L79 datasheet](https://www.st.com/resource/en/datasheet/l79.pdf), DS0428 rev24 section6, specifies2.2µF solid tantalum at the input; aluminium electrolytic requires at least ten times that value. The old2.2µF aluminium specification did not meet that guidance. The upstream1000µF reservoir does not establish local bypass effectiveness across board/harness/socket inductance.

Panasonic's [exact product page](https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1H470) gives47µF±20%,50V,6.3mm body diameter,11.2mm length and2.5mm lead pitch. Minimum initial capacitance37.6µF exceeds22µF. This arithmetic does not establish ESR/stability across temperature, ageing or layout. At35V the nominal stored energy is28.79mJ; protection-diode and startup checks remain necessary. No regulator macromodel simulation or hardware validation is claimed.

[LCSC C407950](https://item.szlcsc.com/396929.html) was observed November24 with535 pieces, MOQ5, ¥1.1676 each (¥5.84 displayed for5). Shipping follows the domestic-policy evidence in the socketing observations; this is not a delivered quote/order.

## Native verification

KiCad10.0.6 loaded/exported the active hierarchy and Control board before and after. `tools/verify_c212.py` passes11 checks: exact named-net/ref-pin preservation, only C212 value changed in exported component metadata and source contract, exact native reverse-delta byte proofs, unchanged ERC and non-airwire DRC findings, unchanged90 Control unconnected count, and the capacitance checks. ERC retains its existing GND/PE alias warning; Control retains13 missing-courtyard findings. DRC chose two different endpoint pairs within existing unconnected nets; the complete reports are retained, and unchanged geometry/nets are proved by the byte comparison. This is not clean DRC.

Six generated loaded-output experiment decks (clean/dirty and three parameter cases) are byte-identical before/after because those experiments exclude the auxiliary-supply sheet and use ideal rails. Previous reports remain dated evidence for their original source hashes; this explicit equivalence bridge prevents falsely claiming those simulations qualified the regulator. No unnecessary repeat of unchanged output simulations was performed.

Full changed-sheet PDF and enlarged C212 region were visually inspected:47µF and polarity are readable, no new annotation or wire overlap introduced. Existing long local supply/bypass routes and U7 text crowding still require the dedicated schematic-humanizer pass; this checkpoint does not certify all-sheet readability.

## Remaining work

1. **C212 footprint:** native D8/P3.5 is still provisional; the selected part requires2.5mm lead pitch. Correct the exact pad/finished-hole/courtyard, repack locally at U7, and rerun DRC. Do not manufacture the current board.
2. Finish local input/output capacitance and reverse-protection review for all regulators, considering socket/adapter inductance. C214 remains10µF aluminium: review tolerance/temperature/ESR margin against ST guidance rather than assuming nominal value is enough.
3. Complete auxiliary supply load, line/no-load voltage, dropout, fault and thermal corners using the actual transformer and adopted loop load. ST L78/L79 TO-220 thermal data gives5°C/W junction-case and50°C/W junction-ambient under stated conditions; the socket itself is not a heatsink.
4. Select rated, retained regulator sockets/contacts and preserve a removable thermal connection. Actual drill envelope and chassis fit remain open.

## Subsequent package checkpoint — November24
C212 now uses the exact2.5mm Panasonic footprint. [Seven-part package review](../../component-selection/footprints/panasonic-fr/review.md) and VAL-025 supersede the provisional3.5mm pitch hold. The historical value-only checker pins the earlier revision; use the new package integration checker for current source/native preservation. Local bypass placement and regulator electrical/thermal qualification remain open.

## Subsequent supply-envelope checkpoint — November24
[Raw-supply and thermal review](envelope-review.md) records72 base cases,4 refinement cases and3 unadopted preload cases. It exposes minimum-load, documented-input-range and provisional transformer-current gaps. Regulator control-loop, startup/reset and actual socket/heatsink qualification remain open. No native changes in this checkpoint.
