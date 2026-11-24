"""Repeat the bounded coupled-magnetics overload/peaking diagnostics.
Public outputs: magnetics-overload-summary.json and named case evidence.
"""
import json
from transformer_run import bounded, OUT
from fixture import fingerprint

CONFIG = dict(channel='clean', mode='native', freq=1000, amp=.1, supply=278,
              volume=1, tone=.5, gain=.5, guard_pentode_power=True)
CASES = [('clean-overload-1k', CONFIG, {}),
         ('dirty-overload-1k', dict(CONFIG, channel='dirty', amp=1), {}),
         ('dirty-overload-5k', dict(CONFIG, channel='dirty', amp=1, freq=5000), {}),
         ('peaking-20k', dict(CONFIG, amp=.00672, freq=20000), dict(half_primary_H=40, coupling=.995))]

def main():
    result = dict(scope='Coupled linear magnetics overload and peaking diagnostics; assumed parameters, no core saturation',
                  source_hashes=fingerprint(), cases=[], physical_qualified=False, fabrication_ready=False)
    for name, cfg, tx in CASES:
        result['cases'].append(bounded('magnetics-'+name, cfg, tx))
        (OUT/'magnetics-overload-summary.json').write_text(json.dumps(result, indent=2)+'\n')

if __name__ == '__main__':main()
