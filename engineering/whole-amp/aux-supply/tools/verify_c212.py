"""Read-only native preservation and manufacturer-value check for C212."""
import copy, hashlib, json, re, subprocess, sys, xml.etree.ElementTree as ET
from pathlib import Path
from correct_c212 import ROOT, MODULE, BASE, PATHS


def native_nets(tree):
    return {n.get('name'): sorted(tuple(sorted(x.attrib.items())) for x in n.findall('node'))
            for n in tree.findall('./nets/net')}


def main():
    out=MODULE/'results'
    before=ET.parse(out/'before.xml').getroot(); after=ET.parse(out/'after.xml').getroot()
    restored=copy.deepcopy(after)
    target=next(c for c in restored.findall('./components/comp') if c.get('ref')=='C212')
    assert target.findtext('value')=='47u'
    target.find('value').text='2.2u'
    checks=dict(native_named_nets_and_pins_unchanged=native_nets(before)==native_nets(after),
                only_c212_component_value_changed=ET.tostring(before.find('components'))==ET.tostring(restored.find('components')),
                new_cap_minimum_uF_above_22=47*.8>=22,
                old_aluminium_value_detected_as_inadequate=2.2<22)
    for path in PATHS:
        old=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT).decode()
        current=(ROOT/path).read_text()
        if path.endswith('.json'):
            a=json.loads(current)
            for c in a['components']:
                if c['reference']=='C212':
                    assert c['value']=='47u';c['value']='2.2u'
            checks['contract_only_value_changed']=a==json.loads(old)
        else:
            pattern=r'(\(property\s+"Reference"\s+"C212"[\s\S]*?\(property\s+"Value"\s+)"47u"'
            reverted,n=re.subn(pattern,lambda m:m.group(1)+'"2.2u"',current)
            checks['reverse_exact_'+Path(path).suffix[1:]]=n==1 and reverted==old
    for label in ['erc','control-drc']:
        a=json.loads((out/f'before-{label}.json').read_text());b=json.loads((out/f'after-{label}.json').read_text())
        a.pop('date');b.pop('date')
        if label=='control-drc':
            air_a=a.pop('unconnected_items');air_b=b.pop('unconnected_items')
            checks['control_unconnected_count_unchanged']=len(air_a)==len(air_b)
        checks[label+'_unchanged']=a==b
    # The effects/output experiments exclude this supply sheet and use ideal rails.
    # Compare emitted decks rather than claiming they now validate regulator behavior.
    sys.path.insert(0,str(ROOT/'engineering/whole-amp/effects-loop/tools'))
    import fixture
    from loaded_feedback_model import build
    current_parts=fixture.PARTS
    new_decks=[build(p,channel=channel) for channel in ['clean','dirty'] for p in [{},{'leakage_H':.08},{'feedback_cap_F':220e-12}]]
    fixture.PARTS=json.loads(subprocess.check_output(['git','show',BASE+':'+PATHS[0]],cwd=ROOT))['components']
    old_decks=[build(p,channel=channel) for channel in ['clean','dirty'] for p in [{},{'leakage_H':.08},{'feedback_cap_F':220e-12}]]
    fixture.PARTS=current_parts
    checks['six_output_experiment_decks_identical']=old_decks==new_decks
    result=dict(checks=checks,passed=all(checks.values()),baseline_commit=BASE,
                source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PATHS},
                corrected_minimum_uF=37.6, required_aluminium_nominal_minimum_uF=22,
                effects_experiment_scope='Supply sheet excluded; six emitted decks identical. No new transient run and no regulator stability claim.',
                footprint_hold='C212 selected EEUFR1H470 pitch2.5mm; provisional native pitch3.5mm must change before fabrication.',
                drc_comparison_note='Native DRC selected different endpoints within two already-unconnected nets; all non-airwire findings match, count remains90, and reverse-delta byte proof establishes unchanged board geometry/nets. Neither report is a routing pass.',
                fabrication_ready=False)
    (out/'c212-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));assert result['passed']
if __name__=='__main__':main()
