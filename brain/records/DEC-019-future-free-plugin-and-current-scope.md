---
id: DEC-019
type: decision
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Finish the hardware; retain a future free amplifier plugin

FB-130: after the hardware design, the user wants DSP/VST emulation released
free to the public, useful for recording and promoting the amplifier. This is
a future project direction, not a current plugin implementation or publication
authorization. Preserve block interfaces and evidence so a later model can
be calibrated against hardware frequency response, clipping, dynamics, supply
interaction and reverb. DSP accuracy, supported platforms/formats and release
conditions remain future work; free price does not decide a source-code license.

FB-131: the user supplied https://circuitcodex.com/ as optional reference.
Inspected its home, about/verification page and linked GitHub repository on
2026-11-25. It offers redrawn circuits, KiCad sources and operating-point
checks. Its own limitations explicitly say tube models target DC bias, not
AC/distortion/tone, and layouts are connectivity diagrams without physical
spacing or lead-dress qualification. Use targeted references and cited original
sources; its badge is not evidence that our amplifier or a VST is validated.
Sources: https://circuitcodex.com/about/ and
https://github.com/TheAnalogMaker/circuit-codex . No assets imported.

FB-132: do not broadly overhaul the amplifier to accommodate these ideas or
the reference archive. Preserve the present blocks and prioritize specific
defects and unmet current requirements. Datasheets describe existing blocks;
adapters and a free plugin do not expand today's hardware scope. All six
engineering scopes remain incomplete; this scope restraint does not waive
protection, PCB, sourcing, fit or screw-access checks.

FB-133: later extract useful functional blocks from CircuitCodex, classify
them by electrical/operating characteristics, store them in ICM and make them
retrievable through RAG. Preserve source URL and revision, asset-specific
license/attribution, schematic references, model applicability and evidence
status. Use structured numeric fields with units and conditions for filtering
(gain, supply/current, headroom, impedances, bandwidth, load and control limits);
RAG supplies descriptive context and citations. Retrieval identifies candidates,
not certified compatible circuits: check actual interface envelopes and source
evidence before reuse. Treat DC-only evidence as DC-only. Future extraction,
index implementation and bulk import are deferred; no current hardware overhaul.
