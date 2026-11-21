---
id: VAL-011
type: validation
domain: cross-domain
status: verified
updated: 2026-11-11
---
# v0.4 solid-state spring reverb — scoped native checks

## Claim and scope
The new [engineering package](../../engineering/solid-state-reverb/README.md) implements DEC-007 as an editable design draft. Verification applies to native schematic/board connectivity, reported CAD rules and the bounded electrical reverb AC fixture only. It does not verify construction safety, complete amplifier behavior, actual parts or cabinet fit.

## Evidence
- [Integrated connectivity](../../engineering/solid-state-reverb/validation/connectivity.json): 229 component references,595 mapped connected pins, no missing/split/short/extra pins.
- [ERC](../../engineering/solid-state-reverb/validation/erc.json): zero errors; one explicit GND/PE net-alias warning.
- [Board parity](../../engineering/solid-state-reverb/validation/board-parity.json):115 connected pads,29 connected nets; one-to-one native pin partitions.
- [Native PCB DRC](../../engineering/solid-state-reverb/validation/pcb-drc.json):zero violations,unconnected items and schematic parity issues after corrections.
- [TI-model results](../../engineering/solid-state-reverb/simulation/results.json):dry1kHz gain≈0.9801 with100k source; wet-control/mute dry gain spread≈6.45e-8. Tank R/L and independent wet injection are surrogates, not an acoustic model.
- [Cabinet source](../../engineering/solid-state-reverb/evidence/cabinet-research.md):three exact-listing manufacturer drawings recovered and read. Source supports external geometry/opening; not a final chassis/stock claim.
- [Full limits and corrections](../../engineering/solid-state-reverb/validation/summary.md).

## Revision and method
KiCad10.0.6 native exports/ERC/DRC, native XML pin comparison, pcbnew footprint/pad layout and routed board; ngspice45.2 with bundled XSPICE modules and unmodified TI OPAx134 final1.4 model. Original source and v0.3 remain unchanged. PCB scope is low-voltage reverb only; no mains/HV traces.

## Remaining evidence
Complete the exact protective parts, selected-component integrated amplifier simulation, supplier-qualified parts/tank, custom chassis/panel and fit gates in the [build plan](../../engineering/solid-state-reverb/build-plan.md). Main tube/control/supply PCB layouts are not completed. Physical inspection, protective measures, bench, acoustics and thermal tests remain outstanding. No purchase, upload, supplier message or energized build occurred.
