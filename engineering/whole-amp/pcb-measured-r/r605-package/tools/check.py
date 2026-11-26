"""Independent native delta, topology, drill, raster and stress checks."""
import collections
import copy
import json
import math
import re
import subprocess
import xml.etree.ElementTree as ET
import pymupdf as fitz
from integrate import M, ROOT, n, sha, props

def baseline(path, c):
    return subprocess.check_output(['git','show',c['baseline_commit']+':'+path],cwd=ROOT)

def objects(tree, kind):
    return {n.field(x,'uuid')[1]:x for x in n.children(tree,kind)}

def drills(path):
    sizes={}; tool=None; result=collections.Counter()
    for line in path.read_text().splitlines():
        match=re.fullmatch(r'(T\d+)C([\d.]+)',line)
        if match:sizes[match[1]]=float(match[2])
        elif re.fullmatch(r'T\d+',line):tool=line
        elif line.startswith('X'):
            match=re.fullmatch(r'X(-?[\d.]+)Y(-?[\d.]+)',line)
            assert match, 'Unsupported drill/slot: '+line
            result[(sizes[tool],float(match[1]),float(match[2]))]+=1
    return result

def validate():
    c=json.loads((M/'contract.json').read_text());receipt=json.loads((M/'results/integration.json').read_text())
    for path,h in receipt['after_sha256'].items():assert sha(ROOT/path)==h,path
    for path,h in c['input_sha256'].items():
        import hashlib
        assert hashlib.sha256(baseline(path,c)).hexdigest()==h,path
    paths=list(c['input_sha256'])
    # Entire source documents must agree after removing just the declared metadata.
    allowed={'footprint','rating','datasheet','package_candidate_mpn','package_evidence'}
    for path in paths[:2]:
        before=json.loads(baseline(path,c));after=json.loads((ROOT/path).read_text())
        old=next(x for x in before['components'] if x['reference']=='R605')
        new=next(x for x in after['components'] if x['reference']=='R605')
        assert new['footprint']==c['footprint'] and new['pins']==c['pins']
        for key in allowed:
            new.pop(key,None);old.pop(key,None)
        assert before==after, 'Unexpected circuit change'
    before=n.parse(baseline(paths[2],c).decode());after=n.parse((ROOT/paths[2]).read_text())
    for tree in [before,after]:
        sym=next(s for s in n.children(tree,'symbol') if props(s)['Reference'][2]=='"R605"')
        sym[:]=[x for x in sym if not(isinstance(x,list) and x[0]=='property' and x[1].strip('"') in ['Footprint','Rating','Datasheet','Package_candidate','Part_status'])]
    assert before==after, 'Schematic wires or visible objects changed'
    before=n.parse(baseline(paths[3],c).decode());after=n.parse((ROOT/paths[3]).read_text())
    bfp=n.fps(before);afp=n.fps(after);assert set(bfp)==set(afp)
    for ref in bfp:
        if ref!='R605':assert bfp[ref]==afp[ref],ref
    f=afp['R605'];assert f[1].strip('"')==c['footprint']
    assert list(map(float,n.field(f,'at')[1:]))==c['board_at_mm']
    pads=n.children(f,'pad');assert len(pads)==2
    for p in pads:
        pin=p[1].strip('"');assert n.field(p,'net')[1].strip('"')==c['pins'][pin]
        assert float(n.field(p,'drill')[1])==c['drill_mm']
        assert list(map(float,n.field(p,'size')[1:]))==[c['pad_diameter_mm']]*2
    assert list(map(float,n.field(pads[1],'at')[1:]))==[c['pitch_mm'],0]
    for kind,removed,added in [('segment',receipt['removed_track_uuids'],receipt['added_track_uuids']),('via',[],[receipt['added_via_uuid']])]:
        a=objects(before,kind);b=objects(after,kind)
        assert set(a)-set(b)=={json.dumps(x) for x in removed}
        assert set(b)-set(a)=={json.dumps(x) for x in added}
        for key in set(a)&set(b):assert a[key]==b[key],key
    # Apart from the exact edited footprint/routes/via, board settings, mounts,
    # outline, graphics, layers and all other objects must remain identical.
    for tree in [before,after]:
        tree[:]=[x for x in tree if not(isinstance(x,list) and x[0] in ['footprint','segment','via'])]
    assert before==after
    bxml=ET.parse(M/'results/before.xml').getroot();axml=ET.parse(M/'results/after.xml').getroot()
    assert n.nets(bxml)==n.nets(axml)
    assert len(bxml.findall('./components/comp'))==len(axml.findall('./components/comp'))==240
    befored=drills(M/'results/drill-before/Renegade_Reverb.drl');afterd=drills(M/'results/drill-after/Renegade_Reverb.drl')
    assert befored-afterd==collections.Counter({(.8,78,-41):1,(.8,88.16,-41):1})
    assert afterd-befored==collections.Counter({(.9,75.76,-50):1,(.9,91,-50):1,(.4,78,-41):1})
    bd=json.loads((M/'results/before-drc.json').read_text());ad=json.loads((M/'results/after-drc.json').read_text())
    assert bd['ignored_checks']==ad['ignored_checks']
    assert not ad['violations'] and not ad['unconnected_items']
    be=json.loads((M/'results/before-erc.json').read_text());ae=json.loads((M/'results/after-erc.json').read_text())
    assert be['sheets']==ae['sheets']
    pdf1=fitz.open(M/'results/before.pdf');pdf2=fitz.open(M/'results/after.pdf')
    assert len(pdf1)==len(pdf2)
    assert all(a.get_pixmap().samples==b.get_pixmap().samples for a,b in zip(pdf1,pdf2)), 'Visible schematic changed'
    gap=c['drill_mm']-c['finished_hole_minus_tolerance_mm']-c['lead_diameter_max_mm']
    assert gap+1e-12>=c['diametral_assembly_allowance_mm']
    # Use worst absolute temperature departure across the full rated interval,
    # not ambient alone: self-heated film temperature is not established.
    rlow=c['nominal_R_ohm']*(1-c['initial_tolerance_fraction'])*(1-c['tcr_fraction_per_C']*(155-25))
    rows=[]
    for temp in c['local_ambient_screen_C']:
        permitted=c['power_W_at70C']*min(1,max(0,(c['derating_zero_C']-temp)/(c['derating_zero_C']-70)))
        for voltage in c['direct_voltage_screens_Vrms']:
            power=voltage**2/rlow
            rows.append(dict(ambient_C=temp,resistor_Vrms=voltage,applied_W=power,permitted_W=permitted,utilization=power/permitted,passes=power<=permitted))
    assert any(x['ambient_C']==100 and x['resistor_Vrms']==18 and not x['passes'] for x in rows)
    # Independent worst sine resonance load: low tank Rdc remains a screening assumption.
    normal=10**2*rlow/(2*(rlow+68.4)**2)
    out={'passed':True,'component_count':240,'net_count':len(n.nets(axml)),'unchanged_schematic_pages':len(pdf1),'unchanged_other_footprints':len(afp)-1,'before_drills':sum(befored.values()),'after_drills':sum(afterd.values()),'finished_hole_diametral_allowance_mm':gap,'maximum_candidate_height_with_provisional_standoff_mm':c['body_diameter_max_mm']+c['body_standoff_provisional_mm'],'R605_min_with_initial_and_full_range_TCR_ohm':rlow,'normal_10Vpeak_resonance_screen_W':normal,'direct_resistor_voltage_screens':rows,'reverb_drc_violations':0,'reverb_unconnected_items':0,'remaining_holds':['Sustained short/overload and hot cabinet qualification','Actual tank permitted current and impedance','Exact China stock and Shanghai checkout','Populated chassis and full drill envelope','Final fabrication tolerances and via ampacity'],'fabrication_ready':False,'input_sha256':receipt['after_sha256']}
    x,y=c['board_at_mm']; half=c['body_length_max_mm']/2; center=x+c['pitch_mm']/2
    envelope={'reference':'R605','frame':'Native Reverb board XY; z=0 at PCB top surface, positive away from PCB','body_AABB_min_mm':[center-half,y-c['body_diameter_max_mm']/2,c['body_standoff_provisional_mm']],'body_AABB_max_mm':[center+half,y+c['body_diameter_max_mm']/2,c['body_standoff_provisional_mm']+c['body_diameter_max_mm']],'footprint':c['footprint'],'board_sha256':sha(ROOT/paths[3]),'contract_sha256':sha(M/'contract.json'),'thermal_clearance_qualified':False,'standoff_status':'3mm engineering allocation; physical thermal/lead-form validation pending','scope':'Conservative cylindrical-body bounding box only; leads, solder and extraction envelope not a complete chassis model'}
    (M/'results/package-envelope.json').write_text(json.dumps(envelope,indent=2)+'\n')
    (M/'results/checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['input_sha256','direct_resistor_voltage_screens']},indent=2))

if __name__=='__main__':validate()
