"""Select exact HV100k parts; retain scoped nominal DC evidence, no CAD edits."""
from pathlib import Path
import json,csv,math
p=Path(__file__).resolve().parent
refs=['R4','R5','R7','R12','R15','R21','R30','R31','R22']
rating=2;report=[]
cases=json.loads((p/'resistor-op-results.json').read_text())['cases']
for ref in refs:
 rows=[r for c in cases for r in c['resistors'] if r['reference']==ref]
 watts=max(r['power_W'] for r in rows); volts=max(r['voltage_V'] for r in rows)
 for ambient in [70,100,125]:
  allowed=rating*min(1,(155-ambient)/(155-70))
  limit=min(500,math.sqrt(allowed*100000))
  report.append(dict(reference=ref,ambient_C=ambient,nominal_DC_W=watts,allowed_W=allowed,utilization=watts/allowed,nominal_DC_V=volts,continuous_voltage_limit_V=limit,pass_nominal_DC=watts<=allowed and volts<=limit))
assert all(r['pass_nominal_DC'] for r in report)
(p/'hv-100k-rating-screen.json').write_text(json.dumps({'mpn':'FMP200JR-52-100K','scope':'Nominal DC fixture only. Assumed local ambient values are NOT measured cabinet temperatures. No transient, fault, tolerance or chosen-tube validation.','manufacturer_source':'evidence/Yageo-FMP.pdf','results':report},indent=2)+'\n')
coverage=json.loads((p/'coverage.json').read_text())
for r in coverage:
 if r['id'] in ['P002','P023']:
  r['selected_mpn']='FMP200JR-52-100K';r['status']='selected; nominal DC rating screen passed; integrated qualification pending'
(p/'coverage.json').write_text(json.dumps(coverage,indent=2,ensure_ascii=False)+'\n')
reg=json.loads((p/'candidate-register.json').read_text())
for r in reg:
 if r['mpn']=='FMP200JR-52-100K':
  r['status']='selected for P002/P023; integrated qualification pending'
  r['notes']+=' Selected November12 for nine HV100k positions; nominal DC screen passes manufacturer derating at assumed70/100/125C. Ten-piece pack covers nine fitted plus one spare. Pulse, high-line, actual local temperature and layout remain pending. See hv-100k-selection.md.'
(p/'candidate-register.json').write_text(json.dumps(reg,indent=2,ensure_ascii=False)+'\n')
with (p/'candidate-register.csv').open('w',newline='') as f:
 fields=list(reg[0]);w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
 for row in reg:w.writerow({k:';'.join(v) if isinstance(v,list) else v for k,v in row.items()})
print('Selected9HVresistors;27 nominal DC derating checks pass. Maximum utilization:',max(x['utilization'] for x in report))
