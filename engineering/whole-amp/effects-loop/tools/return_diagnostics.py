"""Bounded, separate RETURN solver diagnostics; never replace acceptance cases.

Usage: python3 return_diagnostics.py ramp
Choices: trap, tight, esr, ramp. Earlier trap/tight/ESR receipts came from the
same deck substitutions in a scratch script; ESR was manually terminated.
"""
import json
import subprocess
import sys
from pathlib import Path

import return_driver as driver

VARIANTS = {
    'trap': ('method=gear maxord=2', 'method=trap maxord=2'),
    'tight': ('reltol=.001 abstol=1n vntol=10u', 'reltol=.0001 abstol=100p vntol=1u'),
    'esr': ('CB VUP VDN 100n', 'RESR VUP CBI 1\nCB CBI VDN 100n'),
    'ramp': ('VS SRC 0 DC 0 AC 1 SIN(0 1.351 20000)',
             'BVS SRC 0 V=1.351*sin(2*pi*20000*time)*(1-exp(-time/0.002))'),
}


def execute(variant):
    original = driver.deck
    old, new = VARIANTS[variant]
    def diagnostic_deck(*args, **kwargs):
        source = original(*args, **kwargs)
        assert old in source
        return source.replace(old, new)
    driver.deck = diagnostic_deck
    driver.case_key = lambda case: 'return-diagnostic-' + variant
    driver.run_one(4)  # 20 kHz, 135.1 V requested, low supply corner


if __name__ == '__main__':
    variant = sys.argv[1]
    assert variant in VARIANTS
    if '--worker' in sys.argv:
        execute(variant)
    else:
        target = driver.OUT / ('return-diagnostic-' + variant + '.json')
        try:
            process = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                      variant, '--worker'], timeout=45,
                                     capture_output=True, text=True)
            if process.returncode:
                target.write_text(json.dumps(dict(status='failed', error=process.stderr[-3000:]), indent=2)+'\n')
        except subprocess.TimeoutExpired:
            target.write_text(json.dumps(dict(status='timeout', timeout_s=45,
                scope='Diagnostic only; no electrical result or acceptance-case replacement'), indent=2)+'\n')
        print(target.read_text())
