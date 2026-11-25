"""Audit evidence integrity and bounded gain-cell screens, not build readiness."""
import hashlib
import json
import math
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]/'results'
data=json.loads((OUT/'ota-screen.json').read_text())
checks=[]
def check(name,passed): checks.append({'name':name,'passed':bool(passed)})
for path,digest in data['provenance'].items():
    check('input '+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest)
rows={r['name']:r for r in data['cases']}
check('29 unique retained cases',len(rows)==len(data['cases'])==29)
for row in rows.values():
    text=(OUT/row['deck']).read_bytes()
    check('deck '+row['name'],hashlib.sha256(text).hexdigest()==row['sha256'])
    if 'end_s' in row:
        check('duration '+row['name'],row['end_s']>=16/row['case']['hz']*(1-1e-7))
        thd=100*math.sqrt(sum(a*a for a in row['harmonics_peak_V']))/row['fundamental_peak_V']
        check('harmonic accounting '+row['name'],math.isclose(thd,row['thd_percent'],rel_tol=1e-10))
check('all nominal 15V cases complete',all(r['status']=='complete' for r in rows.values() if r['case'].get('rail',15)==15))
check('12V failure remains visible',rows['rail12']['status']=='timeout')
check('trim physically within travel',0<data['trim_fraction']<1)
check('calibration residual below 1mV',abs(rows['dc-calibrated']['op']['out'])<.001)
nominal=[r for n,r in rows.items() if n.startswith('audio-')]
check('nine amplitude frequency combinations',len(nominal)==9)
check('nominal amplitude within 1 percent',all(.99<r['gain']<1.01 for r in nominal))
check('nominal THD below provisional 0.1 percent',all(r['thd_percent']<.1 for r in nominal))
baseline=rows['audio-10000-10']; refined=rows['refinement']
check('halved timestep amplitude agreement',abs(refined['gain']/baseline['gain']-1)<.001)
check('halved timestep distortion agreement',abs(refined['thd_percent']-baseline['thd_percent'])<.001)
for name in ['shunt-1e+11','shunt-1e+13']:
    check('numerical shunt amplitude '+name,abs(rows[name]['gain']/rows['audio-1000-10']['gain']-1)<.0001)
    check('numerical shunt offset '+name,abs(rows[name]['op']['out']-rows['dc-calibrated']['op']['out'])<1e-5)
raw=[rows['dc-untrimmed-'+str(b)]['op']['out'] for b in ['0','5e-05','0.00025','0.0005']]
trimmed=[rows['dc-trimmed-'+str(b)]['op']['out'] for b in ['0','5e-05','0.00025','0.0005']]
raw_spread=max(raw)-min(raw); trim_spread=max(trimmed)-min(trimmed)
check('untrimmed negative control exposes >1V shift',raw_spread>1)
check('trim reduces nominal DC spread >100 times',trim_spread<raw_spread/100)
check('gain reduction is monotonic',0<rows['gain-5e-05']['gain']<rows['gain-0.00025']['gain']<rows['audio-1000-10']['gain'])
native=[]
for p in sorted((ROOT/'engineering/whole-amp/pcb-measured-r/boards').glob('*.kicad_pcb')):
    relative=str(p.relative_to(ROOT)); prior=subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT)
    check('native unchanged '+p.name,p.read_bytes()==prior)
    native.append({'path':relative,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'checks':checks,'passed':all(c['passed'] for c in checks),'native':native,
        'metrics':{'raw_dc_spread_V':raw_spread,'trimmed_dc_spread_V':trim_spread,
                   'max_nominal_thd_percent':max(r['thd_percent'] for r in nominal),
                   'refinement_gain_difference_percent':abs(refined['gain']/baseline['gain']-1)*100},
        'limits':['12V transient times out','Ideal current sources, no pedal/hot-plug/controller implementation',
                  'Manufacturer model warns optimistic stability/bandwidth','No measured tank/headroom/noise or device tolerance qualification',
                  'No China purchase readiness for carrier, sockets or complete control assembly']}
(OUT/'ota-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'passed':report['passed'],'metrics':report['metrics']},indent=2))
assert report['passed'],[c for c in checks if not c['passed']]
