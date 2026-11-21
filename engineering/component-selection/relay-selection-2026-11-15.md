# Signal relay selection — 2026-11-15

Task: qualify existing relay candidate for K1/K2/K3; owner relay_pick agent. Inputs: v0.5 board-plan.json, P029/P097 coverage, existing domestic supplier record. Output: exact engineering choice and remaining checks. No native CAD or shared register changes. Time-boxed manufacturer/source and connectivity inspection; no bench test.

## Engineering choice

Select **Omron G5V-2-H1 DC12**, supplier C128021, for **P029 (K1,K2)** and **P097 (K3)**, conditional on the checks below. Do not substitute the ordinary G5V-2 DC12: its coil load differs. Three fitted parts. Domestic evidence retained from November11: MOQ1, RMB10.65 each, stock11K+; total RMB31.95. Not revalidated as live November15 stock. Source: https://item.szlcsc.com/139304.html . Current indexed LCSC product confirms the exact ordering string: https://www.lcsc.com/product-detail/C128021.html .

## Manufacturer evidence

Primary legacy datasheet successfully read November15:
https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v2.pdf
(K046-E1-03, four pages). Newer primary indexing independently agrees on12V/12.5mA/960ohm/150mW:
https://components.omron.com/system/files/2025-01/datasheet_pdf/CDPA-032.pdf

Conservative legacy H1 limits: sealed DPDT, bifurcated Ag/Au contacts; coil960ohm±10% at23°C,150mW nominal. Pickup≤9V, release threshold≥0.6V at23°C. Contacts1A24VDC rated;125VDC maximum switching voltage is not a1A-at125V rating. Initial contact resistance≤100milliohm. Operating ambient−25..70°C. Envelope20.5×10.1×11.5mm maximum; eight1mm recommended holes. Terminal drawing is bottom-view, positions1/16 coil and4/6/8,13/11/9 contact groups. Manufacturer warns low-level reliability is application-dependent. Maximum coil overvoltage is not permission for continuous overdrive.

## Circuit review and arithmetic

Existing board-plan connects K1/K2 to the12V rail and common COIL_CH low-side Q1 driver; K3 to COIL_REV/Q2. Both driver nodes have1N4007 flyback diodes, cathode at12V. Their signals are input/grid/channel-output selection and wet mute; no contact is intentionally connected to mains or B+.

At nominal12V: one coil12.5mA, two channel coils25mA, all three37.5mA/0.45W. At−10% resistance and12V: one13.889mA, channel pair27.778mA, total41.667mA/0.50W. These are arithmetic load estimates, not hot-driver or regulator qualification.

This part's sealed low-signal contact construction and small coil load make it an appropriate engineering selection for these three positions. No claim of audible superiority or measured switching life.

## Open checks before release

- Verify exact manufacturer bottom-view contact state against symbol and native footprint pad numbers; text extraction alone does not complete graphical pin-map review. Recheck1mm drills, courtyard and orientation on saved boards.
- Confirm voltage at each coil under low-line/hot regulator and driver losses exceeds hot pickup requirement; inspect the complete12V supply load and startup/reset behavior. The23°C9V threshold does not prove hot pickup.
- Bound actual channel-output contact voltage under clipping/startup and coupling-cap faults. Existing nominal signal simulations do not qualify all transient/fault conditions.
- Keep relay ambient below70°C. Check tube heat, sustained coil operation and actual board temperature.
- Bench-check silence, contact intermittency and switching pops at instrument-level currents; a low-level reference load is not guaranteed reliability for every dry circuit. Flyback diode slows release and must be included in switching test.
- Recheck current stock, price and manufacturer identity before purchasing. No order/release approved by this dossier.
