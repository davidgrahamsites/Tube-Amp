"""Static leakage screen, not a warm-up/temperature or transformer qualification."""
from itertools import product
from pathlib import Path
import json

TOTAL_V = 510.31  # Highest existing assumed-winding simulation; not measured PT limit.
NOMINAL_R = 220000
TOLERANCE = 0.05
parts = {
    'EHS2GM221M45OT': {'rated_V': 400, 'leakage_A': (0.02*220*400+25)*1e-6},
    'LGU2G221MELB': {'rated_V': 400, 'leakage_A': 3*(220*400)**0.5*1e-6},
}
results = []
for mpn, part in parts.items():
    corners = []
    for r1, r2, i1, i2 in product(
        [NOMINAL_R*(1-TOLERANCE), NOMINAL_R*(1+TOLERANCE)],
        [NOMINAL_R*(1-TOLERANCE), NOMINAL_R*(1+TOLERANCE)],
        [0, part['leakage_A']], [0, part['leakage_A']]):
        v1 = (TOTAL_V/r2 + i2-i1)/(1/r1+1/r2)
        v2 = TOTAL_V-v1
        corners.append({'r1':r1,'r2':r2,'i1':i1,'i2':i2,
                        'v1':v1,'v2':v2,'p1':v1*v1/r1,'p2':v2*v2/r2})
    worst = max(corners, key=lambda x:max(x['v1'],x['v2']))
    maximum = max(worst['v1'],worst['v2'])
    results.append({'mpn':mpn,'total_assumed_V':TOTAL_V,
                    'leakage_bound_A':part['leakage_A'],
                    'max_cap_V':maximum,'rating_margin_V':part['rated_V']-maximum,
                    'max_balancing_resistor_W':max(max(c['p1'],c['p2']) for c in corners),
                    'passes_static_20C_5min_screen':maximum<part['rated_V'],
                    'worst_corner':worst})
output={'scope':'20C five-minute leakage bounds, 5% balancing resistors, assumed510.31V supply. Not hot leakage, startup, aged-cap fault or actual PT validation.',
        'initial_capacitance_only_max_V':TOTAL_V*1.2/(0.8+1.2),
        'results':results}
Path(__file__).with_name('reservoir-balance-results.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
