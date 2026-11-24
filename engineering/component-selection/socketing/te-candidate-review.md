# TE DIP socket candidates — November 24

Keep sockets. No measured or manufacturer-supported material performance
problem has justified removing one. These candidates improve the available
mechanical/rating evidence; they are not yet released parts.

| Devices | Preferred candidate | Domestic loose stock | Minimum buy / unit price |
|---|---|---:|---:|
| U1, U2 | TE 1-2199298-3, DIP-14 | 5,865 | 17 / ¥1.8944 |
| U10, U11, U12 | TE 1-2199298-2, DIP-8 | 3,390 | 5 / ¥1.4305 |

Read-only observations from [domestic DIP-14](https://item.szlcsc.com/3582459.html)
and [domestic DIP-8](https://item.szlcsc.com/289990.html), November 24. Loose-part
counts are distinct from the pages' JLC assembly inventories. Minimum purchases
total roughly ¥39.36 before freight, although five installed sockets use about
¥8.08 of parts at those unit prices. Availability is dated; no order or address
check was made. CONNFLY remains an inexpensive alternative pending complete data.

The [TE product page](https://www.te.com/en/product-1-2199298-2.html) and
manufacturer drawing C-2199298 support 1 A/contact, 20 mΩ maximum contact
resistance, 250 VAC/DC working rating, −40…105 °C and 50 mating cycles minimum.
The 1,000 VAC dielectric test is **not** a working-voltage rating. Use the
drawing's 3 ±0.25 mm tail length; ignore the product page's erroneous inch field.
The archived manufacturer-authored Rev A drawing was obtained from a
[distributor mirror](https://www.ariat-tech.tw/datasheet/1c/1-2199298-1.pdf).
TE currently lists A1: comparison with the current revision remains mandatory.
The specification download was unavailable; it is not treated as reviewed.

## Fit and holes

The rectangular tails are 0.60 ±0.10 by 0.17 ±0.05 mm, with a maximum corner
diagonal of 0.734 mm. The drawing explicitly calls for **Ø1.0 mm PCB holes**.
With a proposed finished-hole allocation of 1.00 ±0.05 mm, the minimum hole
leaves about 0.216 mm total diametric allowance. Fabricator confirmation is
still needed. A rectangular tail can use a round hole when its specified fit
allows it; it does not automatically require an oval slot.

All five native DIP footprints currently have Ø0.8 mm holes and undersized
courtyards for this candidate assembly. They must be revised, including annular
rings and clearance checks, before these sockets can be adopted. The mechanical
screen finds no candidate body overlap with supported neighboring courtyards,
but that is not a full component or chassis collision check.

Socket maximum height is 5.3 mm. TI's selected
[SN74HC14N](https://www.ti.com/lit/ds/symlink/sn74hc14.pdf) and
[OPA2134PA](https://www.ti.com/lit/ds/symlink/opa2134.pdf) package drawings give
5.08 mm maximum height above the IC seating plane. Conservatively stacking
these gives **10.38 mm above the PCB**. Reserve 12 mm for the assembly and an
additional provisional 15 mm upward extraction space, subject to actual tool,
grip and retention checks. The 14-pin IC body can be 19.69 mm long, exceeding
the socket's 17.98 mm maximum: a socket-only outline would be insufficient.

TE specifies 0.20–0.30 mm mating lead thickness. The reviewed TI drawings give
0.25 mm nominal thickness, without a full tolerance in those drawings. Nominal
compatibility is promising; it is not proof of full tolerance compatibility.
Confirm the manufacturer's limits or actual samples, including lead forming,
pin-1 alignment and vibration retention. U2's exact package drawing also needs
its own final cross-check. No generic socket is approved for the TO-220 regulators
or the supervisor carrier; their current, heat and pin mapping are separate gates.

`socket-envelope.json` is the electrical module's provisional dimensional seam.
The mechanical module consumes it read-only through `check_socket_fit.py`; it
does not make purchasing or electrical decisions. Final chassis clearances must
include insulated harnesses, socket withdrawal, heatsinks and screw access.
