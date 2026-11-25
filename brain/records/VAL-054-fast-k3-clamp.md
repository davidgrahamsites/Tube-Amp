---
id: VAL-054
type: validation
domain: schematic
status: documented
updated: 2026-11-25
---
# Faster K3 clamp and lower raw-warning candidate

[Owned review](../../engineering/whole-amp/control-switching/fast-clamp-review.md) proposes STSMBJ16A-TR drain-to-ground, with both ordinary K3 flyback paths removed, and2.94k/1.01k/1M raw-warning divider. This is candidate-only; native CAD and functional blocks are unchanged.

Twenty-four coil cases give7.446ms maximum time to5% current under the declared fixed-inductance bounds. Conservative sub-1mA tail is included. Hot drain formula21.834V leaves6.166V below30V after a2V overshoot allocation. Actual harness switching peaks and mechanical contacts are unqualified. Independent numerical integration agrees within0.691µs; two coil extremes pass two-timestep SPICE cross-checks. A deliberately retained ordinary diode restores13.940ms decay, demonstrating the topology conflict.

All32 loaded brownout cases pass this conditional trial: minimum healthy-enable margin163.49mV, minimum timing reserve0.480ms. The latter is thin and depends on the still-unverified5ms contact/logic allocation. Earlier eight low-line failures remain preserved in VAL-053. Three corrupted-evidence controls are rejected and91 native/source CAD files retain their startup hashes. Scoped ICM check is clean.

Chinese LCSC lists exact STC133672/SMBJ16A-TR with8873 stock, minBuyNumber1/conversionRatio5 on November25. Domestic courier policy supports a Shanghai sourcing route; price tier/delivery quote not reserved. Manufacturer Rev12 PDF is retained and distinguished from matching current Rev14 web data. No purchase or supplier message.

Next: complete the combined REF5/raw/rail/AC-loss/inhibit sequencing and exact removable-carrier/footprint budget, then native integration and three-board populated fit. Do not interpret this narrow simulated pass as build readiness. All six scopes remain incomplete.
