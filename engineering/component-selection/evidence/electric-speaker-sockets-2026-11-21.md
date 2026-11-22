# Electric speaker and chassis socket evidence — 21 November 2026

## Task card and ownership

Owner: speaker/socket research worker; integration remains with the main electric-build agent. One job: establish usable component geometry, supply evidence and release restrictions. Inputs are the delivered cabinet measurements, current electric circuit (four 12AX7 and two EL34), retained selection dossiers and manufacturer literature. Output is this evidence dossier only. No shared register, schematic or CAD file was changed. No seller was contacted and nothing was purchased.

Success means a component can be traced to exact manufacturer data and a low-quantity mainland source; fit release additionally requires all mating dimensions and service clearances. This pass improves geometry evidence but does not close procurement or fabrication release. Human check: compare the ordered part to its drawing, then use an actual speaker or accurate manufacturer template against the delivered baffle before drilling.

## Speaker: retain Celestion Seventy 80, 8 ohms as a bounded candidate

[Manufacturer product page](https://celestion.com/product/seventy-80/) specifies 80 W, 8/16 ohm options, 98 dB sensitivity, 80–5000 Hz response, 309 mm outside diameter, 297 mm hole PCD, four 7.9 mm holes, 119 mm total depth and 134 mm magnet diameter. The 8-ohm version has 6.1-ohm nominal DC resistance. Use the amplifier output transformer’s 8-ohm connection for this version. Its power rating is a candidate margin, not proof against an unbounded clipped amplifier output or incorrect load selection.

**New fit evidence:** the [official Celestion 2024 brochure, printed page 34](https://celestion.com/wp-content/uploads/2024/01/Guitar_Brochure_2024.pdf) explicitly specifies a **283 mm cutout**, 88 mm chassis depth including gasket, and 31 mm magnet depth. The delivered cabinet aperture is **270 mm**. The missing cutout dimension must no longer be treated as unknown/no restriction.

Calculated consequences:

- The aperture is 13 mm smaller in diameter, or 6.5 mm per side, than the published cutout.
- For rear mounting, this does not alone prove the speaker cannot work. It DOES prevent a documented direct-fit claim: the baffle edge must clear the moving surround/cone at excursion, gasket bearing must be sound, and the opening must not interfere with the basket. Front mounting through the aperture cannot be assumed.
- 210 mm between adjacent holes gives 210 × sqrt(2) = 296.98 mm opposite spacing for a square pattern. This agrees numerically with the speaker’s 297 mm PCD. The reported 294 mm diagonals remain conflicting evidence. Do not average them or force bolts into the basket.
- A nominal 160 mm baffle-to-rear-edge distance minus 119 mm speaker depth leaves 41 mm. This is arithmetic only: B is not a full independent clearance survey, and rear wood, terminals, connectors, chassis/tubes, gasket and mounting hardware still need checking.
- Cabinet inside height 383 mm minus frame diameter 309 mm leaves only 74 mm TOTAL above and below a centred frame. Tube/speaker collision checks must use actual baffle centre location and the cone-shaped basket envelope, not place two rectangles independently.

**Disposition:** suitable electric-guitar type; not selected for purchase or released for fixed-baffle fit. Do not cut/enlarge the cabinet aperture automatically. First establish rear-mounted surround clearance. If it fails, investigate a documented alternative or a separately designed adapter/replacement baffle; a 10-inch speaker cannot directly span the existing 270 mm aperture without an adapter.

## Mainland supply observation, not a verified order

[Shenzhen Mable socket catalogue](https://www.mableaudio.com/en/products.asp?sid=38) remains a local supply route for sockets. The existing supplier relationship proves cabinet/tank delivery only, not these socket stock quantities.

Speaker search found the following leads; none qualifies as a verified low-cost one-unit mainland SKU:

| Source | Observation on this pass | Disposition |
|---|---|---|
| [Pro001 Celestion catalogue](https://www.pro001.com/brand/show.php?itemid=126&page=2) | Seventy 80 advertised; public market price RMB 3,589; listing claims 17 pieces; member price hidden | Price is unattractive; exact impedance and quantity-one delivery not checked. Inventory counter is only a listing claim. |
| [Aobaobio Celestion catalogue](https://www.aobaobio.com/brand/57.html) | Same public RMB 3,589 price; generic 1,000-unit counters across catalogue | Do not treat these counters as physical inventory evidence. |
| [Taobao index lead](https://tao.hooos.com/search?page=1&w=celestion) | Index lists TomLe Fender Deluxe VM G12P-80 and Mag guitar-speaker ranges | Third-party discovery lead only. Exact Taobao variant, impedance, quantity-one price, authenticity and mainland dispatch remain unverified. No engineering claims derive from this index. |

Searches of exact English and Chinese model names did not yield a verifiable one-unit Taobao offer in accessible primary listing content. This is a supply hold, not permission to invent a price or substitute a generic speaker.

## Sockets: retain chassis-mounted solder-lug parts

[Belton manufacturer catalogue](https://www.belton.co.kr/product/product.html?code=00) identifies VTB8-ST and VTB9-ST-2 as wiring types with panel saddle mounting, glass-fibre-filled PPS bodies and phosphor-bronze terminals. Chassis mounting carries tube insertion/removal force and lets the PCB remain a separately removable functional assembly. Do not turn the six sockets into unverified PCB footprints to complete routing.

| Function and quantity | Candidate | Mainland catalogue observation | Status |
|---|---|---|---|
| Four 12AX7 sockets | Belton VTB9-ST-2, solder-lug/front-mount version | Mable USD 3.85 shown; retained detailed listing starts at quantity 10 | Exact plating/suffix, four-piece quote, stock and mounting pitch unresolved |
| Two EL34 sockets | Belton VTB8-ST, solder-lug version | Mable USD 5.30 shown | Geometry improved below; two-piece RMB quote/stock, rating and retainer match unresolved |
| Alternative noval saddle | Belton VTB9-ST-1 | Mable USD 3.85 shown | Drawing contains mounting pitch; mounting direction differs, so not a silent substitution |

Gold plating is not a requirement for audio quality here. Supplier pages use inconsistent plating descriptions for unsuffixed VTB parts. Order suffix/material/finish must be explicit rather than assumed from a catalogue family image. Do not substitute the cheaper VT family while retaining VTB geometry.

### Manufacturer drawing geometry

Primary manufacturer-authored drawings were opened and visually inspected, hosted by HifiCollective:

- [Belton VTB8 series drawing, filename revision 231219](https://www.hificollective.co.uk/sites/default/files/2024-03/VTB8%20SERIES.pdf).
- [Belton VTB9 series drawing, filename revision 210824](https://www.hificollective.co.uk/sites/default/files/2023-04/VTB9%20SERIES%20%282%29_1.pdf).

VTB8-ST: saddle is 50 mm long and 34 mm wide; mounting-hole centres are 40 mm apart; slot width is 3.5 mm. Drawing shows body diameters 30 mm on the tube side and 25.4 mm on the terminal side. Axial body dimension is 13.5 mm plus 9.3 mm terminal projection (22.8 mm overall body/terminal stack). Mounting saddle has an offset: locate the actual chassis plane from the section rather than subtracting one arbitrary nominal height. These dimensions describe the socket, not the EL34, retainer or safety clearance envelope.

VTB9-ST-2: drawing shows 18.5 mm body diameter, 16.5 mm overall axial stack, 8 mm terminal-side segment, 3.3 mm fixing holes and 2 × R3.5 end radii. **The ST-2 mounting-hole centre distance is not explicitly dimensioned in this sheet.** Do not copy the neighbouring ST-1 dimension into its drilling template. The ST-1 drawing explicitly gives 28.5 mm mounting centres and 3.5 mm fixing holes; its saddle geometry and mounting orientation are separate.

These sheets do not establish working voltage, contact-current rating or temperature limit for the selected ordered suffix. Those remain electrical-rating holds. For EL34 heaters, contact capability must cover the selected tube’s heater current plus applicable margin; plate/screen pin insulation must cover the actual amplifier voltage/transients. A generic “high insulated” description is not a numerical rating.

## Retention, visibility and service restrictions

The retained Mable EL34R-47MM/with-ring retainer lead has not been dimensionally matched to VTB8-ST. A 47 mm retainer spacing must not be assumed to share the socket’s 40 mm screw centres. A separate retainer bracket may be required, with its own chassis holes and removal envelope. The manufacturer catalogue explicitly names certain retainers for VT8 variants, which does not prove compatibility with the VTB8 saddle.

Keep sockets and retainers on the fixed metal chassis. No chassis/socket/drill load goes through the removable rear wooden panel. Preserve socket-key orientation and short grid-stopper connections near their valve pins. Keep mains/output/heater wiring away from high-impedance input and reverb-return blocks. Reserve tube withdrawal space plus hand access; do not assess serviceability using the seated glass envelope alone.

Tube glow through the rear slots remains an optional sight-line aim. Do not move high-gain stages into the power-transformer field or remove required shields/guards to expose glow. No tube or terminal may depend on the removable rear wood for mechanical support. Metalwork bonding, hot-glass guard and finger-access checks remain part of the integrated chassis review.

## Integration actions

1. Update Seventy 80 reference cutout to 283 mm and retain the 270 mm delivered aperture as a fit hold.
2. Add VTB8-ST 50 × 34 mm saddle and 40 mm mounting centres to provisional mechanical envelopes, explicitly excluding the retainer/tube/service envelopes.
3. Keep VTB9-ST-2 pitch unverified; obtain the exact ordered drawing or measure the supplied part before drilling. ST-1 is a documented alternative only after a deliberate mount-direction decision.
4. Verify domestic quantity 4 + 2 socket terms and one exact 8-ohm speaker SKU before calling the BOM order-ready.
5. Do not release speaker, socket drilling, or adjacent PCB clearance geometry on this dossier alone.

## Scoped ICM check

This file has one evidence job and introduces no mixed-purpose script/CAD factory. Inputs, dated observations, calculations, unverified claims and integration actions are separated. It changes no source design or part-selection state. Parent integration must register this evidence and rebuild the project catalogs. Structural verification of that integration is owned by the main agent.
