"""Independently check the capacitor-only integration and native exports."""
from pathlib import Path
import collections
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as E
import pymupdf

M = Path(__file__).resolve().parents[1]; ROOT = M.parents[2]; D = M/'results'
sys.path.insert(0, str(ROOT/'engineering/whole-amp/tools'))
import native_sexpr as n

def props(x): return {p[1].strip('"'): p for p in n.children(x, 'property')}
def objects(x, kind):
    return {n.field(p,'uuid')[1]:p for p in n.children(x,kind)}
def ref(x): return props(x)['Reference'][2].strip('"')

def main():
    c=json.loads((M/'contract.json').read_text()); receipt=json.loads((D/'integration.json').read_text())
    def old(p): return subprocess.check_output(['git','show',c['baseline_commit']+':'+p],cwd=ROOT,text=True)
    for p,h in c['native_sha256'].items():
        now=(ROOT/p).read_bytes()
        assert hashlib.sha256(now).hexdigest()==receipt['after_sha256'].get(p,h),p
        if p not in receipt['changed_paths']: continue
        a,b=old(p),now.decode()
        if p.endswith('.json'):
            a,b=json.loads(a),json.loads(b)
            aa=[x for x in a['components'] if x['reference']=='C607'];bb=[x for x in b['components'] if x['reference']=='C607']
            assert len(aa)==len(bb)==1
            assert aa[0]['value']==bb[0]['value']=='1u' and aa[0]['pins']==bb[0]['pins']=={'1':'OUT_AC','2':'WET_AC'}
            assert bb[0]['selected_mpn']==c['mpn'] and bb[0]['footprint']==c['footprint']
            b['components'][b['components'].index(bb[0])]=aa[0];assert a==b,p
        elif p.endswith('.kicad_sch'):
            a,b=n.parse(a),n.parse(b)
            aa={ref(x):x for x in n.children(a,'symbol')};bb={ref(x):x for x in n.children(b,'symbol')}
            for key in ['Footprint','Rating','Datasheet','Selected_MPN','Selection_evidence']:
                props(bb['C607'])[key][2]=props(aa['C607'])[key][2]
            assert a==b,p
        else:
            a,b=n.parse(a),n.parse(b)
            fa={ref(x):x for x in n.children(a,'footprint')};fb={ref(x):x for x in n.children(b,'footprint')}
            assert fa.keys()==fb.keys()
            for r in fa:
                if r!='C607':assert fa[r]==fb[r],r
            cap=fb['C607'];assert cap[1].strip('"')==c['footprint']
            assert list(map(float,n.field(cap,'at')[1:3]))==[131.5,53]
            for i,pad in enumerate(n.children(cap,'pad')):
                assert n.field(pad,'drill')[1:]==['1.0']
                assert list(map(float,n.field(pad,'at')[1:3]))==[10*i,0]
                assert n.field(pad,'net')==n.field(n.children(fa['C607'],'pad')[i],'net')
            sa,sb=objects(a,'segment'),objects(b,'segment');removed=set(sa)-set(sb);added=set(sb)-set(sa)
            assert removed=={'"'+x['old_segment_uuid']+'"' for x in c['routes']} and len(added)==4
            for uid in sa.keys()&sb.keys():assert sa[uid]==sb[uid],uid
            for uid in added:
                s=sb[uid];assert n.field(s,'width')[1]=='0.3' and n.field(s,'layer')[1]=='"F.Cu"'
                p,q=n.field(s,'start'),n.field(s,'end');dx=abs(float(p[1])-float(q[1]));dy=abs(float(p[2])-float(q[2]))
                assert dx==0 or dy==0 or abs(dx-dy)<1e-8
            actual=collections.Counter((n.field(sb[u],'net')[1].strip('"'),tuple(map(float,n.field(sb[u],'start')[1:])),tuple(map(float,n.field(sb[u],'end')[1:]))) for u in added)
            expected=collections.Counter((r['net'],tuple(a),tuple(b)) for r in c['routes'] for a,b in zip(r['new_points_mm'],r['new_points_mm'][1:]))
            assert actual==expected
            # Verify every other board object, including vias, arcs, zones and settings.
            assert [x for x in a if not(isinstance(x,list) and x[0] in ['footprint','segment'])]==[x for x in b if not(isinstance(x,list) and x[0] in ['footprint','segment'])]
            assert not n.children(b,'zone')
    def nets(p):
        return {x.get('name'):sorted(tuple(sorted(y.attrib.items())) for y in x.findall('node')) for x in E.parse(p).findall('nets/net')}
    assert nets(D/'before.xml')==nets(D/'after.xml')
    def components(p):return {x.get('ref'):(x.findtext('value'),tuple(sorted(x.find('libsource').attrib.items())),tuple(y.text for y in x.findall('tstamps/tstamp'))) for x in E.parse(p).findall('components/comp')}
    assert components(D/'before.xml')==components(D/'after.xml')
    def erc(p):return [v for s in json.loads(p.read_text())['sheets'] for v in s['violations']]
    assert erc(D/'before-erc.json')==erc(D/'after-erc.json')
    drc=json.loads((D/'after-drc.json').read_text());assert not drc['violations'] and not drc['unconnected_items']
    a,b=pymupdf.open(D/'before.pdf'),pymupdf.open(D/'after.pdf');assert len(a)==len(b)
    for i in range(len(a)):
        assert a[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).samples==b[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).samples,i
    def holes(folder):
        hits=[]
        for p in sorted(folder.glob('*.drl')):
            import re
            tools={};tool=None
            for line in p.read_text().splitlines():
                m=re.fullmatch(r'T(\d+)C([\d.]+)',line)
                if m:tools[m[1]]=float(m[2]);continue
                m=re.fullmatch(r'T(\d+)',line)
                if m:tool=m[1];continue
                if line.startswith('X'):hits.append((tools[tool],line))
        assert hits
        return collections.Counter(hits)
    before,after=holes(D/'drill-before'),holes(D/'drill-after')
    removed=before-after;added=after-before
    assert removed==collections.Counter({(.9,'X133.0Y-49.0'):1,(.9,'X138.0Y-49.0'):1}),removed
    assert added==collections.Counter({(1.,'X131.5Y-53.0'):1,(1.,'X141.5Y-53.0'):1}),added
    assert hashlib.sha256((M/'evidence/KNSCHA-MPP105J2W10KN22605.pdf').read_bytes()).hexdigest()==c['datasheet_sha256']
    pro=json.loads((ROOT/'engineering/whole-amp/pcb-measured-r/boards/Renegade_Reverb.kicad_pro').read_text())['board']['design_settings']
    assert not pro.get('drc_exclusions') and not any(v=='ignore' for v in pro.get('rule_severities',{}).values())
    result={'passed':True,'nets_preserved':len(nets(D/'after.xml')),'components_preserved':len(components(D/'after.xml')),'pixel_identical_schematic_pages':len(a),'ERC_unchanged_count':len(erc(D/'after-erc.json')),'DRC_violations':0,'unconnected_items':0,'changed_round_holes':2,'moved_pads':2,'other_drill_hits_unchanged':sum((before&after).values()),'removed_segments':2,'added_segments':4,'ground_pour_adopted':False,'voltage_spacing_qualified':False,'fabrication_ready':False,'artifact_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/x for x in receipt['changed_paths']]+[D/'after.xml',D/'after-drc.json',D/'after.pdf']}}
    (D/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'},indent=2))

if __name__=='__main__':main()
