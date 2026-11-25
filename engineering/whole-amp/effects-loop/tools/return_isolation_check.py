"""Regression and timestep checks for the unadopted 50-ohm rail experiment.

Reuse the original RETURN deck/measurement seam; no vendor-model changes,
looser tolerances, shortened runs, or native-circuit changes.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import return_driver as driver

OUT = driver.OUT
CASES = [(case, 1) for case in driver.CASES if case[3]] + [
    ((20000, 135.1, rail, True), 2) for rail in (166.6, 173.4)]
TIMEOUT_S = 90


def deck(case):
    text = driver.deck(*case)
    for unit, sense, rail, power in [('UP', 'UP', 'VUP', 'VP 0'), ('DN', 'DN', 'VDN', '0 VN')]:
        old = f'X{unit} {sense} {rail} {power} {rail} OPA462'
        new = f'X{unit} {sense} {rail}_DRV {power} {rail}_DRV OPA462\nR{unit}ISO {rail}_DRV {rail} 50'
        assert text.count(old) == 1
        text = text.replace(old, new)
    return text


def key(index):
    case, divisor = CASES[index]
    return 'return-isolated-' + '-'.join(str(v) for v in case[:3]) + f'-step{divisor}'


def worker(index):
    assert hashlib.sha256(driver.MODEL.read_bytes()).hexdigest() == driver.SHA
    case, divisor = CASES[index]
    text = deck(case)
    driver.deck = lambda *args, **kwargs: text
    driver.case_key = lambda case: key(index)
    row = dict(case=list(case), step_divisor=divisor,
               deck_sha256=hashlib.sha256(text.encode()).hexdigest())
    start = time.monotonic()
    try:
        row.update(driver.measure(case, step_divisor=divisor,
                                  extra_nodes=('VUP_DRV', 'VDN_DRV')))
        row['isolation_resistors'] = {}
        t = np.array(driver.sp.vector('time'))
        for rail in ('vup', 'vdn'):
            drop = np.array(driver.sp.vector(f'v({rail}_drv)'))-np.array(driver.sp.vector(f'v({rail})'))
            # Integrate over the last ten cycles; adaptive sample count is not a time weight.
            start_t, stop_t = row['end_s']-10/case[0], row['end_s']
            inside = (t > start_t) & (t < stop_t)
            tw = np.r_[start_t, t[inside], stop_t]
            dw = np.interp(tw, t, drop)
            row['isolation_resistors'][rail] = dict(
                maximum_absolute_drop_V=float(np.max(np.abs(dw))),
                maximum_absolute_current_A=float(np.max(np.abs(dw))/50),
                average_power_W=float(np.trapz(dw*dw/50, tw)/(stop_t-start_t)))
    except (AssertionError, IndexError, OSError) as err:
        row.update(status='failed', error=str(err), final_log=driver.sp.logs[-12:])
    row['elapsed_s'] = time.monotonic()-start
    (OUT/(key(index)+'.log')).write_text('\n'.join(line.rstrip() for line in driver.sp.logs)+'\n')
    (OUT/(key(index)+'.json')).write_text(json.dumps(row, indent=2, allow_nan=False)+'\n')


def run():
    rows = []
    for index, (case, divisor) in enumerate(CASES):
        target = OUT/(key(index)+'.json')
        target.unlink(missing_ok=True)
        (OUT/(key(index)+'.log')).unlink(missing_ok=True)
        text = deck(case)
        (OUT/(key(index)+'.cir')).write_text(text)
        try:
            proc = subprocess.run([sys.executable, __file__, '--worker', str(index)],
                                  timeout=TIMEOUT_S, capture_output=True, text=True)
            row = json.loads(target.read_text()) if proc.returncode == 0 and target.exists() else dict(status='failed', error=proc.stderr[-2500:])
        except subprocess.TimeoutExpired:
            row = dict(status='timeout', timeout_s=TIMEOUT_S)
        row.update(case=list(case), step_divisor=divisor,
                   deck_sha256=hashlib.sha256(text.encode()).hexdigest())
        target.write_text(json.dumps(row, indent=2, allow_nan=False)+'\n')
        rows.append(row)
        sources = [Path(__file__), Path(driver.__file__), Path(__file__).with_name('run.py'),
                   Path(__file__).parents[2]/'tools/spice_runtime.py']
        result = dict(scope='Unadopted 50-ohm isolation of each floating rail follower, original 100nF bypass retained',
                      model_url=driver.URL, model_sha256=driver.SHA,
                      sources={str(p.relative_to(Path(__file__).parents[4])):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                      cases=rows, expected_cases=len(CASES), all_attempted=len(rows)==len(CASES),
                      native_modified=False, circuit_selected=False, headroom_qualified=False)
        (OUT/'return-isolated-summary.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
        print(key(index), row['status'], flush=True)


if __name__ == '__main__':
    if '--worker' in sys.argv:
        worker(int(sys.argv[2]))
    else:
        run()
