---
id: VAL-062
type: validation
domain: cross-domain
status: documented
updated: 2026-11-25
---
# C607 coupling capacitor voltage and footprint repair

[Owned review](../../engineering/component-selection/reverb-coupling/review.md)
integrates exact KNSCHA MPP105J2W10KN22605, 1 µF/450 V, in place of C607's
63 V part following VAL-061's conditional fault screen. P130 owns the new
selection; C606 retains P094. Exact manufacturer maximum-body/pitch/round-lead
dimensions drive a new selected-library footprint, two 1 mm finished holes,
and two local 45-degree pad escapes. ICKey China lists minimum one, ¥0.7282 at
the one-piece tier and mainland delivery; Shanghai address checkout is open.

Independent checks preserve 144 nets, 236 component identities and 18 schematic
page rasters. One existing ERC finding is unchanged. Reverb DRC is zero with
zero unrouted connections under the existing rules. Excellon comparison finds
only the two intended changed holes; 136 other drill hits are unchanged.
Other board objects are preserved. No plane is adopted or voltage-spacing
qualification claimed. Hand-forming, fabricator tolerance, thermal/chassis
height and complete fault qualification remain open.

Next: existing D601/D602 clamp current and rail injection, including unpowered
operation, then net-specific clearance and ground pour. Missing candidate rows for previously selected AO3400A and MFR0W4F8200A50
were restored with exact identities and unknown domestic price/MOQ marked null;
selected-BOM generation now succeeds while retaining procurement holds. All six
build scopes remain incomplete. No purchase or fabrication release.
