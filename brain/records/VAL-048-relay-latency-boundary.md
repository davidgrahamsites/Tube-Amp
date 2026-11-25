---
id: VAL-048
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Relay latency and gate-resistor correction

[Owned review](../../engineering/whole-amp/control-switching/relay-latency-review.md) corrects the candidate/native R341 boundary: native1k remains in all three representations; proposed4.7k has not been adopted. Retaining1k fails the candidate base-drive allocation, and a new read-only guard records this explicitly.

Forty-eight analytical coil cases and two SPICE cases with two refinements show substantial current remaining after1ms. Current decay to5% is conditionally4.666–13.947ms; this is not contact-release timing. A separate ideal-gate re-enable simulation failure is retained. Do not credit K3 as instantaneous rail-fault muting or claim complete driver/audio validation.

No native circuit, functional block, socket or footprint change. All six scopes and Chinese purchase/Shanghai delivery, populated three-board fit and drill-access requirements remain open. Next: quantify the audio disturbance before contact motion and qualify the complete supply/reset/mute interface before adding further timer complexity or integrating CAD.
