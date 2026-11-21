> November 20 photo update: model and second marking are now photograph-confirmed; socket labels and meter-specific steps are in [received photo intake](received-tank-photo-intake-2026-11-20.md). Earlier requests below for a label photograph are closed. DC coil readings have since been supplied; see tank_received.electrical_measurements in ../fit-register.json. AC and current qualification remain pending.

> **Latest evidence, November19:** seller reply relayed by user confirms the delivered tank as3springs,600ohm input,2250ohm output,medium decay,input insulated/output grounded,no lock,horizontal/open-side-down. This is the current electrical design basis, replacing the800/2575 assumption. User subsequently transcribed model M8EB2C1B and marking R2610270015 onNovember20; physical size still needs identification because Mable reuses the code. Do not repeat the already answered specification questions.

# Reverb tank identity and electrical evidence — 19 November 2026

**Current result: received tank model marking M8EB2C1B is recorded; public product specifications and a dimension drawing found, but no complete exact-unit electrical datasheet located.** Do not equate a similar catalogue code with a verified equivalent.

## Original manufacturer reference

Archived Accutronics manufacturer document (third-party mirror): https://bustedgear.com/images/resources/Accutronics.pdf ; saved unmodified as `../evidence/accutronics-reference.pdf`. Pages5/6 were rendered and inspected. Type8/E/B reference: input800ohm at1kHz,58ohm DC,150mH; output2575ohm at1kHz,200ohm DC,400mH. Table lists±10% for impedance/inductance/DC resistance and3.1mA recommended AC drive, not an absolute maximum. Reference body234.95×85.725×33.32mm. CodeC is input insulated/output grounded; finalB means horizontal/open-side-down. Medium decay ranges differ between tables:2–3s and1.75–3s. These historical values are not certification of Mable production.

The nominal150mH/58ohm simple series-RL model gives944ohm at1kHz, not800;127mH gives approximately800. Existing simulation uses58ohm/127mH. Retain that as a stated impedance-matched approximation; do not overwrite it with150mH without measured frequency data. No tank acoustic transfer or maximum drive qualification follows from these numbers.

## Mable evidence: conflicting variants

| Supplier item | Listing text | Conflict/open detail |
|---|---|---|
| MAGT0037 M8EB2C1B / TPS3EB2C1B |235×85mm;3springs;800ohm input;medium;input insulated/output grounded|Output printed2.575ohm, likely omitted k; height and full mounting orientation not stated clearly|
| MAGT0046 M8EB2C1B / TPM3EB2C1B mini |180×60×36mm;3springs;600ohm input/2250ohm output;horizontal/open-down|Its linked3spring code chart instead gives E=800ohm,B=2575ohm. Drawing labels178mm total length,60width,37overall height and6.5connector projection. Do not reconcile by assumption.|

Sources: https://www.mableaudio.com/en/productview.asp?sid=10656 and https://www.mableaudio.com/en/productview.asp?sid=11692 . The latter failed the web parser; public HTML was fetched and decoded asGB18030. Saved HTML and linked code/dimension images are under evidence. Image URLs: https://www.mableaudio.com/uploadFile/Picture_small/202501201517567308.jpg and https://www.mableaudio.com/uploadFile/Picture_small/202501201618024178.jpg . Initial downloads accidentally retained an extra/en directory and returned404; corrected relative URLs succeeded. Both images were inspected.

## Needed for our circuit

Obtain photo of the exact quoted unit label plus input/output impedance and test frequency, coil DC resistance, recommended drive current with RMS/peak convention, maximum drive/test conditions, connector-shell grounding, mounting position, dimensional drawing and included grommets/bag/cables. No maximum safe current can be assigned from the present catalogue.

The low-voltage driver can be assessed for either candidate after identity is fixed. The faceplate and expression pedal still adjust wet level only; dry remains unchanged. Changing tank impedance or mounting does not authorize an automatic component or cabinet substitution.

## Circuit follow-through

Historical simulate_reverb.py uses input58ohm+127mH and output200ohm+409mH for the earlier800/2575 reference. Those runs are not validation of this delivered tank. Revise the tank model only with explicit assumptions or measured DC resistance/impedance versus frequency; the supplier statement omits test frequency and drive current. Recheck driver current/headroom, input high-pass response, recovery gain/noise and clipping. Do not assign the old reference3.1mA current as a verified limit of this tank. No native circuit or simulation change was made during this evidence intake. A received-unit label photo and low-level bench characterization can close gaps without another supplier datasheet request.

## November20 exact-label search

User transcribed **M8EB2C1B** and **R2610270015** from the received tank. The second string is recorded as a serial/production marking; its format/date is not decoded. No label photograph was inspected.

Freshly downloaded [Mable MAGT0046 product page](https://www.mableaudio.com/en/productview.asp?sid=11692), saved as `../evidence/mable-MAGT0046-2026-11-20.html`, is headed M8EB2C1B and names TPM3EB2C1B in the description. It gives600ohm/2250ohm,3springs,medium decay,insulated input/grounded output,no lock,horizontal open-side-down. These agree with the seller statement. HTML decoded asGB18030; the web text parser failed Unicode decoding but the direct public download succeeded. No linked PDF/DOC/XLS electrical datasheet was found in this page.

The page links a [dimensioned drawing](https://www.mableaudio.com/uploadFile/Picture_small/202501201618024178.jpg), already saved as `../evidence/mable-mini-tank-drawing.jpg`. Drawing and prose dimensions remain inconsistent: drawing178x60x37mm versus text180x60x36mm. Treat these as catalogue evidence, not measured dimensions of the received unit.

Searches for the exact model with PDF/datasheet, the serial marking, Mable, MOD Electronics and Amplified Parts did not locate a complete exact-Mable-unit electrical datasheet. This is a bounded search result, not proof none exists. The serial search produced no useful identification source.

[MOD Electronics' own specification table](https://www.modelectronics.com/reverb-tanks/sound-samples-product-info) gives800/2575ohm at1kHz for its **MN-8EB2C1B** mini model. That is a different named product; do not apply it to the received Mable unit merely because the code is similar. The older Mable MAGT0037 listing also uses M8EB2C1B but describes a larger235x85mm tank and800ohm input. The model string alone does not resolve these catalogue conflicts.

Working basis remains the seller-confirmed600/2250ohm specification, supported by MAGT0046 prose, with explicit uncertainty. Missing exact-unit items: impedance test frequency/tolerance, coil DC resistance and inductance, recommended/maximum drive current and test conditions, complete physical mounting confirmation. No request to repeatedly ask the seller for a datasheet, no substitution and no fabrication release. Current600R-1 simulation assumptions remain assumptions; label capture does not validate them.

## Measurement route
[Characterization plan](tank-characterization-plan.md) separates DC resistance, low-level AC impedance and sample operating-level tests from unavailable manufacturer current ratings. Instruments, proposed conditions and scope limitations are recorded. No tests have been performed.
