"""Scoped continuous-voltage envelopes; not fault/ESD or circuit simulation."""
from pathlib import Path
import json
p=Path(__file__).resolve().parent
coverage={x['id']:x for x in json.loads((p/'coverage.json').read_text())}
specs=[('P060','MF0207FTE52-1K',1000,5.5),('P062','MF0207FTE52-10K',10000,5.5),('P072','MF0207FTE52-1K',1000,5.5),('P073','MFR50SFTE52-100K',100000,5.5),('P085','MF0207FTE52-10K',10000,32),('P091','MF0207FTE52-220K',220000,16),('P092','MF0207FTE52-1K',1000,16),('P096','MF0207FTE52-1M',1000000,32),('P114','MF0207FTE52-100R',100,4.04)]
rows=[]
for gid,mpn,r,v in specs:
 rating=.5 if mpn.startswith('MFR') else .6
 mwv=300 if mpn.startswith('MFR') else 350
 power=v*v/(r*.99)
 allowable=rating*(155-100)/(155-70)
 row=dict(coverage_id=gid,refs=coverage[gid]['refs'],mpn=mpn,resistance_ohm=r,envelope_rms_or_dc_V=v,min_resistance_ohm=r*.99,power_W=power,local_ambient_limit_C=100,allowable_power_at_100C_W=allowable,utilization=power/allowable,maximum_working_voltage_V=mwv,passed=power<=allowable and v<=mwv,status='engineering selected conditional on documented voltage/temperature envelope; integration and fault checks pending')
 assert row['passed']; rows.append(row)
out=dict(date='2026-11-15',scope='Continuous-voltage arithmetic at 1% low resistance and 100C local ambient; no transient or fault qualification',selections=rows,groups=len(rows),references=sum(len(x['refs']) for x in rows),mpns=len(set(x['mpn'] for x in rows)))
(p/'lv-resistor-selection-2026-11-15.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['groups','references','mpns']}))
print('max utilization',max(x['utilization'] for x in rows))
