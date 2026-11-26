# Reverb clamp current and rail-injection correction — VAL-063

25 November 2026. Baseline eb17981. Candidate correction, not yet in native CAD.

R601 already limits input current; D601/D602 already clamp SEND_IN toward the
rails. [TI OPAx134 revision B](https://www.ti.com/lit/ds/symlink/opa2134.pdf),
page 5, allows at most 10 mA input current and requires current limiting for
signals exceeding a rail by 0.5 V. Its total supply absolute maximum is 36 V.
An ordinary silicon clamp is not guaranteed to hold within 0.5 V: the current
limit matters. [onsemi 1N4148TR evidence](../../../component-selection/lv-semiconductor-selection-2026-11-15.md)
owns the selected external diode limits; no redundant diode is proposed.

## Result and selected correction for integration

Add **10 kΩ from +15 V to GND and 10 kΩ from GND to −15 V**, proposed R619/R620,
using already selected Yageo **MF0207FTE52-10K**. These loads give rail-injected
current a defined sink without relying on a regulator's ability to absorb it
or an undocumented minimum op-amp current. They add nominal 1.5 mA and
22.5 mW per rail. At 18 V and −2% resistance, each dissipates 33.06 mW, versus
388.24 mW derated allowance at 100°C for the selected 0.6 W MF0207.

The first comparison considered only input injection. The output coupling
path through C607 also matters. A 47 kΩ rail load passes the limited transient
fixture but fails the broader combined-current allocation below. Therefore
10 kΩ is the candidate chosen for native integration; 47 kΩ is not adopted.

Native circuit, schematic, PCB, functional interfaces and sockets are unchanged
in this evidence pass. Integration must add the two parts, update the supply
load budget, verify the readable sheet, route the local returns, and rerun
native parity/ERC/DRC/drill checks before calling the correction implemented.

## Declared bounds and independent calculations

IN_AC is bounded to ±313 V as an engineering allocation inherited from the
available-plate screen. This is not a measured supply/overshoot limit or an
arbitrary external effects-source rating. With R601 at 980 kΩ, total input
current is at most **0.3194 mA**, below TI's 10 mA limit. R601/R602 are intact;
no bypassed/shorted-resistor fault is cleared by this calculation.

At a 15 V rail boundary, zero forward drop, R601 −2%, R602 +2%, the maximum
input-path rail injection is 157.02 µA after R602's shunt current. A separate
**0.6 mA output-path injection allocation** covers the tested C607 path with
margin: this allocation is conditional and must be verified against the final
coupling charge and system envelope. Combined injection is 757.02 µA.
The 10 kΩ load at +2% sinks 1.4706 mA, leaving **713.57 µA margin**. The 47 kΩ
load sinks only 312.89 µA and fails that combined allocation. `tools/analyze.py`
uses this pointwise current barrier; it does not assume minimum IC loading.

The 1 µF C607 charge cannot be dismissed because its normal audio voltage is
small. Conversely, a high DC terminal stress applied directly to IN_AC is a
bounding fixture, not a claim that healthy C601 passes sustained DC.
The separate 100 nF +20% / 313 V charge calculation gives at most 0.999 V rise
on an isolated 37.6 µF rail capacitor for that one charge transfer; it does not
bound repeated injection or the larger output capacitor.

R601's selected MF0207 part has 350 V working rating and sufficient conditional
power allowance for this screen, but its native metadata still says only
250 V minimum with no exact part. Correct that source/footprint identity during
integration; do not qualify an arbitrary 250 V resistor by these results.

## Simulation evidence and limitations

36 DC cases compare no load, 47 kΩ and 10 kΩ; positive/negative terminal drive;
powered source-only and unpowered rails; clamp thresholds 0, 0.5 and 1 V.
Independent finite-slope resistor reductions agree within 2.3e−10 V, and a
separate checker verifies input and both rail KCL residuals.

Twelve 12-second native-value transients include R7/C6/R43, C601/R601/R602,
R612/R24 and R616/C607/R617/R618. The plate source rises 0→313 V in 1 ms and
falls after five seconds. Healthy C6 and C6-short cases use powered/unpowered
rails. Two limiting cases repeat at half timestep. Resistors in the input
clamp branch use the stated extremes; other circuit values are nominal.

Clamps are piecewise behavioral current paths with 1 Ω forward slope, not
vendor semiconductor macro-models. The output path similarly tests a possible
rail-injection route without asserting an undocumented OPA2134 output-diode
characteristic. No IC quiescent load is credited. Regulators can supply current
but cannot sink it. Tube plate current, main-stage dynamic loading and actual
heater/supply sequencing are omitted. These deliberately explicit assumptions
must remain visible in any future functional-block datasheet.

Without rail loads, the C6-short/powered fixture reaches about **36.004 V total
rail span**; this is a screening failure, not a predicted real-unit failure.
With 10 kΩ loads the tested span stays below 30.001 V. Maximum modeled output
injection is about 0.232 mA, below the 0.6 mA allocation. Half-step rail-span
differences are below 1 mV. This does not qualify regulator stability, actual
reverse current, cold/hot diode behavior, ESD, arbitrary capacitor charge or
all supply corners.

## China source and next implementation

[Domestic LCSC C513672](https://item.szlcsc.com/528499.html) confirms exact
Yageo MF0207FTE52-10K identity. Existing dated 11 November signed-in evidence
records 6,250 stock, MOQ50, ¥0.1151 each; it is not relabeled a fresh quote.
The 25 November public search confirms identity but does not establish fresh
stock, RMB tier/MOQ or exact Shanghai checkout. Reusing the existing selected
part may fit within that order quantity; final procurement must verify it.
No purchase, contact or upload occurred.

Next: integrate R619/R620 and exact R601 metadata/footprint, re-evaluate the
power/load and shutdown model with the added rail loads, then set voltage
clearances and rebuild the ground pour. All six build scopes remain open.
