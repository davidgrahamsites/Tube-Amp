# Panel connector integration

Owner: electrical/PCB integration. One job: translate the ten external panel-pot interfaces into removable PCB connector requirements without changing the circuit.

Inputs: `../reverb-600/circuit.json`, current `../pcb-measured-r/boards/`, and manufacturer limits in `connector-contract.json`. The earlier proposal in `../../panel-harness/` supplies candidate identities, not verified wiring geometry. Public interface: `results/pot-connectors.csv` and `results/checks.json`.

`wire-candidates.json` owns dated supplier observations and published wire dimensions. The factory derives full-tolerance contact/tool compatibility from those inputs. A compatible diameter is not wire selection, crimp qualification or a stock/delivery confirmation.

Process: run `tools/check_panel_interfaces.py` with KiCad's Python. Read all native boards without saving; derive every terminal net from the circuit, compare existing PCB endpoints and audit the installed candidate footprint against nominal drawing dimensions. Report missing board nodes and hold connector adoption until voltage, full drawing/physical numbering, wire, supplier and populated fit evidence is complete. Never delete all JM wire pads: they also serve tubes, supplies and other interfaces.

Outputs: generated pinout/migration schedule and checks, plus `review.md` explaining constraints. The contract owns connector and crimp requirements; the circuit owns pot nets; mechanical owns final position, cable length and access.

Human check: compare exact purchased parts and crimped samples to manufacturer drawings; continuity-test each numbered cavity against the pot terminals with power disconnected. Confirm CW operation, latch/extraction access and independent rear removal in the populated cabinet. None is passed by this audit.

Task HI-001: prerequisite for T09/T10; medium scope. Done for this bounded audit means ten complete derived interfaces, native endpoint evidence, nominal drill comparison, and negative controls. Manufacturing readiness remains a separate gate.

Task HI-003 (one engineering pass): `tools/cable_loading.py` reuses the source-derived effects-loop fixture to screen RV1–RV8 harness capacitance at FX_SEND. Circuit/model/factory/board hashes identify inputs; `results/cable-loading.json` is the public numerical seam and `cable-loading-review.md` interprets it. The connector mapping stays owned by HI-001. Done means matched unloaded/loaded cases, independent RC and topology controls, frequency-grid refinement, and explicit placement implications. Actual cable capacitance, independent pot-setting corners, RV9/RV602, fault insulation and physical fit remain separate evidence. Human check: compare a measured cable matrix and populated assembly against this experiment before freezing lengths.

Task HI-004: `mating-geometry.json` owns candidate connector datums and nominal assembled bounds; `tools/check_mating_geometry.py` checks the installed footprint and writes `results/mating-geometry-checks.json` and SVG. Read `mating-review.html`. Sources remain in `evidence/`. The edge rule is necessary only; current drawing revision, tolerances, cable bends and extraction remain open. No native placement or service clearance is approved. Mechanical must consume this seam rather than infer mated space from the header courtyard.

Task HI-005: `wire-dressing.json` owns the sourced relaxed-wire rule and the explicit straight-exit planning assumption; `tools/check_wire_dressing.py` consumes HI-004 geometry and the pot interface contract to generate `results/wire-dressing-checks.json` and SVG. Mechanical consumes the per-interface axial reserve; it does not copy connector dimensions. Empty placements, unknown bend/withdrawal geometry and unqualified wire cannot become fit approval. Read `wire-dressing-review.html`; confirm contact freedom and service access on actual parts.

Task HI-006: `voltage-screen.json` owns the declared DC coupling-fault experiment. `tools/check_pot_voltage.py` reads current circuit values/endpoints, solves normalized passive networks and generates JSON, CSV and `pot-voltage-review.html`. Keep sampled results distinct from actual maxima; no connector, pot or insulation approval follows. Human check: confirm exact part DC/track/wiper limits and source bounds before native adoption.

HI-006 loaded follow-up: run `tools/pot_fault_probe.py` with KiCad Python after the linear screen. It reuses the generic tube/supply/buffer factory for 12 bounded DC solves, retains paired results and one example deck, then refreshes the HTML. Fixed supply and sampled settings do not qualify exact parts or protection.

HI-007 source follow-up: `evidence/pot-rating-source-review.html` records the exact B25K-3LA rating conflict and excludes unmatched historical/shaft variants from qualification. It consumes HI-006 numerical evidence without rerunning or changing it.
