# Component rating and coverage audit
Owner: component selection. One job: reconcile every physical source reference with its purchasing/rating record and expose unqualified stress requirements.
Inputs: ../coverage.json, ../candidate-register.json, ../../whole-amp/reverb-600/circuit.json, rating-rules.json and the retained RT datasheet/VAL-056 input-current screen.
Process: tools/audit.py calls the canonical coverage validator, emits a per-part worksheet and evaluates the bounded R304/R314 thermal screen. It does not simulate other parts or infer qualification from a selected MPN.
Outputs: results/parts.csv, results/checks.json and review.md. Circuit and native geometry remain owned by their existing modules.
Human check: trace a resistor and capacitor from the worksheet to an exact datasheet, actual operating corner and physical package. Missing evidence is a release gate; a populated row does not mean qualified.
