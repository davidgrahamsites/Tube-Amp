# Independent research, 23 November 2026
Three read-only researchers: /root/optical_research, /root/loop_research, /root/switch_parts_research. This is research evidence, not qualified procurement or a hardware test.

## Optical controls
Retain K1/K2 initially. Their DPDT selection/grounding functions cannot be replaced by a single SPST optical part. K3 is a possible wet-only experiment if a measured defect warrants it; present de-energized relay mutes. An ordinary LED/LDR becomes high resistance unpowered, reversing that default. Optocoupler -> existing MOSFET -> relay retains the coil, mechanical contact and flyback behavior. Shared power/ground bypasses the system isolation barrier. Isolated remote control could justify it later; it does not isolate the audio loop.

Manufacturer references:
- Omron G5V-2-H1 DC12: https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v2.pdf — DPDT, 12.5mA/150mW nominal coil, initial contact resistance 100mΩ max; switching voltage and coil/contact isolation are different ratings. Diode suppression changes release behavior: https://omronfs.omron.com/en_US/ecb/products/pdf/precautions_pcb.pdf
- Vishay VO617A: https://www.vishay.com/docs/83430/vo617a.pdf — phototransistor control, not bilateral audio switch; CTR variation must be allowed for.
- Advanced Photonix NSL-32SR3: https://www.advancedphotonix.com/wp-content/uploads/2022/03/DS-NSL-32SR3.pdf — 150Ω typical at 5mA LED, 60Ω max at 20mA; dark resistance measured 10 seconds after removal, decay specification to 100kΩ is not full-off time.
- Panasonic AQY221N2VY: https://na.industrial.panasonic.com/products/relays-contactors/lineup/semiconductor-relays/series/13003/model/13004 — low output capacitance 1pF typical/1.5pF max, 12.5Ω maximum Ron; recommended load maximum 15V despite 40V product rating. Form A.
- Panasonic AQY412S: https://industry.panasonic.com/ap/en/products/control/relay/photomos/number/aqy412s — Form B, 60V absolute /48V recommended, Ron1Ω typical/2.5Ω max, leakage1µA max. Selector output capacitance500pF typical: https://industry.panasonic.eu/storage/imported/industrial.panasonic.com/ac/cdn/e/control/catalog/semi_eng_selection.pdf . Do not confuse with ~0.8pF input-output isolation capacitance. AQY412EH has different leakage; do not transfer suffix ratings.
- PhotoMOS definitions: https://industry.panasonic.com/global/en/products/control/relay/photomos/term ; FAQ https://na.industrial.panasonic.com/knowledge-base/faqs/photomosr-faqs
- Audio switching transient mechanisms: https://www.onsemi.com/download/data-sheet/pdf/nlas54405-d.pdf

Screening calculations only: a 500pF shunt with a 10kΩ Thevenin source gives fc31.8kHz and -1.45dB at20kHz; at1MΩ fc318Hz. With R61010kΩ, a 2.5Ω shunt idealized mute is ~-72dB, a150Ω LDR ~-36.6dB. Actual loading, distortion and transition behavior need tests. Each5mA LED resistively powered from12V consumes60mW from that rail, in addition to coil demand in the combined arrangement.

## Effects-loop research
The existing loop is passive and precedes spring send/mixing. A low-impedance return changes dry transfer AND wet injection. R100 DNP does not mean zero DC reference: R612100kΩ+R24 10MΩ gives an indirect ~10.1MΩ path. A deliberate local discharge/reference must still be designed.

Primary precedents, not drop-in qualification:
- Designer serial tube loop: https://www.valvewizard.co.uk/fxlooppcb.html — attenuation and recovery are both necessary; cited design approximately /46 and ×50.
- Discrete HV loop manufacturer: https://mojotone.com/products/mojotone-discrete-hi-voltage-series-effects-loop-for-vacuum-tube-amplifiers
- Designer Zero Loss loop: https://sites.google.com/view/sdm6550/zero-loss-fx-loop — application-specific Marshall support, not Renegade compatibility.
- OPA2134: https://www.ti.com/lit/ds/symlink/opa2134.pdf — non-rail-to-rail; typical ±15V output into2kΩ ~-13.8/+13.5V, not a guaranteed design envelope. Positive common-mode limit +11.5V. Attenuation before a low-voltage stage does not create recovery headroom.
- DD8 nominal -20dBu, max not specified: https://static.roland.com/assets/media/pdf/DD-8_eng03_W.pdf
- DD200 nominal -10dBu, max+7dBu, input2MΩ: https://www.boss.info/fr/products/dd-200/specifications/
- Strymon family maximum+8dBu: https://www.strymon.net/faq/do-your-dsp-driven-pedals-handle-both-instrument-and-line-levels/
- Pull-downs/pops: https://www.valvewizard.co.uk/Pedal_Essentials.pdf
- External protection: https://www.ti.com/lit/an/spva018/spva018.pdf ; back-powering: https://www.analog.com/en/resources/app-notes/an-1387.html

Proposed fixture targets (engineering proposals, not standards): SEND≤1kΩ80Hz–10kHz tested100kΩ||2nF and1MΩ||2nF; RETURN≥1MΩ atmidband from1kΩ/10kΩ sources. DD200 example -10dBu nominal, sine-equivalent peak ≤+1dBu(1.23Vpk) gives6dB margin below+7dBu; not a universal pedal guarantee. Dry, spring drive and wet-recovery transfers compared separately. Full bypass and buffered bypass differ in loading, failures and pops. Supply failure needs isolation of faulty recovery outputs if original passive path is restored.

## Parts and supply evidence
Index observations only, dated23Nov2026. Global USD prices do not prove domestic RMB stock/delivery. No substitutions adopted.
| Part | Supplier reference | Indexed evidence | Status |
|---|---|---|---|
| EL817(C)-F DIP4 | https://www.lcsc.com/product-detail/C181890.html | MOQ20,$0.0475ea | control-only; stock not checkout-confirmed |
| AQY212GS SOP4 | https://www.lcsc.com/product-detail/C719745.html | MOQ1,$1.1793 | FormA, manufacturer48Vrecommended/0.7Ωmax; mainlandunverified |
| AQY412S SOP4 | https://www.lcsc.com/product-detail/C719578.html | MOQ1,$5.1837,19indexed | otherlocaleoutofstock; unresolved |
| OPA2134PA DIP8 | https://www.lcsc.com/product-detail/C1346118.html | MOQ1,$7.3168,111indexed | stock varies; reconfirm |
| OPA2134UA/2K5 SOIC8 | https://www.lcsc.com/product-detail/C87361.html | MOQ1,$2.4893 | distinct footprint from PA |
| OPA1656IDR SOIC8 | https://www.lcsc.com/product-image/C1849431.html | qty1,$1.5553 | alternative only; manufacturer https://www.ti.com/lit/ds/symlink/opa1656.pdf |
| Neutrik NRJ4HF | https://www.digikey.cn/zh/products/detail/neutrik-americas-inc/NRJ4HF/29427414 | qty1 CNY9.92inclVAT,390indexed | mainlandwarehouseunverified; PCBterminal jack not yet harnessqualified |

Jack manufacturer https://www.neutrik.com/en/product/nrj4hf : mono switched, panel<3mm,11.2mmopening,nut separate. -1 suffix adds sleeve/front-panel connection. Supplier tables incorrectly claim overcurrent protection/current for PhotoMOS; manufacturer governs design. Domestic AQY412S https://item.szlcsc.com/762437.html blocked by anti-bot; no RMB confirmation.

User EEVblog link was inspected as context, not primary engineering authority. usac123 article could not be retrieved. Conclusions rest on the manufacturer/designer documents above and the local circuit extraction.
