"""Independent ngspice OP check of saved static leakage corners."""
import sys, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'whole-amp'/'tools'))
from spice_runtime import load,cmd,vector,logs
data=json.loads((ROOT/'reservoir-balance-results.json').read_text())
rows=[]
try:
    for case in data['results']:
        c=case['worst_corner']
        deck=f'''Reservoir static leakage corner: {case['mpn']}
V1 raw 0 {case['total_assumed_V']}
R501 raw mid {c['r1']}
R502 mid 0 {c['r2']}
C29 raw mid 220u
C30 mid 0 220u
I29 raw mid {c['i1']}
I30 mid 0 {c['i2']}
.end
'''
        (ROOT/(case['mpn']+'-balance.cir')).write_text(deck)
        load(deck);cmd('op')
        raw=vector('v(raw)')[0];mid=vector('v(mid)')[0]
        error=max(abs(raw-mid-c['v1']),abs(mid-c['v2']))
        assert error<1e-6, (case['mpn'],error)
        rows.append({'mpn':case['mpn'],'upper_V':raw-mid,'lower_V':mid,
                     'analytic_difference_V':error})
        cmd('destroy all')
    (ROOT/'reservoir-balance-ngspice.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
finally:
    (ROOT/'reservoir-balance-ngspice.log').write_text('\n'.join(logs)+'\n')
