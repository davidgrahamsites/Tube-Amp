---
id: VAL-042
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Expression wet gain-cell screen

[Review](../../engineering/whole-amp/expression-control/ota-review.md) owns the standalone nominal TI LM13700/OPAx134 experiment. Twenty-nine cases: 28 complete, one ±12V transient timeout. Nine ±15V audio cases cover 0.1/1/10Vpeak and 100/1000/10000Hz; maximum sampled THD0.05628%. Halved-timestep amplitude changes0.003565%. The81-check evidence audit passes and verifies unchanged native boards.

Untrimmed gain control moves nominal output DC by1.22185V. A calibrated resistor trim reduces sampled bias-dependent spread to3.181mV, but temperature-dependent residuals, actual current sources, noise, smoothing and hot-plug faults remain. An invalid initial solver-fallback/secant calibration is retained as rejected evidence, not a hardware conclusion.

Exact TI SOIC LM13700M/NOPB has a Chinese LCSC listing reporting83stock/MOQ1 and displayedCNY4.20 (quantity tier not confirmed). Obsolete TI DIP listing reports zero stock. A socketed carrier remains required; no component adoption or native change. Complete Shanghai purchasing evidence, circuitry, integrated qualification and all six build scopes remain open.
