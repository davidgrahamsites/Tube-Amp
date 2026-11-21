"""Selected KYET capacitors: nominal DC check only, not signal/startup qualification."""
from pathlib import Path
import json,sys,hashlib
p=Path(__file__).resolve().parent;sys.path.insert(0,str(p.parent/'whole-amp/tools'))
from simulate_amp import circuit,load,cmd,vector,logs
coverage=json.loads((p/'coverage.json').read_text());a=json.loads((p/'candidate-register.json').read_text())
choices={i:r['mpn'] for r in a if r['mpn'].startswith('KP') for i in r['coverage_ids']}
rows=[]
for ch in ['clean','dirty']:
 text=circuit(ch);load(text);cmd('op');lines={x.split()[0]:x.split() for x in text.splitlines() if x and x[0]=='C'}
 for c in coverage:
  if c['id'] not in choices:continue
  for ref in c['refs']:
   name='CREV_601' if ref=='C601' else ref;line=lines[name]
   def v(n):return 0 if n=='0' else vector('v('+n+')')[-1]
   dv=abs(v(line[1])-v(line[2]));rows.append(dict(channel=ch,reference=ref,mpn=choices[c['id']],nominal_DC_V=dv,rating_V=630,utilization=dv/630,passed=dv<630))
 cmd('destroy all')
(p/'film-cap-rating-screen.json').write_text(json.dumps({'scope':'Nominal400V/-40V generic model DC only. Peak AC plus DC, startup, high-line and temperature pending.','results':rows},indent=2)+'\n');(p/'film-cap-rating-screen.log').write_text('\n'.join(logs))
assert all(r['passed'] for r in rows)
print(len(rows),'checks; max DC voltage',max(x['nominal_DC_V'] for x in rows))
