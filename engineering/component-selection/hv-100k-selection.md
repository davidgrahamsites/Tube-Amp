# Selected HV 100 kΩ resistors

2026-11-12. Select **Yageo FMP200JR-52-100K** for R4,R5,R7,R12,R15,R21,R22,R30,R31 (nine fitted). Preserve 100k resistance; 5% tolerance is this exact part's specification. Do not use it to replace the 1% low-voltage summing/feedback resistors.

Domestic supplier evidence retained November11: LCSC C3456483, ten-piece minimum, ¥0.2739 each, ¥2.739 pack,1190 recorded stock. The November12 web fetch did not expose a current cart/stock quote; these remain dated observations, not refreshed availability. Exact supplier URL is in candidate-register.json.

Manufacturer evidence: `evidence/Yageo-FMP.pdf` and text. FMP200:2W at70°C, linearly derated to zero at155°C;500V maximum working voltage further constrained by sqrt(P×R). Body9±0.5mm ×3.9±0.3mm;lead0.55±0.05mm. Flameproof coating does not establish circuit fault protection.

`select_hv_100k.py` and `hv-100k-rating-screen.json` cover27 nominal DC checks (nine references at70/100/125°C). Maximum utilization44.04% of derated power occurs at R22 at125°C. These temperatures are hypothetical local ambient values, not measurements. The400V stiff-supply/generic-tube fixture is the only operating condition checked here. High-line, audio transient, short-circuit, tolerance and real thermal evidence remain unresolved.

Selected-part footprint: `footprints/Renegade_Selected.pretty/Yageo_FMP200_L9.0_D3.9_P15.24.kicad_mod`,15.24mm formed pitch,0.8mm drill for0.6mm maximum leads,4.7mm courtyard height for4.2mm maximum body diameter. Native KiCad10.0.6 reload/pad checks and SVG export passed; SVG visually reviewed November12. No unsupported3D model included. Provide lead bends outside the body and thermal standoff in assembly review. Native PCB integration has not yet occurred; no old placement generator was rerun.
