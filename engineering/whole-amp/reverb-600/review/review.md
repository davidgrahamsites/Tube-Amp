# Received-tank circuit revision 600R-1

Current follow-up: [November20 measured-resistance simulation, selected parts and native PCB checks](measured-resistance-results-2026-11-20.md). The dated November19 evidence below is retained as history.

19 November 2026. Engineering draft. Cabinet and tank are already delivered.

## What changed

The full 18-sheet amplifier schematic now records the seller-confirmed 600 ohm input / 2250 ohm output tank. The three springs, medium decay, insulated input, grounded output, no lock and horizontal/open-side-down mounting are recorded on the harness sheet. The 13 original amp/supply/control sheets were copied byte-for-byte; their source hashes are retained. Four reverb sheets and the overview changed.

R601 becomes 1M and R602 becomes 100k. They attenuate the send before U10A; the strong tube-preamp signal no longer has to pass through a +/-15V op-amp to reach the phase inverter. R612 now carries passive dry from FX_RETURN to MIX_OUT. New R618 adds wet through 1M. C607 and R617 connect to WET_AC ahead of R618. U12 handles wet only. The faceplate knob and K3 continue to affect wet only. This is the previously studied passive-dry candidate, now captured in native CAD for the received tank.

The fixed insertion loss is real: at approximately1kHz the fixture gain from its ideal source to MIX_OUT is0.8243 with1k source resistance and0.6536 with100k. These include source loading. Dry remains constant as the reverb knob or mute changes; it is not a claim of unchanged gain compared with the original amplifier. Final whole-amplifier gain and feel require integrated and bench checks.

The 220ohm drive resistor is retained. It isolates the op-amp from the reactive load; it does not make this a regulated constant-current source. C602 remains22n with a100k send trimmer (about72Hz unloaded low-cut). C603 remains2.2u nonpolar film. Recovery stays high impedance with gain101 and330p feedback filtering. Actual coil resistance/current rating cannot be deduced from600/2250 alone.

## Checks completed

- KiCad10.0.6 exports the18-page PDF and native XML netlist. All230 references /597 connected pins agree with the contract. All25 modeled R/C elements agree with the native circuit values and endpoints.
- ERC: zero errors, one retained GND/PE alias warning. The warning is shown, not suppressed.
- ngspice with the unmodified TI OPAx134 model:18 dry/wet AC cases,9 coil-load scenarios and6 large-signal transient cases. Eight scoped pass criteria passed. Worst dry-gain variation with knob/mute over20Hz–20kHz is2.21e-15 relative in the fixture.
- Transients use a20Vpeak source behind100k,100/1000/5000Hz and +/-12 or +/-15V ideal rails. All reach40ms. Driver peak remains below2.88V. The modeled dry output reaches about13.1Vpeak without passing through the reverb op-amps. This does not validate tube-grid clipping or actual power supply behavior.
- Input-coil scenarios assume480/600/720ohm at1kHz and30/56/100ohm DC; nominal output assumes2250ohm at1kHz and200ohm DC. Inductances are derived mathematical surrogates, not measured tank values. The nine input models reach up to8.00mA RMS at full trim for the20Vpeak source. Maximum modeled R605 power is14.1mW under that normal-signal scenario. Do not use those figures as a safe tank-current specification.
- Send, output and tank harness PDF pages were rendered and visually inspected. Native pin comparison covers the recovery page too. Stable factories, editable contract, CAD products and run evidence are separated; scoped ICM check passed.

## Parts selected in this pass

Native600R-1 assignments: MFR50SFTE52-100K at R602/R608/R611/R612/R613/R614/R615; MF0207FTE52-1M at R601/R609/R617/R618. These use existing manufacturer/dated mainland sourcing evidence. Selected MPN metadata is now attached to26 reverb references in native CAD; footprint qualification is still explicitly pending. R609/R617 were already selected; the pass adds9 selected positions, taking the selected subset to104 fitted positions across34MPNs and46 groups. The recorded MOQ subset estimate remainsRMB324.47. This is not the complete amp cost or a fresh stock quote.

R605 has an exact2W flameproof candidate FMP200FRF52-220R, but domestic stock/MOQ/RMB price remains unresolved. Its9.0x3.9mm nominal body needs a larger footprint than the earlier generic resistor. R616100ohm remains conditional: ordinary signal dissipation and a sustained full-rail short are different cases. Do not use typical op-amp current limiting as a guaranteed fault bound. See the linked resistor dossier for calculations.

## Cabinet and PCB work still required

The delivered yellow-tweed cabinet is fixed. No replacement cabinet is proposed. The original board outlines are drafts, not requirements. This revision is a SCHEMATIC update: it does not claim that the previous reverb PCB, or the three other routed drafts, match these changed nets/parts or fit the cabinet.

Close actual top-chassis clearances, opposite speaker-hole spacing and tank body/mount dimensions. Select speaker/magnetics, allocate six tube/socket envelopes and service clearance, then repack boards and check the populated assembly. The manufacturer drawing has a speaker-hole/baffle dimension conflict; do not freeze drilling from that conflict. Cabinet rules and current dimensions remain solely in ../../mechanical/fit-register.json.

Expression-pedal behavior remains required. This revision does not yet implement its protected low-voltage port and wet gain-control element. Keep that interface in the board/chassis plan; do not label this PCB pedal-ready. Full-amp transformer/high-frequency simulation issues, protective parts, startup/thermal/pop/noise tests and actual-tank drive qualification remain open.

## Commissioning requirement

Before any powered work, use the project's staged electrical inspection and bench procedure. Set RV601 to minimum. A competent builder should characterize the isolated tank at low signal level and then increase send while measuring coil current and checking return distortion. Establish the working limit on this actual tank. Full trim is not a commissioning instruction. Keep dry independent of wet, retain the faceplate maximum and reserve the pedal control seam.

## Evidence and references

- [Circuit contract](../circuit.json), [native project](../cad/Renegade_220V_Reverb.kicad_sch), [full PDF](Renegade-600R-1.pdf), [pin/value checks](connectivity.json), [ERC](erc.json), [run results](../simulation/results.json), [drive response](drive-response.json).
- [Resistor selection evidence](../../../component-selection/evidence/reverb-resistor-picks-2026-11-19.md); stock observations retain their original dates.
- [TI OPA2134 manufacturer datasheet](https://www.ti.com/lit/ds/symlink/opa2134.pdf), accessed19November: output/input limits, supply range and package pinout. Do not promote typical current limits into guaranteed protection.
- User-supplied [Valve Wizard driver article](https://www.valvewizard.co.uk/reverbdriver.html), checked19November, describes measured inductive tank behavior and both voltage/current drive approaches. It supports considering frequency shaping; it is not a datasheet for the delivered Mable tank. The supplied Amplified Parts URL returned402 in the web tool; no claim is based on inaccessible content. Forum assertions were not used as component ratings.
