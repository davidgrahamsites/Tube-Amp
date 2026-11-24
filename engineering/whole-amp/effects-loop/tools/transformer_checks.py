"""Independent analytical checks of coupled-winding model topology and polarity.
Only validates the linear fixture, never transformer construction or saturation.
"""
import json
import math
from pathlib import Path
import sys
from transformer_model import RATIO, winding_lines, integrated_deck
from fixture import ROOT, WHOLE, fingerprint
sys.path.insert(0, str(WHOLE / 'tools'))
import spice_runtime as sp

def main():
    rows = []
    sp.cmd('version')
    version = list(sp.logs)
    for hz in [50, 1000, 20000]:
        for polarity in [1, -1]:
            text = '\n'.join(['Coupled transformer analytical fixture',
                f'VDRIVE DRIVE_P DRIVE_N DC 1 AC {RATIO}', 'RCT B_MAIN 0 1gig',
                'RPA DRIVE_P PA_W 100', 'RPB PB_W DRIVE_N 100',
                *winding_lines(polarity=polarity), 'RLOAD SPEAKER 0 8', '.end']) + '\n'
            sp.load(text)
            # Winding resistance makes nonzero DC excitation well-posed.
            sp.cmd('op')
            dc = sp.vector('v(speaker)')[-1]
            sp.cmd(f'ac lin 1 {hz} {hz}')
            v = sp.vector('v(speaker)')[0]
            current = -sp.vector('i(vdrive)')[0]
            admittance = current / RATIO
            winding_y = 1 / 7600 + 1 / (1j * 2 * math.pi * hz * 40)
            expected = 1 / (200 + 1 / winding_y)
            expected_v = polarity / (1 + 200 * winding_y)
            checks = dict(dc_secondary_zero=abs(dc) < 1e-9,
                signed_loaded_turns_ratio=abs(v-expected_v) < 1e-7,
                primary_admittance=abs(admittance-expected) < 1e-9,
                real_power_balance=abs((RATIO*current.conjugate()).real-abs(v)**2/8-200*abs(current)**2) < 1e-8)
            rows.append(dict(frequency_Hz=hz, polarity=polarity, secondary_DC_V=dc,
                secondary_AC=[v.real,v.imag], primary_admittance=[admittance.real,admittance.imag],checks=checks))
            (ROOT/'results'/f'magnetics-fixture-{hz}-{polarity}.cir').write_text(text)
            sp.cmd('destroy all')
    gains = {}
    for sign in [0, 1, -1]:
        text, _ = integrated_deck(mode='return-drive',amp=0,feedback_phase=sign)
        sp.load(text); sp.cmd('op'); sp.cmd('ac lin 1 1000 1000')
        gains[str(sign)] = abs(sp.vector('v(speaker)')[0])
        (ROOT/'results'/f'magnetics-feedback-{sign}.cir').write_text(text)
        sp.cmd('destroy all')
    checks = dict(all_analytical_checks=all(all(r['checks'].values()) for r in rows),
                  intended_feedback_reduces_gain=gains['1'] < gains['0'])
    result=dict(source_hashes=fingerprint(),simulator_version_log=version,rows=rows,
                feedback_gain=gains,checks=checks,passed=all(checks.values()),physical_qualified=False)
    (ROOT/'results/magnetics-fixture-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'results/magnetics-fixture-checks.log').write_text('\n'.join(x.rstrip() for x in sp.logs)+'\n')
    print(json.dumps(result,indent=2));assert result['passed']

if __name__ == '__main__':main()
