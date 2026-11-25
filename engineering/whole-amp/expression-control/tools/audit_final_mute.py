"""Audit the bounded native repair and retained sequencing diagnostic evidence.

Inputs: baseline/after XML, ERC and after DRC paths, in that order. These are
fresh KiCad exports. This audit never relaxes native rules or edits CAD.
"""
import copy
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import integrate_final_mute as m
from final_mute_loading import calculate

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pins(path):
    return {(n.get('ref'),n.get('pin')):net.get('name')
        for net in ET.parse(path).findall('./nets/net') for n in net.findall('node')}
def violations(path):
    return [(s['path'],v['type'],v['severity'],v['description'])
        for s in json.loads(path.read_text())['sheets'] for v in s['violations']]

def main():
    before_xml, after_xml, before_erc, after_erc, drc_path = map(Path,sys.argv[1:])
    checks=[]
    def check(name, result): checks.append(dict(name=name,pass_=bool(result)))
    a,b=pins(before_xml),pins(after_xml)
    delta={f'{r}.{p}':[a.get((r,p)),b.get((r,p))] for r,p in a.keys()|b.keys() if a.get((r,p))!=b.get((r,p))}
    check('exact declared XML pin delta',delta=={'K3.11':['unconnected-(K3-Pad11)','GND'],'K3.13':['unconnected-(K3-Pad13)','Net-(C607-Pad2)']})
    check('native component identities unchanged',ET.tostring(ET.parse(before_xml).find('components'))==ET.tostring(ET.parse(after_xml).find('components')))
    check('ERC unchanged',violations(before_erc)==violations(after_erc))
    drc=json.loads(drc_path.read_text())
    check('DRC zero reported violations',not drc['violations'])
    check('DRC zero opens',not drc['unconnected_items'])
    old={p:subprocess.check_output(['git','show',m.BASE+':'+p],cwd=m.ota.ROOT,text=True) for p in [m.CIR,m.SCH,m.PCB]}
    old_c=json.loads(old[m.CIR]); new_c=json.loads((m.ota.ROOT/m.CIR).read_text())
    next(c for c in old_c['components'] if c['reference']=='K3' and c['unit']==3)['pins']={'13':'WET_AC','11':'GND','9':None}
    check('circuit JSON only two pins',old_c==new_c)
    old_p=m.v.parse(old[m.PCB]);new_p=m.v.parse((m.ota.ROOT/m.PCB).read_text())
    for n,net in [('13','WET_AC'),('11','GND')]:
        pad=next(p for p in m.v.children(m.v.fps(old_p)['K3'],'pad') if p[1]==json.dumps(n))
        pad.append(['net',json.dumps(net)])
    check('all footprints holes and placement preserved',m.v.fps(old_p)==m.v.fps(new_p))
    old_ids={m.identity(x):x for x in old_p[1:] if m.identity(x)}
    new_ids={m.identity(x):x for x in new_p[1:] if m.identity(x)}
    check('all existing PCB objects preserved except declared pad nets',all(new_ids.get(k)==v for k,v in old_ids.items()))
    added=[v for k,v in new_ids.items() if k not in old_ids]
    check('only five tracks and one via added',sorted(x[0] for x in added)==['segment']*5+['via'])
    check('all new tracks axis aligned or 45 degrees',all((lambda dx,dy:abs(dx)<1e-8 or abs(dy)<1e-8 or abs(abs(dx)-abs(dy))<1e-8)(float(m.v.field(x,'start')[1])-float(m.v.field(x,'end')[1]),float(m.v.field(x,'start')[2])-float(m.v.field(x,'end')[2])) for x in added if x[0]=='segment'))
    receipt=json.loads((m.ota.OUT/'final-mute-integration.json').read_text())
    check('native hashes match integration receipt',all(digest(m.ota.ROOT/p)==h for p,h in receipt['after_sha256'].items()))
    seq=json.loads((m.ota.OUT/'power-sequence.json').read_text())
    for p,h in seq['provenance'].items():check('sequence input '+p,digest(m.ota.ROOT/p)==h)
    for row in seq['cases']:
        for kind in ['deck','log']:check(row['name']+' '+kind+' hash',digest(m.ota.OUT/row[kind])==row[kind+'_sha256'])
    failed=[r['name'] for r in seq['cases'] if r['status']!='complete-diagnostic']
    check('sequence failures retained',failed==['reference-first','negative-late'])
    check('startup not falsely qualified',seq['startup_qualified'] is False)
    loading=calculate();check('30 loading cases',len(loading['cases'])==30)
    check('dry gain change below 0.001dB in fixture',loading['max_abs_gain_change_dB']<.001)
    report=dict(baseline_commit=m.BASE,checks=checks,passed=sum(c['pass_'] for c in checks),
        total=len(checks),pin_delta=delta,sequence_failures=failed,
        native_exports_sha256={p.name:digest(p) for p in map(Path,sys.argv[1:])},
        erc=violations(after_erc),ignored_drc_checks=drc['ignored_checks'],
        scope='Evidence/native integrity only. No rail-fault monitor, full expression PCB, procurement or build-ready claim.')
    (m.ota.OUT/'final-mute-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"{report['passed']}/{report['total']} checks pass; sequence failures remain {failed}")
    if report['passed']!=report['total']:raise SystemExit(1)

if __name__=='__main__':main()
