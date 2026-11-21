# Low-voltage diode choices — 2026-11-15

Owner: diode_pick delegated sourcing pass. Inputs: current coverage/candidate register and v0.4/v0.5 circuit capture scripts. Output: two engineering selections, four fitted references. No shared register or native CAD edits. Done condition: exact supplier identity, primary ratings, circuit-specific screening and explicit open checks. Budget: three minutes.

## Select P075: onsemi1N4007RLG for D331/D341

C53568, recorded mainland November11 stock173K+, MOQ10, RMB0.3291 each; buy10 costsRMB3.291. This is dated inventory, not a November15 live domestic quote. https://so.szlcsc.com/global.html?k=C53568

Manufacturer primary datasheet: https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf (June2024Rev18), retrievedNovember15.1N4007RLG is in the active ordering table; the DISCONTINUED heading below it starts the legacy unsuffixed table.1000V repetitive reverse,1A rectified current under specified75C conditions,30A one-cycle nonrepetitive surge. Axial plastic case59-10, cathode band. Mounting/thermal conditions still apply.

Circuit: D331 cathode to+12V, anodeCOIL_CH; D341 cathode+12V, anodeCOIL_REV. D331 clamps two parallel H1 relay coils, D341 one. Assuming960ohm +/-10% per coil and12V +/-10%, worst initial room-temperature currents are30.56mA/15.28mA; reverse voltage while energized is13.2V. These are comfortably below diode ratings. They are not full cold-coil, inductive energy, release-time or repetitive thermal checks. Retain supplier/model confirmation for the relays and inspect actual turnoff overshoot and local diode placement. Symbol pin1=K, pin2=A; actual board pad polarity, hole diameter and lead bend clearance require integration review.

P105 uses the same candidate for bridge, bias and regulator-discharge duties but is NOT selected by this dossier: different charging/discharge pulse conditions need separate checking.

## Select P082: onsemi1N4148TR for D601/D602

C84410, recorded mainland November11 stock108K+, MOQ50, RMB0.1038 each; buy50 costsRMB5.19. https://so.szlcsc.com/global.html?k=C84410

Exact manufacturer identity also corroborated by LCSC catalogue https://www.lcsc.com/product-detail/Switching-Diodes_onsemi-1N4148TR_C84410.html . Export-site prices are not a refreshed domestic quote.

Manufacturer primary datasheet: https://www.onsemi.com/pdf/datasheet/1n914-d.pdf (September2024Rev6), retrievedNovember15. ExactTR ordering variant is DO-35 tape/reel.100V repetitive reverse,200mA average,300mA DC at stated conditions;1V max at10mA,4ns maximum recovery at specified test condition. Cathode black band. Drawing case017AG: body length3.05–4.56mm, diameter1.53–1.91mm, lead diameter0.460–0.533mm.

Circuit D601 K=+15V/A=DRY_IN; D602 K=DRY_IN/A=-15V. At50Vpeak input and original100k series resistor (1% low), conservative clamp current ignoring forward drop is0.354mA. Opposite diode sees approximately31V. Candidate1M input resistor lowers this current tenfold. DO-35/P7.62 footprint already proposed; verify pad1=cathode and actual drill/bend clearance before integration.

This selects the diode, not a proven op-amp protection circuit: rail absorption, unpowered injection, hot leakage and real input excursions remain open. A diode can survive while an IC rail is lifted. No mains/B+ isolation claim.

## Held open

2N7000C232838 maker is onsemi, but guessed manufacturer datasheet URL redirects to missing-document page. Do not promote based on generic family or threshold voltage. BAT54HT1G input clamps need separate input-protection/ESD and footprint checks. Neither was selected in this pass.

Machine-readable selections and arithmetic are in lv-semiconductor-selection-2026-11-15.json. No order or construction release.
