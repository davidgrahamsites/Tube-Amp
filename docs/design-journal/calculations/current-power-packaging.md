# Current power-packaging calculations

**Checkpoint:** 26 November 2026; FB-143–148 and completed combined packaging synthesis

**Purpose:** readable derivations attached to the [capacitor packaging chapter](../chapters/capacitor-bank-and-driver-access.md) and [lower-power chapter](../chapters/bottom-power-packaging.md). These are not new component selections, limits, or architecture adoption.

## 1. Minimum lead protrusion and raised-body shortfall

**Choice informed:** whether the candidate film capacitors can be raised above nearby parts using only their leads.

**Inputs and sources:** Panasonic EZPV60506MTC exposed lead length is 4 ± 2 mm; CRC FC6136 is 4 ± 1 mm. Current boards are nominally 1.6 mm thick. Values and conditional geometry are in the [assembly arithmetic receipt](../../../engineering/component-selection/power-film/results/assembly-options.json), derived from the [mounting research](../../../plans/capacitor-bank-fit/mounting-research.md). Both candidate parts remain unselected.

**Symbols and equations:**

- $L_{min}$: minimum exposed lead length, mm.
- $t_{PCB}$: nominal PCB thickness, mm.
- `h`: trial body lift above its seated position, mm.
- $p=L_{min}-t_{PCB}$: lead remaining below a seated board, mm.
- $s=L_{min}-t_{PCB}-h$: lead shortfall below the board after the trial lift, mm. A negative `s` means the lead does not reach the board underside.

**Substitution and result:**

- Panasonic: $L_{min}=4-2=2$ mm. $p=2-1.6=0.4$ mm. At $h=3$ mm, $s=2-1.6-3=-2.6$ mm, a 2.6 mm reach shortfall.
- CRC: $L_{min}=4-1=3$ mm. $p=3-1.6=1.4$ mm. At $h=3$ mm, $s=3-1.6-3=-1.6$ mm, a 1.6 mm reach shortfall.

**Validation and scope:** These match the assembly-options receipt. They omit PCB thickness tolerance, solder protrusion, lead/body positional tolerance, bending limits, and a support structure. They show why the stated 3 mm raised-body idea is not supported by these minimum lead lengths; they do not reject a purpose-designed supported assembly.

**Linked choice:** do not suspend or elevate these bodies on short leads alone. The dedicated power-PCB capacitor area is the preferred starting layout; a structurally supported bank remains conditional and unapproved.

## 2. Maximum bodies and conditional array orientation

**Choice informed:** compare local capacitor body envelopes before modeling the complete cassette.

**Inputs and sources:** Panasonic maximum body $L×W×H=58×26×41$ mm; CRC $58.5×36×51$ mm. Nominal PCB thickness $t=1.6$ mm. Panasonic has a manufacturer 10 mm neighbor-heating recommendation; the same 10 mm used for CRC is only a comparison assumption. [Assembly-options receipt](../../../engineering/component-selection/power-film/results/assembly-options.json) and [geometry research](../../../plans/capacitor-bank-fit/geometry-research.md) contain the source bounds.

**Symbols and equations:**

- `L,W,H`: maximum capacitor body length, width, and height, mm.
- `g`: assumed edge gap between adjacent bodies, mm.
- `t`: nominal PCB thickness, mm.
- For a 2×2 body array, planar extent is $(2*L+g) by (2*W+g)$.
- For a compact row repeated across the short body axis, planar extent is $(4*W+3*g) by L$.
- Horizontal board plus body height is `H+t`. Standing the board vertically swaps that stack into the depth/height axes; it does not reduce body dimensions or account for support.

**Substitution and result, Panasonic, $g=10$ mm:**

- 2×2 horizontal: $(2\times58+10)\times(2\times26+10)\times(41+1.6)=126\times62\times42.6\,\mathrm{mm}$.
- 2×2 vertical: $126\times(41+1.6)\times62=126\times42.6\times62\,\mathrm{mm}$. Local depth saving: $62-42.6=19.4$ mm; height increases by the same 19.4 mm.
- Short-axis row horizontal: $(4\times26+3\times10)\times58\times(41+1.6)=134\times58\times42.6\,\mathrm{mm}$.
- Short-axis row vertical: $134\times42.6\times58\,\mathrm{mm}$; local depth saving: $58-42.6=15.4$ mm.

**Substitution and result, CRC, $g=10$ mm comparison assumption:**

- 2×2 horizontal: $(2\times58.5+10)\times(2\times36+10)\times(51+1.6)=127\times82\times52.6\,\mathrm{mm}$.
- 2×2 vertical: $127\times52.6\times82\,\mathrm{mm}$. The depth/height trade is 29.4 mm.

**Validation and scope:** Panasonic and CRC values agree with the machine-readable assembly-options receipt. The gaps do not represent high-voltage clearance. Dimensions exclude board margins, underside solder, support, retention, contacts, insulation, connectors, underlying parts, wires, removal paths, cooling, cabinet and thermal fit. These are local candidate array extents, not finished PCB outlines or usable cabinet volume. No exact capacitor is adopted.

**Linked choice:** compare a compact 2×2 and short-axis row on the revised power PCB first; consider a supported vertical or upper bank only if whole-cassette comparison shows a real advantage.

## 3. Existing whole-carrier diagnostic overruns

**Choice informed:** moving capacitors cannot be treated as a solution to all current board/cassette geometry deficits.

**Inputs and sources:** current board outlines and provisional diagnostic assembly allowances are in [geometry research](../../../plans/capacitor-bank-fit/geometry-research.md). The comparison frame is 467 mm wide × 160 mm deep, not a verified usable cabinet rectangle. Diagnostic allowances are 10 mm construction edge each side, 15 mm side-flange each side, and an 8 mm inter-board gap.

**Symbols and equations:**

- $W_A,D_A$: assembly width and depth, mm.
- Width for a side-by-side tier is board widths plus 8 mm inter-board gap, 20 mm total construction-edge allowance, and 30 mm total side-flange allowance.
- Depth is the largest board depth plus 20 mm total construction-edge allowance.
- Overrun is `assembly-frame`; a negative width residual is not clearance approval.

**Substitution and result:**

- Main + Reverb: width $290+160+8+2×10+2×15=508$ mm; depth $max(140,100)+2×10=160$ mm. Against 467×160 mm: `+41` mm width, 0 mm depth.
- Rotated Power + Control: width $175+230+8+20+30=463$ mm; depth $max(160,110)+20=180$ mm. Residual: `-4` mm width, `+20` mm depth; the width residual is not usable clearance.
- Main + rotated Reverb: width $290+100+8+20+30=448$ mm; depth $max(140,160)+20=180$ mm. Residual: `-19` mm width, `+20` mm depth.

**Validation and scope:** The equations and inputs match the cited geometry research. This is an arithmetic screen using unqualified allowances and incomplete board geometry. It is not a shared-datum cabinet fit, loaded assembly model, or physical mock-up. Lowering power does not automatically remove Main/Reverb's width issue, nor establish that the Power PCB fits the reported floor depth.

**Linked choice:** the completed synthesis keeps upper K2 as a diagnostic reference and hybrid lower K1 as the first conditional comparison; neither is adopted or proven to fit.

## 4. Heater current and loop $IR$/$I^2R$ sensitivity

**Choice informed:** assess whether extra heater wiring could cause material voltage drop or dissipation before selecting a harness.

**Inputs and sources:** four JJ ECC83S heaters at nominal 0.3 A each, two JJ EL34 heaters at nominal 1.5 A each, 6.3 V heater supply, two 100 Ω midpoint resistors in series, and 0.15 A pilot allowance. The candidate tube ratings and inventory source are recorded in the [bottom harness research](../../../plans/bottom-power-enclosure/harness-research.md), [source circuit](../../../engineering/whole-amp/reverb-600/circuit.json), and [arithmetic receipt inputs](../../../plans/power-packaging-synthesis/calculations/inputs.json). These are nominal/example values, not exact purchased-tube data or a winding rating.

**Symbols and equations:**

- `N`: heater count, unitless.
- $I_h$: nominal heater current per tube, A.
- $V_h$: nominal heater voltage, V.
- $R_m$: sum of midpoint-resistor values, Ω.
- $I_p$: pilot allowance, A.
- $R_{loop}$: total hypothetical loop resistance including both conductors, contacts, and terminations, Ω.
- $I_{pre}=N_{pre}I_{pre,tube}$; $I_{out}=N_{out}I_{out,tube}$.
- $I_m=V_h/R_m$; $I_{total}=I_{pre}+I_{out}+I_m+I_p$.
- $V_{drop}=I R_{loop}$, V; $P_{loop}=I^2R_{loop}$, W.
- For an illustrative drop budget $V_b$, $R_{loop,max}=V_b/I_{total}$, Ω.

**Substitution and result:**

- Preamp: $4×0.3=1.2$ A. Output tubes: $2×1.5=3.0$ A.
- Midpoint: $6.3/200=0.0315$ A. Total inventory: $1.2+3.0+0.0315+0.15=4.3815$ A.
- At a hypothetical $R_{loop}=0.010$ Ω: $V_{drop}=4.3815×0.010=0.043815$ V; $P_{loop}=4.3815^2×0.010=0.1919754$ W, approximately 0.192 W.
- If heater groups were isolated, which is not adopted or yet qualified: preamp-only $1.2×0.010=0.012$ V and $1.2^2×0.010=0.0144$ W; output-only $3.0×0.010=0.030$ V and $3.0^2×0.010=0.090$ W.
- Illustrative total-loop resistance for 0.10 V drop: $0.10/4.3815=0.0228232$ Ω, approximately 22.82 mΩ. For 0.20 V: $0.20/4.3815=0.0456465$ Ω, approximately 45.65 mΩ.

**Validation and scope:** These values match the 16-case arithmetic receipt to rounding. The 0.10 V and 0.20 V values are examples, not approved drop budgets. The loop value is hypothetical; no wire, route, or connector is selected. The total excludes cold-start surge and tolerances. The existing shared heater reference fails HD-002 in 14 of 38 modeled cases, and isolated winding/group allocation is not approved; this calculation does not solve heater-to-cathode limits, insulation, or startup behavior.

**Linked choice:** the synthesis keeps heater and reference allocation as an adoption blocker. Do not freeze winding count, connector, wire gauge, or claim a safe voltage drop from this sensitivity alone.

## 5. Nominal reservoir series capacitance and isolated $RC$ time constant

**Choice informed:** show the scale of the raw reservoir's nominal series capacitance and its simple resistor-capacitor time constant without calling that the system discharge time.

**Inputs and sources:** C29 and C30 are each 220 µF and rated 350 V each in the current circuit contract; R501 and R502 are each 220 kΩ, with the source listing 2 W and a 350 V working minimum. Their endpoints put each resistor across a capacitor section. See the [circuit](../../../engineering/whole-amp/reverb-600/circuit.json), [interface/discharge research](../../../plans/capacitor-bank-fit/interface-research.md), and [receipt](../../../plans/power-packaging-synthesis/calculations/inputs.json).

**Symbols and equations:**

- $C_1,C_2$: nominal section capacitances, F.
- $C_{eq}$: ideal series capacitance, F; $1/C_{eq}=1/C_1+1/C_2$.
- $R_b,C_b$: one section's nominal bleeder resistance and capacitance.
- τ: ideal single-pole time constant, s; $\tau=R_bC_b$.

**Substitution and result:**

- Two equal 220 µF sections in series: $C_{eq}=220/2=110$ µF.
- Each isolated section: $\tau=220{,}000\times220\times10^{-6}=48.4\,\mathrm{s}$.
- The ideal complete equal series pair can also be represented as 440 kΩ across 110 µF: $\tau=440{,}000\times110\times10^{-6}=48.4\,\mathrm{s}$.

The two nominal stage-filter RC estimates are also simple one-pole examples: R17/C12 gives $10{,}000\times50\times10^{-6}=0.5\,\mathrm{s}$; R35 with C13 and C25 treated as an ideal 100 µF parallel total at their shared B_PRE node gives $10{,}000\times100\times10^{-6}=1.0\,\mathrm{s}$. C13 and C25 remain distinct 50 µF references with deliberate physical returns. These RC values ignore source impedance, L1, tube loading, wiring, and the full network; they are not ripple or startup qualification.

**Validation and scope:** The 110 µF and 48.4 s values match the receipt's `series_reservoir` and `isolated_bleeder_tau` results. This idealized branch model excludes standby switching, tube loads, tolerance, leakage, transformer and rectifier behavior, other filter capacitors and connector states. A time constant is not a safe service delay or residual-voltage criterion; the synthesis requires full-network state analysis and hardware verification.

**Linked choice:** keep the raw reservoir, bleeders, CT return, downstream filters, and both module halves explicit in the service/interface plan. No added bleeder or discharge claim is adopted.

## 6. Illustrative stored energy

**Choice informed:** show why a disconnected high-voltage capacitor bank needs explicit charge-state and service planning.

**Inputs and sources:** 50 µF film capacitor value from the [current circuit](../../../engineering/whole-amp/reverb-600/circuit.json); 110 µF nominal series raw reservoir from the previous calculation. The machine-readable receipt sets 400 V as an illustrative voltage only.

**Symbols and equation:**

- `C`: capacitance, F.
- `V`: assumed capacitor voltage, V.
- `E`: stored energy, joule (J); $E=\frac{1}{2}CV^2$.

**Substitution and result:**

- One 50 µF film capacitor at an illustrative 400 V: $E=\frac{1}{2}\times50\times10^{-6}\times400^2=4.0\,\mathrm{J}$.
- An ideal 110 µF series raw-reservoir pair at an illustrative 400 V total: $E=\frac{1}{2}\times110\times10^{-6}\times400^2=8.8\,\mathrm{J}$.

**Validation and scope:** These results match the arithmetic receipt. The 400 V is not an operating-voltage claim, test instruction, or safe charge limit. Series-section voltage sharing is not proven equal under real tolerances/leakage, and real stored energy depends on actual voltage and capacitance. This example supplies no discharge time or permission to touch/unmate a bank.

**Linked choice:** account for charged, powered-off, standby-open, partially disconnected, and removed states on both power modules; define measured residual-voltage criteria and a safe discharge procedure before approving service.

## Calculation source receipt

The user requirement FB-148 asks that calculations and solutions be documented alongside the choices they inform; its canonical source is the [feedback ledger](../../../brain/feedback/events.json).

The parent-owned machine calculation package contains frozen nominal/hypothetical inputs, the calculation factory, and a 16-case result: [inputs](../../../plans/power-packaging-synthesis/calculations/inputs.json), [factory](../../../plans/power-packaging-synthesis/calculations/tools/calculate.py), [arithmetic result](../../../plans/power-packaging-synthesis/calculations/results/arithmetic.json). Its `design_qualified` field is false. The mechanical array and carrier equations are sourced to the manufacturer-based geometry inputs and result in [assembly-options.json](../../../engineering/component-selection/power-film/results/assembly-options.json) and [geometry research](../../../plans/capacitor-bank-fit/geometry-research.md); no physical fit is established.


## Vocabulary key

- **Lead protrusion:** lead length left below the PCB after the part is seated.
- **Series capacitors:** capacitors connected one after another. Their equivalent capacitance is lower than either capacitor alone.
- **Parallel capacitors:** capacitors connected across the same two nodes. Their nominal capacitances add, but the physical references and return paths may still need to stay separate.
- **RC time constant:** the ideal product of resistance and capacitance. It describes one simple decay model; it is not a safe waiting time for this amplifier.
- **Loop resistance:** resistance of both supply and return wires plus contacts and terminations.
- **Stored energy:** energy held in a charged capacitor. Actual energy depends on its actual capacitance and voltage.
- **Carrier overrun:** calculated assembly width or depth beyond a provisional comparison frame. A negative remainder is not proof of usable clearance.
- **Return path:** the conductor or circuit route that carries current back to its source. It is not automatically the chassis or protective earth.

## Source and choice links

FB-148 asks for calculations alongside the choices they support. See the [feedback ledger](../../../brain/feedback/events.json), [combined synthesis](../../../plans/power-packaging-synthesis/final.md), and the linked capacitor and lower-power journal chapters above. Earlier project calculations remain queued for backfill; this file does not claim full historical coverage.
