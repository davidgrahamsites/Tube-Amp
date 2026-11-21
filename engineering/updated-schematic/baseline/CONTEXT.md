# Original source baseline

One job: preserve a native capture of the original Renegade audio, power, switching and legacy relay-supply topology.

## Inputs
The three original embedded source images, as-printed BOM and intake notes in `sources/original-ppt/`.

## Process
Map tube halves by actual pins and assign explicit native references to unnamed controls/magnetics/selector. Retain source values and historical 115/120 V supplies; do not substitute the revision's values. Source capacitor ratings, LED scope and T3 12V-CT interpretation remain unresolved. Chassis/service terminal and supply flag symbols document interfaces; they are not additional source circuitry.

## Outputs
`Renegade_Source_Baseline.kicad_pro`, its root schematic and ten child sheets. The project-local symbol table references `../libraries/`.

## Human check
Reconcile source terminal/wiper/valve mappings and magnetic operating conditions before treating this as a qualified simulation baseline. It does not suit 220 V mains as captured.
