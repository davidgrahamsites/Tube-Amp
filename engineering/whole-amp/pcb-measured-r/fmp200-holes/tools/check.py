"""Independent complete native-delta and Excellon audit for 26 FMP200 holes."""
import collections
import copy
import json
import math
import re
import subprocess
from integrate import M, ROOT, n, sha

def old(path,c):
    return subprocess.check_output(['git','show',c['baseline_commit']+':'+path],cwd=ROOT).decode()

def drill_hits(path):
    tools={};active=None;hits=collections.Counter()
    for line in path.read_text().splitlines():
        a=re.fullmatch(r'(T\d+)C([\d.]+)',line)
        if a:tools[a[1]]=float(a[2])
        elif re.fullmatch(r'T\d+',line):active=line
        elif line.startswith('X'):
            a=re.fullmatch(r'X(-?[\d.]+)Y(-?[\d.]+)',line)
            assert a, 'Unsupported drill shape: '+line
            hits[(tools[active],float(a[1]),float(a[2]))]+=1
    return hits

def undo_declared_delta(f, original):
    """Restore only allowed fields, then compare complete parsed objects."""
    original_pads={p[1]:p for p in n.children(original,'pad')}
    for p in n.children(f,'pad'):
        assert n.field(p,'drill')[1:]==['0.9']
        assert n.field(p,'size')[1:]==['1.8','1.8']
        n.field(p,'drill')[1:]=n.field(original_pads[p[1]],'drill')[1:]
        n.field(p,'size')[1:]=n.field(original_pads[p[1]],'size')[1:]
    courts=[x for x in n.children(f,'fp_rect') if n.field(x,'layer')[1]=='"F.CrtYd"']
    assert len(courts)==1
    oc=next(x for x in n.children(original,'fp_rect') if n.field(x,'layer')[1]=='"F.CrtYd"')
    assert [float(n.field(courts[0],k)[1]) for k in ['start','end']]==[-1.15,16.39]
    for key in ['start','end']:n.field(courts[0],key)[1]=n.field(oc,key)[1]
    original_lines={n.field(x,'uuid')[1]:x for x in n.children(original,'fp_line')}
    for line in n.children(f,'fp_line'):
        orig=original_lines[n.field(line,'uuid')[1]]
        if n.field(line,'layer')[1]=='"F.SilkS"' and n.field(line,'start')[1:] in [['1.15','0'],['14.09','0']]:
            n.field(line,'start')[1:]=n.field(orig,'start')[1:]
    assert '2W at70C' in n.field(f,'tags')[1] and '0.5W' not in n.field(f,'tags')[1]
    n.field(f,'tags')[1]=n.field(original,'tags')[1]
    assert f==original, 'Undeclared footprint change'

def main():
    c=json.loads((M/'contract.json').read_text());receipt=json.loads((M/'results/integration.json').read_text())
    assert sha(ROOT/c['datasheet_path'])==c['datasheet_sha256']
    for path,h in receipt['after_sha256'].items():assert sha(ROOT/path)==h,path
    lib=next(iter(c['input_sha256']))
    undo_declared_delta(n.parse((ROOT/lib).read_text()),n.parse(old(lib,c)))
    unchanged_sources=list((ROOT/'engineering/whole-amp/reverb-600/cad').glob('*.kicad_sch'))
    unchanged_sources += [ROOT/'engineering/whole-amp/reverb-600/circuit.json',ROOT/'engineering/whole-amp/reverb-600/cad/design-connectivity.json']
    unchanged_sources += [ROOT/f'engineering/whole-amp/pcb-measured-r/boards/Renegade_{name}.kicad_pcb' for name in ['Control','Reverb']]
    for path in unchanged_sources:assert path.read_text()==old(str(path.relative_to(ROOT)),c),str(path)
    reports={};envelopes=[]
    for path,refs in c['reference_groups'].items():
        before=n.parse(old(path,c));after=n.parse((ROOT/path).read_text());a=n.fps(before);b=n.fps(after)
        assert set(a)==set(b)
        removed=collections.Counter();added=collections.Counter()
        for ref in refs:
            f=b[ref];origin=list(map(float,n.field(f,'at')[1:]));assert len(origin)==2 or origin[2]==0, 'Rotated envelope requires transform'
            for pad in n.children(f,'pad'):
                px,py=map(float,n.field(pad,'at')[1:3]);x=round(origin[0]+px,4);y=-round(origin[1]+py,4)
                removed[(.8,x,y)]+=1;added[(.9,x,y)]+=1
            # Body maximum, relative to PCB top. Actual standoff is explicitly unknown.
            envelopes.append({'reference':ref,'board':path,'footprint':c['library_id'],'maximum_body_xy_mm':[9.5,4.2],
                              'body_center_xy_mm':[round(origin[0]+7.62,4),origin[1]],'body_diameter_max_mm':4.2,
                              'body_underside_standoff_mm':None,'installed_height_mm':None,
                              'source':c['datasheet_path'],'board_sha256':sha(ROOT/path),
                              'status':'Body dimensions known; thermal standoff and populated fit unresolved'})
            undo_declared_delta(f,a[ref])
        # All remaining board objects, positions, nets and routes are preserved.
        assert before==after, path
        name=path.split('/')[-1].split('.')[0]
        bd=M/'results/before'/name;ad=M/'results/after'/name
        drb=drill_hits(bd/(name+'.drl'));dra=drill_hits(ad/(name+'.drl'))
        assert drb-dra==removed and dra-drb==added, name
        d1=json.loads((bd/'drc.json').read_text());d2=json.loads((ad/'drc.json').read_text())
        for key in ['violations','unconnected_items','ignored_checks','schematic_parity']:
            assert d1[key]==d2[key], (name,key)
        reports[name]={'references':refs,'resized_holes':2*len(refs),'unchanged_drill_count':sum(dra.values()),
                       'existing_DRC_findings':len(d2['violations']),'existing_unconnected_items':len(d2['unconnected_items']),
                       'new_DRC_findings':0,'placement_and_connectivity_unchanged':True}
    gap=c['new_drill_mm']-c['finished_hole_tolerance_mm']-c['maximum_round_lead_mm']
    ring=(c['new_pad_mm']-(c['new_drill_mm']+c['finished_hole_tolerance_mm']))/2
    assert math.isclose(gap,.2) and math.isclose(ring,.4)
    result={'passed':True,'unchanged_source_files':len(unchanged_sources),'resistors':len(envelopes),'resized_holes':26,'finished_hole_min_mm':.8,'maximum_lead_mm':.6,
            'diametral_allowance_mm':gap,'annular_ring_before_registration_mm':ring,'boards':reports,
            'unchanged_scope':'All source schematic/circuit files, board placements, nets, tracks, vias, other footprints, mounts and outline',
            'fabrication_ready':False,'remaining_holds':['Actual supplier finished-hole/registration tolerances','Hot/pulse/fault resistor ratings','Assembly standoff and chassis fit','Existing unrouted connections and DRC findings'],
            'input_sha256':receipt['after_sha256']}
    (M/'results/checks.json').write_text(json.dumps(result,indent=2)+'\n')
    (M/'results/package-envelopes.json').write_text(json.dumps({'frame':'Native board XY in mm; z measured from PCB top','components':envelopes,'fabrication_ready':False},indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},indent=2))

if __name__=='__main__':main()
