"""Small-signal dry loading of the spare-contact wet shunt; not a pop model."""
import cmath
import hashlib
import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'results'

def calculate():
    rows = []
    for hz in [20, 100, 1000, 10000, 20000]:
        for source in [0, 10000, 100000]:
            for load in [1e6, 10e6]:
                z = 100 + 1/(2j*math.pi*hz*1e-6)
                wet_before = 1/(1e6 + 1/(1/1e6 + 1/z))
                wet_after = 1/(1e6 + 1/(1/1e6 + 1/z + 1/.1))
                before = 1/(1 + (1e5+source)*(1/load+wet_before))
                after = 1/(1 + (1e5+source)*(1/load+wet_after))
                rows.append(dict(hz=hz, source_ohm=source, load_ohm=load,
                    dry_gain_change_dB=20*math.log10(abs(after/before)),
                    phase_change_deg=math.degrees(cmath.phase(after/before))))
    return dict(scope='Passive dry-loading comparison with U12 output at zero volts, R616=100 ohm, C607=1uF, R617/R618=1Mohm, R612=100kohm and closed contact=0.1ohm. Not switching, bounce, pop or full-amplifier qualification.',
        cases=rows, max_abs_gain_change_dB=max(abs(r['dry_gain_change_dB']) for r in rows),
        max_abs_phase_change_deg=max(abs(r['phase_change_deg']) for r in rows),
        rail_step_bound=dict(voltage=16.5, series_ohm=100, capacitor_F=1e-6,
            initial_current_A=16.5/100, stored_energy_J=.5*1e-6*16.5**2),
        contact_limit_source='https://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v2.pdf',
        factory_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())

if __name__ == '__main__':
    (OUT/'final-wet-mute-loading.json').write_text(json.dumps(calculate(), indent=2)+'\n')
