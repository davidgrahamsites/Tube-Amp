# Reservoir balance / heater-elevation resistor selections

Select Yageo **FMP200JR-52-220K** forR501,R502,R506 and **FMP200JR-52-39K** forR507. Both are2W flameproof5% axial resistors,500V maximum working rating further limited by power/temperature. Use the already prepared FMP20015.24mm-pitch footprint, with exact value retained per reference. Manufacturer body/lead dimensions match the100k FMP200 dossier.

Domestic November11 observations: C1759543 (220k),MOQ10,¥0.3018 each,3020stock; C3421367 (39k),MOQ10,¥0.3312 each,2670stock. Total minimum purchase¥6.33 before shipping. Links: https://item.szlcsc.com/1850325.html ; https://item.szlcsc.com/3986678.html .

check_power_divider_resistors.py uses the existing assumed510.31V supply bound and5% divider tolerance. R506 reaches439.775V and0.899W; R507≤83.606V and0.171W. R501/R502 reach365.562V/0.580W under the previously documented Nichicon20°C leakage screen. These bounds pass at70/100°C assumptions. **R506 fails the125°C power screen**; place these parts in a verified cool area≤100°C, preferably lower, with body standoff/clearance and no nearby capacitors exposed to resistor heat. No actual cabinet temperature is established.

The rejected400V Aishi reservoir candidate is not restored. Final reservoir selection still needs hot leakage/ripple/startup evidence. Heater-reference voltage can approach83.6V under this assumed corner; tube heater-cathode limits, actual heater winding insulation/leakage and startup sequencing require separate checks. The static resistor selection does not qualify that interface or the real transformer.

## November26 expanded R506 boundary

[HD-001](heater-divider-rating/review.md) supersedes any interpretation of the normal-only pass as fault qualification. At the550V extended ceiling and100°C, a shorted C505 places550V/1.52355W on R506 with the declared drift allocation, exceeding its continuous ratings. Higher-voltage alternatives are screened but not adopted; lower-divider open and upper-feed short also require heater-reference protection review. R501/R502 remain under their earlier, separately limited reservoir screen.
