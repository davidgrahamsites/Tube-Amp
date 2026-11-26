# Packaging arithmetic workbook
Owner: integration. One job: make the conditional power-packaging arithmetic reproducible and link it to decisions.

## Inputs
inputs.json contains source-linked nominal inputs and hypothetical sensitivities. Canonical capacitor geometry calculations remain in engineering/component-selection/power-film; do not duplicate its package ownership here.

## Process
Run python3 tools/calculate.py from any directory. This is arithmetic only, not simulation, actual maximum-load qualification or a measured result. Sources are current circuit, JJ reference tubes and the dated harness research. Mark every hypothetical value explicitly.

## Outputs
results/arithmetic.json contains formula, substitutions, units, result, source input hashes and limits. Human explanations live in docs/design-journal/calculations/current-power-packaging.md.

## Human check
Recompute one heater-drop and one discharge/energy result by hand. Confirm that neither hypothetical400V nor example drop budgets became accepted limits or actual rail measurements. Existing heater topology is unqualified.
