---
id: VAL-004
type: validation
domain: schematic
status: verified
updated: 2026-10-04
---
# Bundled ngspice scripted solver qualification

## Claim and revision
KiCad's installed shared ngspice 45.2 can be driven from its native arm64 Python for the tested DC and transient analyses, returning real numerical vectors. This is software/interface qualification, not selected-component amplifier simulation.

## Method
Followed the [official shared-library interface](https://ngspice.sourceforge.io/shared.html) and its `sharedspice.h` vector/callback definitions. Used KiCad Python 3.9 and `/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib`. Reproducible command from the workspace:

```sh
'/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3' simulation/tools/qualify_ngspice.py
```

Compared a 5 V equal-resistor divider with analytic 2.5 V, then a 1k/1uF RC step with `5*(1-exp(-t/0.001))`. These deliberately simple analytic circuits contain no amplifier model.

## Actual result
Run completed with exit code 0. DC output 2.5 V, tolerance 1e-6 V. Transient returned 529 samples; at 0.0010032120579622765 s, output was 3.166514988368747 V versus analytic 3.166501565913611 V, within the declared 0.01 V tolerance. Engine output identifies ngspice-45.2. No solver error was reported in the retained log.

## Evidence
[Qualification script](../../simulation/tools/qualify_ngspice.py), [result JSON](../../simulation/qualification/result.json), [engine log](../../simulation/qualification/ngspice.log), [DC netlist](../../simulation/qualification/dc-divider.cir) and [RC netlist](../../simulation/qualification/rc-step.cir). Result JSON records exact runtime, library and netlist hashes.

## Scope and follow-up
No actual build part has been selected or simulated here. AC/noise, tube nonlinear models, transformer behavior, digital code models and the integrated amplifier require their own qualification/runs. Proceed through the [selected-component simulation contract](../../simulation/requirements.md); do not treat these tool tests as a design pass.
