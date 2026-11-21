# Repack the original amplifier into the delivered cabinet

Owner: Renegade integration agent. Cabinet fixed by user November19. Inputs: ../fit-register.json, original circuit, selected component evidence. Output: revised internal component choices and native board/chassis assembly, preserving functions.

1. Resolve the actual speaker mount and chassis opening with a few measurements from the received cabinet. Do not assume an ambiguous catalogue diameter proves the delivered mounting pattern. Select a documented guitar driver for that mount and depth; no speaker is locked yet.
2. Allocate physical envelopes first to the six tubes/sockets, PT/OT/choke/auxiliary supply and speaker. Keep tube extraction, hot-part clearance, shielding/earth and service paths explicit.
3. Replace oversized power-component candidates before routing. Investigate series electrolytics as an alternative to the bulky50uF film blocks while preserving nominal50uF and voltage margin. This requires balancing/leakage/ripple/startup checks; it is not an approved circuit change. Manufacturer GU table reviewed as an early lead lists100uF400V envelopes20×35,22×30 or25×25mm. Exact suffix, stock and fit still need closure. Source: https://datasheet.lcsc.com/datasheet/pdf/5b27a583f417fa58ae95c6e91a6b0a25.pdf?productCode=C1582832 .
4. Repack control/reverb using suitable small parts and consolidate wiring where serviceable. Existing230×110 and160×100mm outlines are not requirements. Preserve needed voltage spacing and input noise control.
5. Revise native boards in a new design revision after the envelope assignment; retain routed originals as history. Do not rerun historical generators over saved boards.
6. If tank arrived, identify its label and measure body/mounting and isolated coil DC resistances; use published references and a bounded low-level characterization plan. If absent, select a documented equivalent with domestic supply. Do not make another unanswered supplier request the critical path.

No replacement part is declared fit based on search keywords. Speaker search in this pass did not establish a direct312mm-PCD/270mm-cutout candidate. Listings mentioning312mm often mean frame diameter; distinguish frame from bolt circle. A new part number without verified geometry would repeat the original mistake.
