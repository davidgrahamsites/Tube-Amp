"""Require the selected-parts register to account for every active physical reference."""
from collections import Counter
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]

def validate(coverage, circuit):
    physical={}
    for unit in circuit['components']:
        if unit['symbol']=='power_PWR_FLAG':
            continue
        physical.setdefault(unit['reference'],[]).append(unit)
    counts=Counter(ref for group in coverage for ref in group['refs'])
    duplicates=sorted(ref for ref,count in counts.items() if count!=1)
    missing=sorted(set(physical)-set(counts))
    stale=sorted(set(counts)-set(physical))
    errors=[]
    if duplicates:errors.append('Duplicate coverage: '+', '.join(duplicates))
    if missing:errors.append('Missing coverage: '+', '.join(missing))
    if stale:errors.append('Unknown active references: '+', '.join(stale))
    by_ref={ref:group for group in coverage for ref in group['refs']}
    for ref,units in physical.items():
        explicit={u['selected_mpn'] for u in units if u.get('selected_mpn')}
        if explicit and explicit!={by_ref.get(ref,{}).get('selected_mpn')}:
            errors.append('Explicit circuit/BOM MPN mismatch: '+ref)
    if errors:raise ValueError('\n'.join(errors))
    return {'physical_references':len(physical),'coverage_groups':len(coverage),
            'selected_references':sum(1 for ref in physical if by_ref[ref].get('selected_mpn')),
            'all_references_accounted_for':True,'all_parts_qualified':False}

if __name__=='__main__':
    print(json.dumps(validate(json.loads((ROOT/'engineering/component-selection/coverage.json').read_text()),
        json.loads((ROOT/'engineering/whole-amp/reverb-600/circuit.json').read_text())),indent=2))
