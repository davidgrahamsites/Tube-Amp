"""Compare native before/after XML, ERC and protected-board hashes.
Usage: python verify_protection_native.py BEFORE_XML BEFORE_ERC BEFORE_HASHES
Baseline can be reproduced by exporting the recorded baseline Git revision.
"""
from pathlib import Path
import copy,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
REVIEW=ROOT.parent/'reverb-600/review'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def nets(tree):
    return {n.get('name'):sorted(tuple(sorted(x.attrib.items())) for x in n.findall('node')) for n in tree.findall('./nets/net')}
def violations(data):
    return {json.dumps(dict(sheet=s['path'],violation=v),sort_keys=True) for s in data['sheets'] for v in s['violations']}
def main():
    before,erc,hashes=map(Path,sys.argv[1:])
    old=ET.parse(before).getroot();new=ET.parse(REVIEW/'grounding-native.xml').getroot()
    record_path=ROOT/'results/protection-native-integration.json';r=json.loads(record_path.read_text())
    originals={c.get('ref'):ET.tostring(c) for c in old.findall('./components/comp')}
    restored=copy.deepcopy(new)
    for c in restored.findall('./components/comp'):
        change=next((x for x in r['changes'] if x['reference']==c.get('ref')),None)
        if change:
            assert c.findtext('value')==change['after']['Value']
            c.find('value').text=change['before']['Value']
            for item in c.findall('./fields/field')+c.findall('property'):
                key=item.get('name')
                if key not in ['Rating','Design_status']:continue
                if item.tag=='field':
                    assert item.text==change['after'][key];item.text=change['before'][key]
                else:
                    assert item.get('value')==change['after'][key];item.set('value',change['before'][key])
    final={c.get('ref'):ET.tostring(c) for c in restored.findall('./components/comp')}
    b=json.loads(hashes.read_text());a=violations(json.loads(erc.read_text()));z=violations(json.loads((REVIEW/'protection-erc.json').read_text()))
    contract_path='engineering/whole-amp/reverb-600/circuit.json'
    original_contract=json.loads(subprocess.check_output(['git','show',r['baseline_commit']+':'+contract_path],cwd=REPO))
    restored_contract=json.loads((REPO/contract_path).read_text())
    for c in restored_contract['components']:
        change=next((x for x in r['changes'] if x['reference']==c['reference']),None)
        if change:
            for prop,key in [('Value','value'),('Rating','rating'),('Design_status','status')]:
                assert c[key]==change['after'][prop];c[key]=change['before'][prop]
    matrix=json.loads((ROOT/'results/protection-acceptance-summary.json').read_text())
    tests=dict(exact_named_net_and_endpoint_preservation=nets(old)==nets(new),
        only_authorized_component_fields_changed=originals==final,
        only_authorized_contract_fields_changed=original_contract==restored_contract,
        stress_matrix_uses_exact_prechange_circuit=all(x['source_hashes'][contract_path]==r['before_hashes'][contract_path] for x in matrix['cases']),
        protected_boards_unchanged=all(sha(REPO/p)==h for p,h in b.items() if p.endswith('.kicad_pcb')),
        other_native_sheets_unchanged=all(sha(REPO/p)==h for p,h in b.items() if p.endswith('.kicad_sch') and not p.endswith('/04_output.kicad_sch')),
        no_new_ERC=z.issubset(a))
    r.update(native_connectivity_comparison='PASS' if all(tests.values()) else 'FAIL',native_checks=tests,
        before_xml_sha256=sha(before),after_xml_sha256=sha(REVIEW/'grounding-native.xml'),
        components=len(originals),named_nets=len(nets(new)),erc_before=len(a),erc_after=len(z),
        remaining_erc=[json.loads(x) for x in sorted(z)],
        library_repair='Added existing Renegade_Selected library and made library paths project-relative; no check suppression',
        visual_review=dict(scope='Changed output sheet only; no all-project readability certification',
            full_page='engineering/whole-amp/reverb-600/review/protection-output.pdf',
            inspected=['Full output sheet','Enlarged V5/R41 and V6/R42 branches'],
            changed_values_readable=True,changed_text_overlap=False))
    record_path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(checks=tests,erc_before=len(a),erc_after=len(z)),indent=2));assert all(tests.values())
if __name__=='__main__':main()
