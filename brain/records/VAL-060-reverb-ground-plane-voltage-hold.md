---
id: VAL-060
type: validation
domain: pcb
status: documented
updated: 2026-11-25
---
# Reverb pour candidate exposes signal-voltage classification fault

[Owned review](../../engineering/whole-amp/pcb-measured-r/ground-planes/review.md) creates and checks a Reverb bottom-ground candidate: one14,061.69mm² region, four mounting exclusions, exact preservation of all previous board objects/drills,0strict DRC/0opens. All active native files remain unchanged; the candidate is **not adopted**.

Native connectivity and prior overload evidence invalidate treating the entire Reverb board as low voltage merely because its op-amps use±15V. FX_RETURN is normalled to the tube-derived SEND, with recorded generic-fixture excursions−135.094/+97.777V. R612/MIX_OUT/JR5 carry that dry path and R618 couples the wet output. Current global0.25mm rules and “Low voltage only” connector metadata do not qualify it. A clean candidate DRC under those rules is inadequate. Exact worst-case normal/fault voltage and C607 differential stress remain to derive.

T03 logical earth/signal bond is already complete; physical return mapping is still open. Next: correct misleading interface metadata, quantify voltage domains, qualify spacing/connectors/passives and rebuild domain-aware pours before adoption. TI's OPA2134 layout guidance also requires revisiting local ceramic bypass loops. All six goal scopes and China purchase qualification remain incomplete. No fabrication release, supplier contact or purchase.
