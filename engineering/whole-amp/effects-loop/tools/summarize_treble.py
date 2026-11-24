"""Compare compensation with its matched unchanged-C22/R31 baseline.
Produces evidence for the user's treble priority; no invented tonal pass limit.
"""
from pathlib import Path
import csv,json,hashlib
import math
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'results';s=json.loads((out/'feedback-summary.json').read_text());by={c['name']:c for c in s['cases']};rows=[]
for c in s['cases']:
    if '-comp' not in c['name'] and '-lead' not in c['name']:continue
    p=c['parameters'];base=by[f'feedback-comp47-lk{round(p["leakage_H"]*1000)}-pres{p["presence"]}']
    a=c['analysis'];b=base['analysis'];row=dict(case=c['name'],baseline=base['name'],C22_pF=round((p['pi_cap_F'] or 47e-12)*1e12),added_R31_cap_pF=round(p['feedback_cap_F']*1e12),leakage_mH=round(p['leakage_H']*1000),presence_fraction=p['presence'])
    for hz in [1000,5000,10000,20000]:row[f'change_{hz}Hz_dB']=20*math.log10(a['points'][str(hz)]['gain_V_V']/b['points'][str(hz)]['gain_V_V'])
    row.update(gain_margin_dB=a['min_gain_margin_dB'],unity_angle_distance_deg=a['min_unity_angle_deg'],HF_peak_relative_1k_dB=a['HF_peak_relative_1k_dB']);rows.append(row)
with (out/'feedback-treble-comparison.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={}
for label,match in [('C22_470pF',lambda r:r['C22_pF']==470),('R31_47pF',lambda r:r['added_R31_cap_pF']==47),('C22_100pF',lambda r:r['C22_pF']==100)]:
    subset=[r for r in rows if match(r)];summary[label]={str(hz):[min(r[f'change_{hz}Hz_dB'] for r in subset),max(r[f'change_{hz}Hz_dB'] for r in subset)] for hz in [5000,10000,20000]}
result=dict(scope='Matched baseline change across tested transformer and Presence positions; not acoustic pickup or speaker response',source='feedback-summary.json',source_sha256=hashlib.sha256((out/'feedback-summary.json').read_bytes()).hexdigest(),factory_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=len(rows),range_of_gain_change_dB=summary,user_numeric_tone_threshold=None,no_compensation_adopted=True)
(out/'feedback-treble-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
