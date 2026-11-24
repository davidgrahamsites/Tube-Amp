# Socket policy — FB-117

Owner: Renegade integration. Inputs: the user's November24 clarification, active source IC/tube inventory and exact contact/package evidence. Output: per-device socket decisions in socket-plan.json and the populated assembly.

Use an actual socket beneath DIP ICs by default. It enables replacement without repeated desoldering; it does not inherently improve noise or electrically protect a chip. A DIP package describes the chip's leads, so the separate socket still needs its own BOM entry, footprint, height and removal space.

The user permits a component-specific exception if a socket materially degrades operation. Record the device, evidence, affected electrical/thermal/mechanical behavior and chosen mounting method before changing the manifest/native board. A theoretical parasitic present in every socket is not by itself a reason to discard the serviceability preference. No exception is currently adopted. All six tubes retain proper tube sockets and retention.

For U10–U12 OPA2134, evaluate input/feedback capacitance, contact quality and supply-loop inductance with nearby bypass capacitors. TI's [OPA2134 layout guidance](https://www.ti.com/lit/ds/symlink/opa2134.pdf), section7.4, requires compact input/feedback paths and local ceramic supply bypass. It does not establish a blanket socket prohibition. TI explicitly discourages sockets for a different, much faster [OPA2891 family](https://www.ti.com/lit/ds/symlink/opa2891.pdf); that warning demonstrates why decisions must be part-specific, not a reason to exempt the current audio ICs. Current OPA2134 socket suitability still needs actual circuit/layout evidence.

U1/U2 logic sockets need correct lead fit, orientation, bypass and retention. U3's candidate removable carrier and U4–U7 regulator contacts/thermal fastening remain unresolved, with direct soldering now available as an engineering exception only when the documented performance comparison warrants it. No arbitrary extra adapters are required at the expense of reliable operation.

Human check: inspect socket fit and retention, swap a device with power removed, and verify stability/noise and temperatures on the assembled board. ESD handling remains necessary when inserting or removing sensitive ICs.
