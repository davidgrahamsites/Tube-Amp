# Capacitor elevation and supported-bank options

November 26, 2026; FB-144. Owner: component selection and mechanical integration. This is a packaging comparison, not a new capacitor selection or a fourth-board adoption. It follows the [exact-package review](review.md). Four capacitors C12/C13/C25/C26 remain in the power-supply functional block.

## What the current candidates permit

The [Panasonic EZPV R9 specification](https://industrial.panasonic.com/content/data/CP/PDF/ezpv_je.pdf), drawing/page 2 and use precautions/pages 23–24, gives the candidate geometry and warns against excessive lead-root force. The exact EZPV60506MTC candidate has exposed lead length 4 ± 2 mm. Against the current 1.6 mm nominal PCB, the minimum 2 mm lead leaves only 0.4 mm below the board with the body seated; a 3 mm body lift would leave the shortest lead 2.6 mm short of the underside. This calculation even omits solder protrusion and board thickness tolerance. A useful raised platform cannot be obtained simply by leaving these leads long. CRC FC6136's 4 ± 1 mm leads also do not provide a tall mounting platform. Neither part is selected by this comparison.

The parts and their solder joints must not be assumed to support a suspended mass above other components under cabinet vibration. Engineering interpretation: use a designed body support and PCB/chassis load path, and keep the terminals free of sustained bending loads. Arbitrary adhesive is not a qualified support method: Panasonic specifically requires checking the effects of fixing resin on the part. Its soldering conditions are component heat limits, not proof that any enlarged hole or solder joint is manufacturable.

## Options

| Arrangement | Benefit | Required checks / downside | Current disposition |
|---|---|---|---|
| Dedicated capacitor area on revised power PCB | Fewest extra interconnects; supports the intended three-board architecture; accessible assembly | Repack from actual body/pin limits, reserve heat/lead/support space and service access | Preferred starting layout |
| Capacitors elevated on leads alone | Apparent footprint saving | Short leads, lead-root/joint loads, exposed HV, obstructed components and screws | Do not use as the packaging solution |
| Capacitor PCB supported by chassis-mounted brackets/standoffs | Moves capacitor bank to another plane while retaining power-block ownership | Adds PCB, mounting, insulated/rated connections, underside HV clearance, removal sequence, mass and heat checks | Valid candidate if the populated model shows a real benefit |
| Suitable chassis-mounted capacitors with an insulated harness | Could free PCB area and transfer mass directly to structure | Requires exact suitable capacitor/mounting type, protected terminals, connectorized wiring and revised current/return paths | Alternative, no exact part selected |

A supported upper tier should not sit over hot power resistors/regulators, sensitive preamp circuitry, or mounting screws that must remain reachable. Put its fasteners where the bank can be removed without unsoldering wiring or removing the wooden rear cover together with electronics. It attaches to the removable metal assembly, never the removable wooden back. Support comes from the bracket/standoffs, not electrical headers.

If a bank moves, each supply node and its return remain explicit. Do not combine C12/C13/C25/C26 just because they are mechanically adjacent. Keep associated charging/decoupling loops short and route their supply/return pairs deliberately. Exact connector voltage/current, creepage/clearance and mating access must cover the actual high-voltage domain; a generic small board-to-board header is not qualified. Required discharge/protection behavior must include the removable bank. No bare field wires soldered directly to the main PCB are proposed.

Height savings cannot be inferred from reduced plan area. Upper-board height equals the lower component envelope plus the required separation, upper PCB thickness, capacitor height and any body seating/support allowance. The maximum Panasonic body is 41 mm high; the CRC body is 51 mm. A second tier therefore consumes substantial cabinet height before clearances, supports and extraction space. The [calculation receipt](results/assembly-options.json) quantifies conditional packaging dimensions without inventing a usable cabinet volume or HV clearance.

Next: compare the supported bank against a repacked single power PCB in the common populated assembly, using actual speaker/magnetics and socket envelopes. A bank daughterboard would add a physical PCB even though it retains the same functional block; the user's earlier three-board preference remains the baseline. No assembly or fabrication fit is approved by this proposal.

Conditional body-only comparison: Panasonic 126 × 62 × 41 mm; CRC 127 × 82 × 51 mm, both in a 2×2 arrangement with a 10 mm inter-body gap. That gap is a Panasonic neighbor recommendation and only a comparison assumption for CRC; neither value is an electrical-clearance specification. The nominal upper PCB plus body adds 42.6 mm or 52.6 mm before lower parts, separation and mounting. See the [five-pass fit plan](../../../plans/capacitor-bank-fit/CONTEXT.md) for the expanded comparison.
