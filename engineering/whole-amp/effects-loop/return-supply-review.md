# RETURN floating-supply diagnosis — 24–25 November 2026

Owner: electric integration. Authority: FB-102 and the through-chassis execution card. This is an unadopted circuit experiment. The original production circuit, functional blocks, PCB files and all mounting holes are unchanged.

## Task card and interface

Inputs: the existing `tools/return_driver.py` experiment at revision960652f5, TI's unmodified OPA462 final1.3 model, `return-headroom-review.md` and the existing effects-loop review targets. One job: isolate the two20kHz solver failures and check a physically implementable candidate change without deleting bypass or weakening the solver settings.

Factories: `tools/return_supply_diagnostics.py` owns the causal matrix; `tools/return_isolation_check.py` owns regression and refinement through `return_driver.measure(case, step_divisor, extra_nodes)`; `tools/audit_return_supply.py` independently checks retained cases, generated decks, nominal screens, controls, source hashes and native preservation. The measurement seam's defaults remain unchanged; saved additional probes are read-only. Products are `results/return-supply-*` and `results/return-isolated-*`. This review is their public interpretation. Estimated scope: one diagnostic pass, not a completed effects-loop design.

Done-condition for this pass: reproduce the failures, retain unsuccessful variants, identify a completed bounded comparison, check numerical sensitivity and record what remains unqualified. Required human evidence: a correctly powered and protected bench circuit, measured HF behavior and startup/thermal results before any hardware claim. No order, supplier message or fabrication upload is part of this pass.

## Research basis

[TI SBOA510 section2](https://www.ti.com/lit/an/sboa510/sboa510.pdf) explicitly reports stable lab operation with100nF across the moving supply outputs. Therefore our failed simulation does **not** establish a defect in TI's example. Our gain, load and rails differ. Section5 also discusses deliberately biasing the enable interface; the five-pin model used here omits that interface. It cannot qualify enable wiring, disable behavior or associated noise susceptibility.

The [OPA462 datasheet, figures36–38](https://www.ti.com/lit/ds/symlink/opa462.pdf) provides capacitive-load and isolation-resistor behavior under its stated test conditions. This motivates a resistor-isolation experiment; it does not validate our100nF bootstrap combination. The device is an8-pin HSOIC with exposed thermal pad, not a DIP. A simple socket adapter would still need a demonstrated heat path and controlled wiring. No socket exception or adapter selection is made.

## Causal matrix

All variants retain135.1V requested peak, gain100,340kΩ parallel100pF load,1kΩ output resistance and ±166.6/±173.4V ideal fixed supply corners. The original interval, Gear2, tolerances and maximum step remain unchanged. Each causal case has a45s wall limit. Electrical duration is30ms at20kHz.

| Change from original experiment |166.6V corner|173.4V corner|Meaning|
|---|---|---|---|
|None|Timestep failure|Timestep failure|Original upper-follower failures reproduced|
|50Ω after each rail follower; its local feedback before the resistor|Completes|Completes|Retains100nF at the main amplifier's moving power pins|
|Replace100nF with10nF|Wall timeout|Wall timeout|No electrical conclusion|
|Omit100nF|Completes|Completes|Causal diagnostic only; not a proposed circuit|

The observations implicate the modeled floating-output/bypass interaction. They do not distinguish every possible physical-instability and macro-model numerical mechanism. The original failed cases remain in `return-real-*`; none was overwritten with a passing result.

## Isolated-rail follow-up

Ten original bootstrapped stimulus/supply combinations plus two half-step20kHz refinements all complete. The90s per-case wall bound accommodates the finer timestep; it does not shorten electrical duration or relax tolerances. Low-frequency runs retain at least30cycles. All use the same unmodified manufacturer model with midpoint nodesets, which are initial guesses rather than clamps. Runtime logs identify ngspice45.2,27°C and PSpice compatibility mode.

|Requested output|Loaded port behavior, both corners|
|---|---|
|135.1Vpeak at82.4Hz|Gain error approximately−0.00017dB|
|135.1Vpeak at1kHz|Approximately−0.00101dB; modeled harmonics2–10 THD≈0.00049%|
|135.1Vpeak at5kHz|Approximately−0.019dB|
|135.1Vpeak at20kHz|Approximately130.278Vpeak; gain error−0.2815dB; modeled THD≈0.00402%|
|150Vpeak at1kHz|Approximately−0.00101dB; smallest output-to-moving-rail margin8.109V|

Gain error is relative to the source multiplied by nominal gain **after** the declared1k input/1M input and1k output/340k load losses. It is not a claim that135.1V requested becomes135.1V delivered. The source is1.351Vpeak for the135.1V test. The135V value came from a deep-overload fixture; it is not the amp's required clean RETURN level.

Halving the maximum timestep changes20kHz port amplitude by at most0.00787% and modeled THD by0.00000179percentage points. Adding read-only rail-output probes leaves original50Ω case metrics unchanged within1e−9 absolute numeric units. Worst retained-window settling difference is0.000261%. The50Ω parts carry at most5.329mA peak and0.836mW average in the measured steady-state windows, using time-weighted integration. These numbers exclude startup, faults and real component variation; they are not resistor-rating or thermal acceptance.

The108-check evidence audit passes, including six deliberate failing controls. The nominal fixture meets the existing proposed±0.5dB gain screen at the sampled frequencies and a conservative modeled-THD screen. It has **not** swept the complete20Hz–20kHz band, measured noise or qualified the complete amp. The four native board hashes are unchanged.

## Cost, sourcing and alternative route

The OPA462IDDAR has a specific Chinese listing, [LCSC C1855811](https://item.szlcsc.com/1946624.html). The public page retrieved on24November establishes identity/package, but does not expose a dependable own-item quantity-one stock/price or Shanghai delivery quote. A related-item/search price is insufficient evidence. Do not add three of these ICs, sockets/adapters and extra rails to the selected BOM based on this experiment.

A lower-parts-count discrete candidate remains worth evaluating. [Tube-Town's FX-Loop150 RevD manual](https://media.tubetown.net/info/datenblaetter/kits/kit-fxloop150-RevD-EN.pdf) documents a two-LND150 approach with250–400V supply, but its stated port limits do not prove recovery of this135Vpeak test. [Microchip's LND150 datasheet](https://www.microchip.com/content/dam/mchp/documents/OTH/ProductDocuments/DataSheets/LND150-LND250-N-Channel-Depletion-Mode-DMOS-FETs-Data-Sheet-20005454A.pdf) is the device basis; threshold/current spread, load capacitance and thermal limits require explicit treatment. A verified manufacturer SPICE model was not retrieved in this pass.

[LCSC LND150N3-G-P003/C629120](https://item.szlcsc.com/658919.html) is an exact Chinese sourcing lead; the accessible listing lacks sufficient current stock/MOQ/delivery evidence. The plainN3-G is a different order code. Neither imported-board examples nor distributor search snippets establish an affordable Shanghai-deliverable implementation. No substitute is adopted.

## Decision and next action

Keep50Ω rail isolation as a reproducible working **simulation reference**, outside native CAD/BOM. It resolves numerical completion for this alternative fixture, not T05. Do not remove the bypass capacitor. The more expensive bootstrap circuit still lacks real supply design, startup/shutdown and fault protection, thermal/socket qualification, exact purchasing and integrated dry/spring/wet behavior.

Next derive the necessary clean/overload recovery and source-impedance envelope with the current loaded-output model; compare a costed discrete candidate at the **same** insertion point. The earlier−2.26/−6.88dB wet-mix changes from a low-impedance return remain unresolved. A topology change cannot silently bypass that requirement. Preserve the three-board block plan, independent rear removal and current46mm chuck record; full tool clearance still needs body/bit geometry.

Reproduce using KiCad's bundled Python (with NumPy): run the causal factory, then the isolated-rail factory, then the audit. Fetch the checksum-pinned model using `return_driver.py --fetch` if absent. The causal matrix was rerun after adding the compatible refinement/probe seam and stale-log cleanup; both summaries pin the final measurement source. Exact emitted decks are checked independently. A rerun replaces that case’s previous products rather than accumulating old copies.
