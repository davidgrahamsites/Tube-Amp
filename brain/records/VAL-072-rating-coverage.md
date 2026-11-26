---
id: VAL-072
type: validation
domain: components
status: verified
updated: 2026-11-25
---
# Rating inventory and missing BOM references

[Review](../../engineering/component-selection/rating-coverage/review.md) reconciles the already-integrated R304/R314 into P133 and the selected-parts BOM, with exact RT0603 identity and dated Chinese supplier evidence. All240 physical source references are accounted for; this is not all-part qualification. The BOM factory now rejects omissions, duplicate coverage and explicit source/MPN disagreement. Three negative controls pass.

The manufacturer-backed bounded R304/R314 screen is2.8125mW each versus64.706mW allowed at assumed100°C. No circuit, native layout or footprint changed. Their thermal/power-sequence/fault limits and purchasing quantity/price remain explicit. The worksheet assigns applicable stress checks to every reference, including voltage/ripple for capacitors and current/VA/heat for magnetics. Complete operating/fault evidence and populated three-board fit remain open; objective6 is not complete.

The staged-source check additionally caught C605’s stale candidate-only record and a nonexistent working evidence pointer. Reconciled P093 with the already-adopted exact100V C0G source/native identity; prior manufacturer dossier and local-loop adoption remain linked. All native files are unchanged. No new circuit selection or fresh Chinese stock claim.
