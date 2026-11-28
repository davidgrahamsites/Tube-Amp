"""CB-005. Connect the CB-002 servo to the source-derived downstream fixture."""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from composite_return import M, ROOT, deck as recovery, sp

sys.path.insert(0, str(M.parent / 'tools'))
from loaded_feedback_model import build
from fixture import fingerprint

RESULT = M / 'results' / 'integrated-load.json'
REFERENCE = M.parent / 'results' / 'return-port-summary.json'
SPEC = M / 'composite-return.json'
CAPS_PF = (0, 100, 500)


def replace_one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def circuit(hz, amplitude, capacitance):
    tube = build(mode='buffer', source_ohm=1000, supply=278, channel='clean',
                 amp=0, freq=hz, volume=1, tone=.5, gain=.5)
    tube = replace_one(tube, 'RBUF_OUT BUF_OUT FX_RETURN 1000', '* recovery drives FX_RETURN')
    assert ' AC 0 SIN(' in tube
    tube = replace_one(tube, 'VTEST RET_DRIVE 0 DC 0 AC 1', '* inactive test source removed')
    spec = json.loads(SPEC.read_text())
    case = next(row for row in spec['cases'] if row['id'] == 'servo-sink-20k')
    params = {**spec['default'], **case, 'opamp_model': spec['opamp_model'],
              'frequency_Hz': hz, 'input_peak_V': amplitude / 100}
    stage = recovery(params).split('\n', 1)[1]
    stage = replace_one(stage, 'RLOAD load 0 340000', 'VPORT load FX_RETURN 0')
    stage = replace_one(stage, 'CLOAD load 0 100p',
                        f'CHARNESS FX_RETURN 0 {capacitance}p' if capacitance else '* no added capacitor')
    return replace_one(tube, '.end\n', stage)


def run_case(hz, amplitude, pf, reference):
    net = circuit(hz, amplitude, pf)
    sp.load(net)
    sp.cmd('op')
    bias = sp.vector('v(out)')[-1]
    assert abs(bias - 200) < 1 and abs(sp.vector('v(sense)')[-1] - 1) < .01
    sp.cmd(f'ac lin 1 {hz} {hz}')
    current = sp.vector('i(vport)')[-1]
    admittance = current / sp.vector('v(fx_return)')[-1]
    expected = 1 / reference + 2j * np.pi * hz * pf * 1e-12
    ac_error = abs(admittance / expected - 1)
    assert ac_error < .005, (hz, pf, admittance, expected)
    probes = ['v(fx_return)', 'i(vport)', 'v(send_in)', 'v(gate)', 'v(drive)', 'v(out)',
              'v(csgate)', 'v(sense)']
    sp.cmd('save ' + ' '.join(probes))
    step = 1 / (hz * (640 if hz == 20000 else 320))
    end = .003 if hz == 20000 else .05
    sp.cmd(f'tran {step} {end} 0 {step}')
    t = np.array(sp.vector('time'))
    row = dict(hz=hz, target_Vpk=amplitude, added_pF=pf, bias_V=bias,
               admittance_S=[admittance.real, admittance.imag], ac_error_fraction=ac_error,
               linear_target_current_mApk=1000 * amplitude * abs(admittance),
               requested_end_s=end, reached_s=float(t[-1]) if len(t) else 0, max_step_s=step,
               deck_sha256=hashlib.sha256(net.encode()).hexdigest())
    if row['reached_s'] < end * (1 - 1e-8):
        row.update(status='incomplete', solver_messages=sp.logs[-12:])
        sp.cmd('destroy all')
        return row
    assert np.isfinite(t).all() and np.all(np.diff(t) > 0)
    def samples(name, stop):
        times = stop + (np.arange(3200) / 320 - 10) / hz
        return np.interp(times, t, sp.vector(name))
    v, i, send, gate, drive, out, csgate, sense = [samples(n, end) for n in probes]
    harm = 2 * abs(np.fft.rfft(v) / len(v))[np.arange(1, 11) * 10]
    previous = samples(probes[0], end - 10 / hz)
    prior_current = samples(probes[1], end - 10 / hz)
    row.update(status='completed', fundamental_Vpk=harm[0], thd_percent=100*np.linalg.norm(harm[1:])/harm[0],
               port_current_mA=[1000*i.min(), 1000*i.max()], send_input_abs_Vpk=max(abs(send)),
               max_abs_Vgs=max(max(abs(gate)), max(abs(drive-out)), max(abs(csgate-sense))),
               successive_window_voltage_rms_difference_V=np.sqrt(np.mean((v-previous)**2)),
               successive_window_current_rms_difference_mA=1000*np.sqrt(np.mean((i-prior_current)**2)))
    sp.cmd('destroy all')
    print(hz, amplitude, pf, row['fundamental_Vpk'], row['thd_percent'], flush=True)
    return row


def main():
    refs = json.loads(REFERENCE.read_text())
    points = next(c for c in refs['cases'] if c['config']==dict(channel='clean',volume=1,tone=.5,gain=1)
                  )['measurements']['load-probe']['points']
    with ProcessPoolExecutor(max_workers=3) as pool:
        jobs = [pool.submit(run_case, hz, a, pf, complex(*points[str(hz)]['FX_RETURN']))
                for hz, a in [(1000, 4.27), (1000, 135), (20000, 135)] for pf in CAPS_PF]
        cases = [job.result() for job in jobs]
    sources = [REFERENCE, SPEC, Path(__file__), M/'tools/composite_return.py',
               ROOT/'engineering/solid-state-reverb/simulation/models/OPAx134.LIB',
               M.parent.parent/'tools/spice_runtime.py']
    sources.extend(M.parent/'tools'/name for name in (
        'fixture.py', 'transformer_model.py', 'feedback_model.py', 'loaded_feedback_model.py'))
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result = dict(id='CB-005', sources={**fingerprint(), **hashes}, cases=cases, hardware_qualified=False)
    RESULT.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
