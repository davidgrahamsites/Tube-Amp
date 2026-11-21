# Original schematic fidelity and explicit adaptations — v0.4

The original PPTX, images, baseline and v0.3 remain unchanged. The source is OpenValve/AX84 Renegade v1.2 (2001). This revision retains its six tube envelopes, clean/dirty preamp values, tone stacks, channel switching method, effects loop, long-tail phase inverter, EL34 pair, output transformer/load/taps and feedback/presence network. It does not claim that an old drawing establishes present-day safety or part availability.

| Difference from source | Reason / status |
|---|---|
| T1 372FX electrical reference instead of 272FX | 220V/50Hz-compatible equivalent winding class: 300-0-300V, 173mA; 6.3V/5A; dedicated 50V bias tap. Manufacturer lists original 272FX at 115V/60Hz, 172mA. Actual China replacement and lead map remain a purchasing gate. |
| Bias R40/R39/R38 = 1k/4.7k/22k plus R503 33k minimum stop | Retains previous corrected bias network for dedicated 50V tap. Source 220k/15k/56k derive bias from HV winding. Source and revised networks cannot be interchanged without checking bias. |
| R33/R34 restored to source 220k | Reverses v0.3 speculative 100k change. JJ sheet does not supply a fixed-bias grid-return limit; earlier citation did not substantiate 100k. Qualify exact selected tubes and bias stability before energizing. |
| R110/R111 1-ohm cathode sense resistors | Measurement access; introduces approximately tens of mV at idle. Socket-side grid/screen resistors remain required. |
| Series C29/C30 220u/350V plus 220k/2W sharing/bleeders | 110u effective, versus source parallel 50u+50u. Voltage-sharing/startup/leakage checks still required. |
| Downstream filter capacitors specified >=600V | Covers provisional 523V no-load envelope at 242V and 12% transformer regulation; source printed no voltage rating. Actual regulation and capacitor series need selection. |
| Standby after reservoir, bias stays live | Inherited v0.3 adaptation. Exact HVDC switch rating remains unresolved; not an approved construction choice. Do not substitute an ordinary 250VAC switch. |
| Heater reference elevation, artificial center tap | Retained for cathode follower heater/cathode stress. Heater winding CT must be insulated, not grounded simultaneously. |
| T3 220V/50Hz, 18-0-18V/0.25A | Supplies isolated +/-15V audio plus regulated +12V relays and +5V debounce logic. Source 120V and ambiguous 12V-CT supply is incompatible. |
| Existing debounced two-button controller retained | Earlier explicit user requirement, independent of tube-reverb removal. Power-off pedal insertion remains required pending hot-plug validation. |
| New solid-state spring circuit after FX return and before C19/R24 | Constant dry plus adjustable wet. Six op-amp sections, physical tank, one panel REVERB knob and internal SEND trim. Small dry loading difference and finite op-amp headroom are documented/simulated. |
| R100 marked DNP | Removes the previous tube-reverb revision's additional 1M effects-return shunt. Do not fit it. |
| No V7/V8/T4 or reverb B+ branch | Removes both added reverb tubes, their heater load and reverb driver transformer; heater budget falls to 4.2A plus pilot. |

The native connectivity check maps all integrated connected pins. Board parity checks compare native standalone export with actual pads; these do not replace a full source raster-to-pin independent engineering review or chosen-component amplifier simulation.
