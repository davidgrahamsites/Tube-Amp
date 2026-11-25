# Debounce input repair evidence
Owner: Renegade control integration.
Inputs: baseline commit and hashes in baseline.json; native source/schematic/Control PCB; retained TI/Yageo source references in ../../debounce-input-review.md.
Process: guarded native edit, full XML partition/component comparison, native ERC/DRC, two-pole timing enumeration and independent ngspice witnesses. Factories live in ../../tools. This folder contains evidence, never authoring instructions or replacement source CAD.
Outputs: integration/check receipts, one before/after schematic export pair, final page/crops, source observations and visual audit. Existing failures stay explicit; no fabrication qualification.
Human check: inspect the native resistor-to-input paths and scope inputs, supply and gates on the assembled socketed board during power loss. Confirm capacitor identity and remaining PCB routes.
