"""HF-resolved cross-check of loaded-winding positive/negative controls."""
import hashlib
import json
from pathlib import Path

import numpy as np

from fixture import ROOT, fingerprint
from loaded_feedback_model import build
from loop_probe import sp
from sweep_loaded_feedback import hashes


def main():
    sources, factories = fingerprint(), hashes()
    factories['transient_check'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rows = []
    for label, p, step in [
        ('nominal', dict(presence=0), 1/6.4e6),
        ('high-leakage', dict(presence=0, leakage_H=.08), 1/6.4e6),
        ('negative-fine', dict(presence=0, leakage_H=.08, feedback_cap_F=220e-12), 1/6.4e6),
        ('negative-refined', dict(presence=0, leakage_H=.08, feedback_cap_F=220e-12), 1/12.8e6),
    ]:
        text = '\n'.join('BRING RET_DRIVE 0 V=.01*sin(2*pi*50000*time)*(time>0.001)*(time<0.0011)'
                         if line.startswith('VTEST ') else line for line in build(p).splitlines()) + '\n'
        name = 'loaded-burst-' + label
        (ROOT/'results'/f'{name}.cir').write_text(text)
        sp.load(text)
        sp.cmd('op')
        dc = float(sp.vector('v(speaker)')[-1])
        sp.cmd('save v(speaker)')
        sp.cmd(f'tran {step} .01 0 {step}')
        t, v = np.array(sp.vector('time')), np.array(sp.vector('v(speaker)'))
        assert t[-1] >= .01*(1-1e-8) and np.isfinite(v).all()
        grid = np.linspace(.0095, .01, 2001)
        row = dict(name=name, parameters=p, end_s=float(t[-1]), max_step_s=step,
                   operating_point_speaker_V=dc,
                   raw_late_peak_V=float(max(abs(v[t >= .009]))),
                   late_tail_peak_V=float(max(abs(v[t >= .009] - dc))),
                   burst_peak_V=float(max(abs(v[(t >= .001) & (t <= .0012)]))),
                   deck_sha256=hashlib.sha256(text.encode()).hexdigest(),
                   waveform=dict(time_s=grid.tolist(), speaker_V=np.interp(grid, t, v).tolist()))
        rows.append(row)
        sp.cmd('destroy all')
        print(name, row['late_tail_peak_V'], flush=True)
    refinement = abs(rows[3]['late_tail_peak_V']/rows[2]['late_tail_peak_V']-1)
    checks = dict(sources_preserved=sources == fingerprint(),
                  factories_preserved=all(hashes()[k] == v for k,v in factories.items() if k != 'transient_check'),
                  nominal_decays=rows[0]['late_tail_peak_V'] < 1e-5,
                  high_leakage_decays=rows[1]['late_tail_peak_V'] < 1e-5,
                  negative_oscillates=rows[2]['late_tail_peak_V'] > .1,
                  negative_refinement_agrees=refinement < .02)
    result = dict(scope='10 ms local burst at operating point; not startup, power or saturation qualification',
                  metric_correction='Initial absolute-voltage check falsely treated approximately 89 uV winding DC offset as ringing. Residual is now measured relative to the independently computed operating point; the 10 uV limit is unchanged.',
                  source_hashes=sources, factory_hashes=factories, cases=rows,
                  relative_refinement_difference=refinement, checks=checks, passed=all(checks.values()))
    (ROOT/'results/loaded-burst-summary.json').write_text(json.dumps(result, indent=2)+'\n')
    (ROOT/'results/loaded-burst.log').write_text('\n'.join(sp.logs)+'\n')
    assert result['passed'], checks


if __name__ == '__main__':
    main()
