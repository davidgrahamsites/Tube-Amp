---
id: VAL-063
type: validation
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Reverb clamp current and rail-load correction candidate

[Owned review](../../engineering/whole-amp/reverb-600/input-clamps/review.md)
checks existing input clamps plus the output coupling injection path. The
conditional input-current bound is 0.3194 mA; the combined rail-current
allocation selects 10 kΩ per rail for integration, reusing sourced Yageo
MF0207FTE52-10K. Adds nominal 1.5 mA/22.5 mW per rail. A 47 kΩ alternative
fails the combined allocation despite passing the limited transient fixture.

36 DC cases, 12 native-value transients and two half-step refinements complete.
Independent DC reduction/KCL checks pass. The no-load C6-short screen reaches
about 36.004 V total; the selected candidate stays below 30.001 V in tested cases.
Ideal clamp/source-only regulator/no-IC-load assumptions are explicit; this
is not a physical OPA2134 fault prediction or full rail qualification.

No native circuit/PCB change in this pass. Next integrate R619/R620, synchronize
R601's exact 350 V selected part, update supply/shutdown loading, then qualify
spacing and ground pour. Shanghai checkout, actual magnetic components and
populated fit remain open. DEC-018 requires these assumptions and evidence
limits to flow into final reusable functional-block datasheets.
