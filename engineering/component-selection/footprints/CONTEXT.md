# Selected-part footprint preparation
Inputs: component dossiers, manufacturer package dimensions and original native-board hashes.
Process: footprint factories prepare local KiCad geometry and integration-manifest.json records intended assignments. Preserve native boards; this folder does not own final placement/routing.
Outputs: footprint libraries, previews, dimensional checks and a planned integration manifest.
Human check: compare physical purchased parts and manufacturer maximum dimensions with pads/courtyards before integrating or fabricating.

November21 explicit KNSCHA_82CL0120 and Yageo_FMP100_P10.16 library entries are prepared by the guarded package factory in ../../whole-amp/pcb-measured-r/tools/integrate_service_wave_parts.py using dimensional equivalence documented in the LV/bias-resistor dossiers. PCB placement and route repair remain owned by that module.

November24: [Panasonic FR-A module](panasonic-fr/CONTEXT.md) owns the three exact long-lead packages used at seven references, explicit finished-hole assumptions and manufacturer excerpt. Its tools generate the local library and validate native integration/drill evidence; PCB mutation remains in the PCB integration module.
