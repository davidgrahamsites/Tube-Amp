"""Causal diagnostics for the unadopted OPA462 RETURN experiment.

Keep the original acceptance receipts. No model/native mutation and no relaxed
tolerances. Removing bypass is a diagnostic, never an implementation proposal.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import return_driver as driver

OUT = driver.OUT
VARIANTS = ['original', 'rail-50ohm', 'bypass-10n', 'no-bypass']


def make_deck(variant, rail):
    text = driver.deck(20000, 135.1, rail, True)
    if variant == 'rail-50ohm':
        for old, new in [
            ('XUP UP VUP VP 0 VUP OPA462', 'XUP UP VUP_DRV VP 0 VUP_DRV OPA462\nRUPISO VUP_DRV VUP 50'),
            ('XDN DN VDN 0 VN VDN OPA462', 'XDN DN VDN_DRV 0 VN VDN_DRV OPA462\nRDNISO VDN_DRV VDN 50')]:
            assert text.count(old) == 1
            text = text.replace(old, new)
    elif variant in ('bypass-10n', 'no-bypass'):
        assert text.count('CB VUP VDN 100n') == 1
        text = text.replace('CB VUP VDN 100n', 'CB VUP VDN 10n' if variant == 'bypass-10n' else '* CB omitted for causal diagnostic only')
    else:
        assert variant == 'original'
    return text


def worker(variant, rail):
    assert hashlib.sha256(driver.MODEL.read_bytes()).hexdigest() == driver.SHA
    text = make_deck(variant, rail)
    # measure() captures driver.deck dynamically; install only this fixed deck.
    driver.deck = lambda *args, **kwargs: text
    key = f'return-supply-{variant}-{rail}'
    driver.case_key = lambda case: key
    started = time.monotonic()
    row = dict(variant=variant, rail_V=rail, deck_sha256=hashlib.sha256(text.encode()).hexdigest())
    try:
        row.update(driver.measure((20000, 135.1, rail, True)))
    except (AssertionError, IndexError, OSError) as err:
        row.update(status='failed', error=str(err), final_log=driver.sp.logs[-12:])
    row['elapsed_s'] = time.monotonic()-started
    (OUT/(key+'.log')).write_text('\n'.join(l.rstrip() for l in driver.sp.logs)+'\n')
    (OUT/(key+'.json')).write_text(json.dumps(row, indent=2, allow_nan=False)+'\n')


def main():
    rows = []
    for variant in VARIANTS:
        for rail in [166.6, 173.4]:
            key = f'return-supply-{variant}-{rail}'
            text = make_deck(variant, rail)
            (OUT/(key+'.cir')).write_text(text)
            target = OUT/(key+'.json')
            target.unlink(missing_ok=True)
            (OUT/(key+'.log')).unlink(missing_ok=True)
            try:
                proc = subprocess.run([sys.executable, __file__, '--worker', variant, str(rail)],
                                      timeout=45, capture_output=True, text=True)
                row = json.loads(target.read_text()) if proc.returncode == 0 and target.exists() else dict(status='failed', error=proc.stderr[-2500:])
            except subprocess.TimeoutExpired:
                row = dict(status='timeout', timeout_s=45)
            row.update(variant=variant, rail_V=rail, deck_sha256=hashlib.sha256(text.encode()).hexdigest())
            target.write_text(json.dumps(row, indent=2, allow_nan=False)+'\n')
            rows.append(row)
            result = dict(scope='Unadopted RETURN causal supply/bypass diagnostics at 20kHz, 135.1V requested peak, original interval/tolerances',
                          model_url=driver.URL, model_sha256=driver.SHA,
                          source_sha256={str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), Path(driver.__file__)]},
                          cases=rows, expected_cases=8, all_attempted=len(rows)==8,
                          native_modified=False, circuit_selected=False, headroom_qualified=False)
            (OUT/'return-supply-summary.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
            print(key, row['status'], flush=True)


if __name__ == '__main__':
    if '--worker' in sys.argv:
        worker(sys.argv[2], float(sys.argv[3]))
    else:
        main()
