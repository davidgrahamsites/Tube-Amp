# Acoustic instrument interface review — 20 November 2026

Owner: electrical/acoustic integration. Status: research and proposals; no selected part or circuit mutation.

## Inputs and identity
User-confirmed instruments and primary-use requirements live in [the handoff](../../../Renegade_Codex_Handoff.md#user-confirmed-requirements). A model name does not prove an installed pickup or its impedance.

An exact manufacturer pickup specification for the reported Night Wish 550-D was not located in this search. A third-party listing mentions 550D, but does not establish this instrument’s electronics. No pickup type was assigned.

Enya’s [Chinese manufacturer Nova Go page](https://www.enyamusical.com/nova-go-listing) describes an ES1/D1 smart version with onboard processing and rechargeable battery. Its [English page](https://www.enyamusical.com/nova-go-en) describes the same feature family. Other Nova Go variants exist; these pages do not identify the user’s individual guitar. Do not substitute Nova Go Sonic electric-guitar specifications. Which guitar has the battery remains unknown.

## Buffer proposal
A unity-gain FET-input op-amp buffer is a plausible way to preserve a passive piezo signal while supplying a low-impedance signal to the existing preamp. TI’s [Signal Conditioning Piezoelectric Sensors](https://www.ti.com/lit/an/sloa033a/sloa033a.pdf) explains source capacitance/input resistance interaction and FET/CMOS input choices. The complete circuit needs a bias return, defined input resistance, coupling/protection, supply decoupling and sufficient headroom. A device’s high input impedance alone is not the finished input impedance. A roughly 10 Mohm piezo input is a starting proposal, not a frozen value or a declaration that the guitar has piezo pickups. Magnetic pickup loading may need a selectable lower input resistance.

An external buffer/preamp close to a passive guitar can also handle this interface and keep the high-impedance cable short. This would simplify the amp-side interface, while adding an external box and power source. User wording “off amp buffer” may mean op-amp or off-amp; neither interpretation is a confirmed design decision.

## Speaker proposal
Fishman’s [Loudbox Mini product specifications](https://fishman.com/dp/loudbox-mini-acoustic-amplifier/) list a 6.5-inch woofer and 1-inch soft-dome tweeter. This is evidence for a common acoustic two-way approach, not a recommendation to buy those replacement drivers for this cabinet.

A tweeter can extend high-frequency reproduction, but does not correct an electric-guitar woofer’s midrange response or tube-preamp voicing. Evaluate a compatible woofer/tweeter/crossover system or coaxial assembly. Check measured response, crossover phase/sensitivity, tweeter protection, complete impedance versus frequency and output-transformer load. Do not simply parallel a tweeter across the output. For electric overdrive, evaluate reduced high-frequency output; any mode switching must preserve a valid amplifier load. No crossover frequency, drivers, switch or baffle alteration selected.

## Next check
Identify pickup/control/output hardware and intended clean versus coloured acoustic sound. Compare acoustic-compatible speaker assemblies against the delivered cabinet’s actual opening, mounting pattern, depth, thermal/service clearances and tube-amp load. Retain original amp/cabinet requirements unless explicitly revised. No CAD change, fit release, fresh simulation or purchase is claimed by this research.
