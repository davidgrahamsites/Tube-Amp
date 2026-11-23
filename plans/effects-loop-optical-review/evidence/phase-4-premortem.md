# Independent pre-mortem
Reviewer: /root/loop_premortem, fresh context, read only v3.md. All five findings accepted.
1. Reference-setting acceptance could hide material wet/dry changes elsewhere. Set limits across intended controls before topology choice.
2. Narrow envelope could allow recovery clipping during ordinary use. Cover both channels, settings, frequencies, transients and pedal output; reduced behavior is a design decision.
3. Recovery disconnection alone misses loading by a failed send branch. Distinguish power-loss bypass from component-fault recovery.
4. Port protection lacks bounded voltage, source impedance, fault duration and acceptance. Resolve before part selection; include protection loading.
5. Standalone fixture success cannot establish integrated supply, switching, hum or bootstrapped-PI behavior. Integrated measurements are release gates.
