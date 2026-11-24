# Revision factories
Inputs: circuit.json, preserved v0.5 native sheets and v0.4 connectivity/model/router.
Process: build_revision.py captures changed sheets in a new directory; simulate.py evaluates the electrical interface; check_native.py compares native pins with the contract.
Outputs: sibling cad, simulation and review products. Never overwrite earlier native projects.
Human check: review circuit.json and changed wire paths before accepting generated CAD.

Electric-input audit: check_electric_input.py accepts a fresh KiCad XML netlist path, checks the original input connections/values and writes review/electric-input-loading-2026-11-21.json. It owns no circuit changes and does not simulate pickup frequency response or tube overload.

Grounding audit: run `check_grounding.py` before `check_native.py`. It exports current `../review/grounding-native.xml`, proves the explicit GB1 bridge using a temporary native cut and emits `grounding-audit.json`. `grounding_contract.py` is the small shared read-only validation seam: a changed circuit/schematic/contract/XML invalidates the proof. Native checker accepts `--netlist` but requires the matching proven XML. The PCB hole/pad audit also uses this seam. Physical earth wiring is outside the automated proof.
