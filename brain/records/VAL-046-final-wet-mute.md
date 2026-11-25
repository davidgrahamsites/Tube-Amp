---
id: VAL-046
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Final wet mute and supply-sequencing holds

[Owned review](../../engineering/whole-amp/expression-control/final-mute-review.md) records the native K3 spare-contact repair: common13 to WET_AC, NC11 to GND, pin9 still unconnected. No extra component, footprint, mounting or block change. Fresh reverb DRC0/opens0, existing ERC1 unchanged; exact two-pin native delta and preserved geometry. 39/39 scoped evidence checks pass.

Eight expression-candidate rail diagnostics retain two incomplete solver failures and large excursions in completed fault cases. Startup is not qualified; automatic analog-rail fault inhibit remains unimplemented. The local mute acts only when K3 is deenergized. China listing C128021 reports stock and minimum buy1; Shanghai address-specific checkout remains unverified. All six project scopes remain active and manufacturing is held.

Follow-on [analog-rail monitor screen](../../engineering/whole-amp/control-switching/rail-monitor-review.md) is not native: initial LM393P network passes4/7 provisional limits and is rejected pending tighter thresholds. The TI download labelled LM393 actually identifies LM2903B; it was not used as classic-part evidence. C5209 has a domestic minimum-buy1 listing; exact purchase/part qualification remains open.
