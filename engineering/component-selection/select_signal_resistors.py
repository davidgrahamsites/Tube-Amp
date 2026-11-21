"""Exact signal resistor selections, with scoped DC screens. No native CAD mutation."""
from pathlib import Path
import json,math,csv
p=Path(__file__).resolve().parent;coverage=json.loads((p/'coverage.json').read_text());register=json.loads((p/'candidate-register.json').read_text());op=json.loads((p/'resistor-op-results.json').read_text())
# Preserve the nine already selected higher-power FMP100k resistors; avoid unresolved reverb topology and DNP HV R100.
selection={'P004':'MFR50SFTE52-1K5','P014':'MFR50SFTE52-2K7','P020':'MFR50SFTE52-1K8','P033':'MF0207FTE52-82K','P018':'MF0207FTE52-470K','P037':'MF0207FTE52-47K','P039':'MF0207FTE52-220K','P036':'MF0207FTE52-10K','P003':'MF0207FTE52-1M'}
rows=[]
for c in coverage:
 if c['id'] not in selection:continue
 mpn=selection[c['id']];rated=.5 if mpn.startswith('MFR50S') else .6;vmax=300 if mpn.startswith('MFR50S') else 350
 for ref in c['refs']:
  cases=[r for case in op['cases'] for r in case['resistors'] if r['reference']==ref]
  assert cases,ref
  power=max(r['power_W'] for r in cases);volts=max(r['voltage_V'] for r in cases);ohms=cases[0]['ohms']
  for temp in [70,100,125]:
   allowed=rated*(155-temp)/85;limit=min(vmax,math.sqrt(allowed*ohms))
   rows.append(dict(reference=ref,mpn=mpn,ambient_C=temp,nominal_DC_W=power,nominal_DC_V=volts,allowed_W=allowed,allowed_V=limit,utilization=power/allowed,passed=power<=allowed and volts<=limit))
assert all(r['passed'] for r in rows),[r for r in rows if not r['passed']]
for c in coverage:
 if c['id'] in selection:c['selected_mpn']=selection[c['id']];c['status']='selected; nominal DC/temperature screen passed; transient and native integration pending'
for r in register:
 if r['mpn'] in selection.values():r['status']='selected for groups in signal-resistor-selection.md; transient and integration pending'
(p/'signal-resistor-rating-screen.json').write_text(json.dumps({'scope':'400V stiff supply,-40V bias,generic tubes; DC only. Temperature assumptions, not measured enclosure.','results':rows},indent=2)+'\n')
(p/'coverage.json').write_text(json.dumps(coverage,indent=2)+'\n');(p/'candidate-register.json').write_text(json.dumps(register,indent=2)+'\n')
with (p/'candidate-register.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(register[0]));w.writeheader()
 for row in register:w.writerow({k:(';'.join(v) if isinstance(v,list) else v) for k,v in row.items()})
print(len(rows),'checks;',len(set(r['reference'] for r in rows)),'references; max utilization',max(r['utilization'] for r in rows))
