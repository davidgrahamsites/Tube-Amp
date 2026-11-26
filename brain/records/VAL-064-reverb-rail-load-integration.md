---
id: VAL-064
type: validation
domain: cross-domain
status: documented
updated: 2026-11-25
---
# Native reverb rail loads and supply regression

[Owned review](../../engineering/whole-amp/reverb-600/rail-load-integration/review.md) adopts R619/R620 10 kΩ local rail loads and synchronizes R601's exact MF0207 1 MΩ/350 V package without changing the audio path. Four new round plated 0.8 mm holes; all 138 previous hits and 411 prior tracks preserved. Explicit native delta, logical ground-bond negative control, source parity and rendered review pass. Reverb DRC/opens remain zero under existing rules; one pre-existing ERC finding remains. No voltage-spacing or ground-pour approval.

Source-bound maximum added current is 1.836735 mA per rail. Updated 72-case supply screen and four refinements complete, retaining 44 engineering-flagged cases. Separate 32-case candidate brownout screen plus a half-step repeat retain 0.38320 ms minimum conditional timing reserve and 150.324 mV healthy-enable margin; actual contact timing and complete power sequencing remain unqualified. Candidate protection is not adopted.

Exact Yageo Chinese listing is verified; historical stock/MOQ are not refreshed and Shanghai checkout is open. Next voltage-specific spacing/connectors and plane rules, then remaining electrical integration/routing and populated three-board fit. All six scopes remain incomplete. No purchase, supplier contact or fabrication release.
