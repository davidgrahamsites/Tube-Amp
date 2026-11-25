"""Verify the exact metadata-only delta, native connectivity and stress receipts."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as E
import pymupdf

M = Path(__file__).resolve().parents[1]; ROOT = M.parents[3]; D = M/'results'
sys.path.insert(0, str(ROOT/'engineering/whole-amp/tools'))
import native_sexpr as v


def main():
    c = json.loads((M/'contract.json').read_text()); m = c['metadata']
    result = json.loads((D/'integration.json').read_text())
    def old(p): return subprocess.check_output(['git','show',c['baseline_commit']+':'+p],text=True,cwd=ROOT)
    for path,h in c['native_sha256'].items():
        text = (ROOT/path).read_text()
        if path not in result['changed_paths']:
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == h, path
            continue
        assert hashlib.sha256(text.encode()).hexdigest() == result['after_sha256'][path]
        if path == c['legacy_factory']:
            assert text == old(path).replace(m['old_silk'],m['new_silk'])
        elif path.endswith('.json'):
            a,b = json.loads(old(path)),json.loads(text)
            changed = []
            for x,y in zip(a['components'],b['components']):
                if x['reference'] in m['references']:
                    assert x['rating'] == m['old_rating'] and y['rating'] == m['new_rating']
                    y['rating'] = x['rating']; changed.append(x['reference'])
            assert sorted(changed) == sorted(m['references']) and a == b, path
        else:
            a,b = v.parse(old(path)),v.parse(text)
            kind = 'footprint' if path.endswith('.kicad_pcb') else 'symbol'
            for obj in v.children(b,kind):
                pr = {p[1].strip('"'):p for p in v.children(obj,'property')}
                if pr['Reference'][2].strip('"') in m['references']:
                    assert pr['Rating'][2] == json.dumps(m['new_rating'])
                    pr['Rating'][2] = json.dumps(m['old_rating'])
            if kind == 'footprint':
                matches = [x for x in v.children(b,'gr_text') if x[1] == json.dumps(m['new_silk'])]
                assert len(matches) == 1; matches[0][1] = json.dumps(m['old_silk'])
            assert a == b, path
    def nets(path):
        return {n.get('name'):sorted(tuple(sorted(p.attrib.items())) for p in n.findall('node'))
                for n in E.parse(path).getroot().findall('nets/net')}
    before,after = nets(D/'before.xml'),nets(D/'after.xml'); assert before == after
    def comps(path):
        out = {}
        for x in E.parse(path).getroot().findall('components/comp'):
            if x.get('ref') in m['references']:
                for p in x.findall('property'):
                    if p.get('name') == 'Rating': p.set('value', m['old_rating'])
                for f in x.findall('fields/field'):
                    if f.get('name') == 'Rating': f.text = m['old_rating']
            out[x.get('ref')] = E.tostring(x)
        return out
    cb,ca = comps(D/'before.xml'),comps(D/'after.xml'); assert cb == ca
    def erc(p): return [x for s in json.loads(p.read_text())['sheets'] for x in s['violations']]
    assert erc(D/'before-erc.json') == erc(D/'after-erc.json')
    drc = json.loads((D/'after-drc.json').read_text()); db = json.loads((D/'before-drc.json').read_text())
    for k in ['violations','unconnected_items']: assert drc[k] == db[k]
    a,b = pymupdf.open(D/'before.pdf'),pymupdf.open(D/'after.pdf'); assert len(a)==len(b)
    rasters = []
    for i in range(len(a)):
        x=a[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)); y=b[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5))
        assert (x.width,x.height,x.samples)==(y.width,y.height,y.samples),i
        rasters.append(hashlib.sha256(y.samples).hexdigest())
    s=json.loads((D/'stress.json').read_text()); assert s['all_cases_completed']
    # Known fault failure must not be reported as all-electrical-pass.
    assert len(s['ac'])==24 and len(s['cold_plate_transient'])==18 and len(s['dc_c6_short'])==6
    assert s['independent_max_error_V']<1e-5 and not s['fault_rating_screen_passed']
    assert 1<s['max_ac_C607_V']<2 and 20<s['max_transient_C607_V']<30 and s['max_DC_fault_C607_V']>63
    for p,h in s['input_sha256'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert len(s['deck_sha256']) == 72
    for p,h in s['deck_sha256'].items(): assert hashlib.sha256((D/p).read_bytes()).hexdigest()==h,p
    pro=json.loads((ROOT/'engineering/whole-amp/pcb-measured-r/boards/Renegade_Reverb.kicad_pro').read_text())
    design=pro['board']['design_settings']; assert not design.get('drc_exclusions',[])
    assert not [k for k,x in design.get('rule_severities',{}).items() if x=='ignore']
    out={'metadata_preservation_passed':True,'net_count':len(before),'components_preserved':len(cb),
         'schematic_pages_pixel_identical':len(a),'raster_sha256':rasters,
         'ERC_unchanged_count':len(erc(D/'after-erc.json')),
         'Reverb_DRC_violations':len(drc['violations']),'Reverb_unconnected':len(drc['unconnected_items']),
         'old_board_copper_pads_drills_unchanged':True,'new_pour_adopted':False,
         'stress_software_checks_passed':True,'fault_rating_screen_passed':False,
         'clearance_qualified':False,'fabrication_ready':False,
         'evidence_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir()
                            if p.suffix in ['.xml','.pdf','.json'] and p.name!='checks.json'}}
    (D/'checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:x for k,x in out.items() if k not in ['evidence_sha256','raster_sha256']},indent=2))


if __name__=='__main__': main()
