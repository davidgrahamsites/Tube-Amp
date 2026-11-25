# Control reset and relay switching
Owner: Renegade integration. One job: qualify the reset-to-relay electrical interface.

Inputs: ../reverb-600/circuit.json, native latch sheet and Control/Main/Reverb boards; exact manufacturer data and dated supplier observations in review.md. Baseline a9fd3fb5e12f23d84b21dd751f16ec957ed9e62e.
Process: contract.json owns candidate limits. tools calculates corners and simulates bounded cases through ../tools/spice_runtime.py. models retains unmodified manufacturer models separately from generated decks/results. Native adoption requires a separate preservation/netlist/ERC/DRC and visual gate. No factory silently regenerates other modules.
Outputs/public seam: review.md, contract.json and results/*.json. Candidate supervisor and native driver status are explicit. Socket hardware belongs to ../../component-selection/socketing; these checks do not qualify that interface.
Human check: measure reset startup/brownout, HC74 outputs, driver drain transients and relay pickup/release on the assembled harness at actual temperatures. Check every IC/tube is removable and the installed socket carrier pin mapping matches its drawing.

Current reset-edge seam: edge-contract.json and edge-routes.json define the bounded repair; edge-review.md and results/edge-native-checks.json supersede earlier native hashes only for this declared change. analyze_reset_edges.py diagnoses the unchanged vendor-model limitation.

Brownout screen: brownout-contract.json owns the matrix; brownout-review.md records limits. check_brownout_limits.py, simulate_brownout_matrix.py and refine_brownout_matrix.py keep qualification false when completed nominal models cannot prove hardware corners.

Divider comparison: divider-contract.json is a separate candidate interface; tools/check_divider_options.py writes results/divider-options.json. divider-review.md retains manufacturer/supplier observations and explicit failed extended screens. It does not overwrite the historical simulation contract or select a native part.

Analog-rail inhibit candidate: rail-monitor-contract.json defines the proposed two-comparator sense/feedback network and REV_GATE interface; rail-monitor-review.md interprets tools/rail_monitor_budget.py endpoint results. It is not native. Only the earlier K3 final-contact repair is adopted (VAL-046).

Buffered rail candidate: rail-monitor-buffered-contract.json owns the reduced-impedance network and spare-U1E interface. rail-monitor-buffered-review.md separates conditional static success from unresolved sourcing/timing/native adoption. Original rail-monitor-contract.json now uses corrected full-temperature comparator limits.

Delay candidate: rail-delay-contract.json extends that candidate with spare-U1F and a direct fault path. rail-delay-review.md owns the interpretation, including a failed brief-fault hold screen. The interface is still candidate-only; hot-component and full driver/contact response are not qualified.

Coil-latency seam: relay-latency-contract.json and relay-latency-review.md distinguish coil-current decay from contact response. The delay factory guards native R341=1k in source/schematic/board;4.7k is still an unadopted requirement of the candidate.
