# Native reverb interface voltage and metadata correction

Owner: electrical integration. November 25, 2026. Baseline: `6f39803`. This continues VAL-060's held ground-plane review. The electrical circuit, board copper and drill geometry are unchanged.

## What is corrected

JR1 and JR5 carry the tube-derived dry signal and are not limited by the reverb op-amps' ±15 V supplies. Their source, native schematic, PCB and derived connectivity ratings now explicitly require tube-signal voltage/insulation qualification. The Reverb board legend drops “LV”; its historical refinement factory uses the same corrected legend. No connector has been silently qualified or substituted. Other low-voltage connector descriptions are unchanged.

The exact native comparison preserves all prior objects apart from those two hidden ratings and that shorter board legend. Native exports preserve 144 nets and 236 component identities; all 18 schematic pages are pixel-identical at the checked resolution. ERC retains one existing finding; Reverb DRC remains zero violations/zero opens under the existing rules. The final silkscreen was inspected: the shortened legend remains legible at the bottom with no new overlap. These checks do not validate the existing voltage clearances. The VAL-060 candidate is still outside active CAD, and its historical baseline hashes are intentionally not rewritten to pretend it was revalidated against this revision.

## Stress screen

`tools/simulate.py` reads the actual values and pin connections of C601/R601/R602, R612, R616/C607/R617/R618, R24 and, for the cold-plate/fault cases, R7/C6/R43. It checks an isolated passive interface with the wet-mute contact open (reverb enabled). The wet amplifier is an ideal source; the main phase-inverter AC load is omitted. R24 remains; C19 blocks DC. This is an interface screen, not an integrated amplifier simulation.

| Screen | Cases | Maximum absolute voltage across C607 |
|---|---:|---:|
| Audio, 3.07 V peak dry plus 15 V peak wet | 12 frequency/source-resistance combinations | 0.250 V |
| Overload, 135.1 V peak dry plus 15 V peak wet | 12 combinations | 1.194 V |
| Healthy C6, conditional cold-plate power-on/off | 18 transients | 22.536 V |
| C6 short, available plate-supply DC bound | 6 operating points | 153.422 V |

The 24 AC combinations require 48 independent dry/wet solves; sums of magnitudes bound their relative phase. Frequencies are 20, 82.4, 1,000 and 20,000 Hz; source resistances are 1, 40 and 200 kΩ. A separate complex nodal solver checks every node; the DC cases have an independent resistor-network reduction. Maximum disagreement with ngspice is 9.1e-12 V. All 72 decks complete.

The conditional startup cases step the unloaded clean plate supply between zero and 278/313 V through the actual 100 kΩ R7 and 47 nF C6, with 1 ms/100 ms/1 s rise/fall and wet DC at −15/0/+15 V. Tube plate current and actual heater/supply sequencing are omitted. These are explicit stimulus bounds, not measured supply extrema. The phase inverter and op-amp clamp behavior are not simulated. The resulting SEND_IN peak of 23.207 V flags the need to include the real input clamps and rail injection; it is not a claim that an unclamped physical OPA2134 input would reach that voltage.

C607's small AC differential voltage is distinct from the large ground-referenced dry voltage. The 63 V part passes these nominal audio/startup screens but **does not pass the available-rail C6-short screen**. The latter deliberately omits tube plate current and holds K3 unmuted; it is not a proven single-fault maximum or evidence of a failed physical capacitor. Even the 278 V/zero-wet DC case reaches 122.944 V across C607. Resolve that exposure through the final interface protection/voltage-rated coupling design before accepting C607. Merely replacing C607 does not address all exposed signals, connector insulation, relay contacts or op-amp rail injection.

Nominal tolerances only: resistor/capacitor tolerance, thermal behavior, actual supply overshoot and long-term fault dissipation remain outside this screen. The full selected RETURN architecture and actual magnetic components are still pending. The clean 3.07 V reference comes from prior nominal 25 W modeling; 135.1 V is an overload fixture reference, not the required clean RETURN swing.

## Ground-plane and component consequences

[TI's insulation-spacing guidance, SLUP421](https://www.ti.com/lit/ml/slup421/slup421.pdf), pages 4, 14 and 23–24, distinguishes working RMS voltage, transient voltage, environment/material and functional versus protective insulation. Therefore a global 0.25 mm rule or a candidate's 0.5 mm pour clearance cannot be accepted simply because its DRC passes. Solder mask is not credited as qualified conformal insulation. No exact clearance is adopted from an incomplete voltage envelope.

The quiet tank recovery area still benefits from a substantially continuous ground reference and short local returns. Voltage-specific copper keepouts are needed around the dry interface, with physical current-return review. Do not fragment the whole ground plane merely because different blocks exist. The established GB1 signal/chassis and independent protective-earth contract remains unchanged.

No new part is selected or ordered here. JR1/JR5's JST XH candidates and C607's existing KNSCHA selection retain their unresolved voltage/fault and physical-fit gates. A marketplace listing does not prove insulation, authentic part identity or shipment to the user's Shanghai address. China procurement remains incomplete.

## Next concrete work

1. Resolve C607/interface fault exposure and startup input-clamp/rail-injection behavior against the accepted buffered loop architecture. Compare a voltage-rated film capacitor with appropriate interface protection using exact China-sourceable parts and real package dimensions.
2. Establish connector and net-specific voltage requirements, encode spacing rules and reroute any resulting violations. Rebuild and inspect the ground plane against those rules.
3. Continue remaining native control/power integration, main routing, insulated harnesses and populated three-board chassis fit. Actual drill body/reach and several cabinet/speaker dimensions remain unresolved; the 46 mm chuck alone does not qualify access.

Reproduction: use KiCad's bundled Python for `tools/simulate.py`; use system Python for `tools/check.py`. `tools/export_native.py before` is allowed only at the recorded baseline; `correct_metadata.py --apply` then makes the declared change, and `export_native.py after` validates the resulting files. Existing native manual edits supersede historical generation factories; do not regenerate the whole project from a stale factory. Software receipts and deliberate failure flags are retained in results. All six scopes remain incomplete; no manufacturing release.
