"""Measure the existing RETURN interface before selecting recovery components.

No native edits. Source/load Thevenin probes retain DC topology apart from the
normalled jack opening, which is AC-coupled on both source paths.
"""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
from fixture import fingerprint
from loaded_feedback_model import build
from run import OUT, sp

ROOT = Path(__file__).resolve().parents[4]
HZ = [20, 40, 82.4, 200, 1000, 5000, 10000, 20000]
CONFIGS = [dict(channel=c, volume=v, tone=t, gain=g) for c,v,t,g in
           itertools.product(['clean','dirty'], [.01,.25,1], [0,.5,1], [.1,1])]
RESISTANCES = [1000, 10000, 22000, 47000, 68000, 100000, 150000, 220000]
NODES = ['FX_SEND','FX_RETURN','MIX_OUT','SEND_IN','PI_G1','SPEAKER']


def deck(config, mode, resistance=1000):
    base_mode = 'buffer' if mode.startswith('buffer') else 'native'
    text = build(mode=base_mode, stimulus='wet' if mode.endswith('wet') else 'dry',
                 amp=0, source_ohm=resistance, **config)
    lines = text.splitlines()
    assert sum(l.startswith('VSOURCE ') for l in lines) == 1
    assert sum(l.startswith('VWET ') for l in lines) == 1
    assert sum(l.startswith('VTEST ') for l in lines) == 1
    clean = []
    for line in lines:
        if line.startswith('VSOURCE '):
            line = line.replace(' AC 0', ' AC 1') if mode.endswith('dry') else line.replace(' AC 1', ' AC 0')
        if line.startswith('VWET '):
            line = 'VWET OUT_BUF 0 DC 0 AC ' + ('1' if mode.endswith('wet') else '0')
        if line.startswith('VTEST '):
            line = 'VTEST RET_DRIVE 0 DC 0 AC 0'
        clean.append(line)
    lines = clean
    if mode in ('source-probe','load-probe','open-wet'):
        assert sum(l.startswith('RNORMAL ') for l in lines) == 1
        lines = [l for l in lines if not l.startswith('RNORMAL ')]
        if mode != 'open-wet':
            node = 'FX_SEND' if mode == 'source-probe' else 'FX_RETURN'
            lines.insert(lines.index('.end'), f'IPROBE 0 {node} DC 0 AC 1')
    assert mode in ('source-probe','load-probe','open-wet','native-dry','native-wet','buffer-dry','buffer-wet')
    lines[0] = 'Renegade RETURN port experiment, not selected hardware'
    return '\n'.join(lines)+'\n'


def packed(z):
    return [float(z.real), float(z.imag)]


def unpacked(pair):
    return complex(*pair)


def measure(text):
    sp.load(text); sp.cmd('op')
    op = {n:float(sp.vector('v('+n.lower()+')')[-1]) for n in NODES}
    assert all(np.isfinite(v) for v in op.values())
    result = {}
    for hz in HZ:
        sp.cmd(f'ac lin 1 {hz} {hz}')
        actual = sp.vector('frequency')[-1].real
        assert abs(actual-hz) < hz*1e-9
        result[str(hz)] = {n:packed(sp.vector('v('+n.lower()+')')[-1]) for n in NODES}
    sp.cmd('destroy all')
    return dict(op=op, points=result)


def derive(measured, resistance):
    rows = []
    for hz in HZ:
        points = {k:v['points'][str(hz)] for k,v in measured.items()}
        zs = unpacked(points['source-probe']['FX_SEND'])
        zl = unpacked(points['load-probe']['FX_RETURN'])
        # Native normal contact has 0.05 ohm in the retained reference fixture.
        zn = zs+.05
        hwet = {n:unpacked(points['open-wet'][n]) for n in NODES}
        zi = {n:unpacked(points['load-probe'][n]) for n in NODES}
        native = {n:hwet[n]-zi[n]*hwet['FX_RETURN']/(zl+zn) for n in ['MIX_OUT','SEND_IN','PI_G1','SPEAKER']}
        buffered = {n:hwet[n]-zi[n]*hwet['FX_RETURN']/(zl+resistance) for n in native}
        dry_ratio = 1e6*(zn+zl)/((zs+1e6)*(resistance+zl))
        rows.append(dict(hz=hz, source_Z_ohm=packed(zs), load_Z_ohm=packed(zl),
                         dry_ratio=packed(dry_ratio),
                         wet_native_predicted={n:packed(v) for n,v in native.items()},
                         wet_buffer_predicted={n:packed(v) for n,v in buffered.items()}))
    return rows


def main():
    rows = []
    for index, config in enumerate(CONFIGS):
        start = time.monotonic()
        measurements, hashes = {}, {}
        for mode in ['source-probe','load-probe','open-wet','native-dry','native-wet']:
            text = deck(config, mode)
            name = f'return-port-{index:02}-{mode}.cir'
            (OUT/name).write_text(text)
            hashes[name] = hashlib.sha256(text.encode()).hexdigest()
            measurements[mode] = measure(text)
        # Direct circuit comparisons validate the independent port predictions.
        direct = {}
        for resistance in (1000, 100000):
            direct[str(resistance)] = {}
            for mode in ('buffer-dry','buffer-wet'):
                text = deck(config, mode, resistance)
                name = f'return-port-{index:02}-{mode}-{resistance}.cir'
                (OUT/name).write_text(text)
                hashes[name] = hashlib.sha256(text.encode()).hexdigest()
                direct[str(resistance)][mode] = measure(text)
        row = dict(config=config, measurements=measurements, direct=direct, deck_sha256=hashes,
                   predictions={str(r):derive(measurements,r) for r in RESISTANCES},
                   elapsed_s=time.monotonic()-start)
        rows.append(row)
        sources = [Path(__file__),*(Path(__file__).with_name(n) for n in ['fixture.py','loaded_feedback_model.py','feedback_model.py','transformer_model.py','run.py']),
                   ROOT/'engineering/whole-amp/tools/spice_runtime.py']
        result = dict(scope='Open-jack AC source/load probes and same-interface fixed-output-resistance comparison; no selected recovery circuit',
                      input_sha256=fingerprint(), source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                      frequencies_Hz=HZ, input_buffer_ohm=1e6, output_resistances_ohm=RESISTANCES,
                      expected_configs=len(CONFIGS), all_attempted=len(rows)==len(CONFIGS),
                      cases=rows, native_modified=False, circuit_selected=False, fabrication_release=False)
        (OUT/'return-port-summary.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
        print(index, config, 'completed', flush=True)
    (OUT/'return-port.log').write_text('\n'.join(l.rstrip() for l in sp.logs)+'\n')


if __name__ == '__main__':
    main()
