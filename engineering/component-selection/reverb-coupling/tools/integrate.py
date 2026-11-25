"""Adopt one voltage-rated capacitor and reroute only its moved pad escape."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import uuid

M=Path(__file__).resolve().parents[1]; ROOT=M.parents[2]
sys.path.insert(0,str(ROOT/'engineering/whole-amp/tools')); import native_sexpr as n
sys.path.insert(0,str(ROOT/'engineering/whole-amp/reverb-600/interface-voltage/tools')); from correct_metadata import spans
Q=json.dumps
def emit(x): return '('+' '.join(emit(y) if isinstance(y,list) else y for y in x)+')'
def props(x): return {p[1].strip('"'):p for p in n.children(x,'property')}
def uid(tag): return Q(str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade-c607-450V/'+tag)))


def main():
    assert sys.argv[1:]==['--apply']
    c=json.loads((M/'contract.json').read_text())
    for p,h in c['native_sha256'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    fp=c['footprint']; rating='450VDC polypropylene; exact MPP105J2W10KN22605; system fault/thermal qualification pending'
    changes={}; evidence='engineering/component-selection/reverb-coupling/review.md'
    for p in ['engineering/whole-amp/reverb-600/circuit.json','engineering/whole-amp/reverb-600/cad/design-connectivity.json']:
        data=json.loads((ROOT/p).read_text()); rows=[x for x in data['components'] if x['reference']=='C607']; assert len(rows)==1
        x=rows[0]; assert x['value']=='1u' and x['pins']=={'1':'OUT_AC','2':'WET_AC'}
        x.update(footprint=fp,selected_mpn=c['mpn'],rating=rating,datasheet=c['datasheet'],selection_evidence=evidence,
                 selection_status='adopted voltage-rated coupling capacitor; system qualification pending')
        changes[p]=json.dumps(data,indent=2)+'\n'
    p='engineering/whole-amp/reverb-600/cad/07c_reverb_output.kicad_sch'; text=(ROOT/p).read_text(); found=0
    for a,b in spans(text,'symbol'):
        s=n.parse(text[a:b]); pr=props(s)
        if pr['Reference'][2]!='"C607"':continue
        for key,value in {'Footprint':fp,'Rating':rating,'Datasheet':c['datasheet'],'Selected_MPN':c['mpn'],
                          'Selection_evidence':'VAL-062; voltage-rated C607, system qualification pending'}.items():
            assert key in pr,key; pr[key][2]=Q(value); assert 'hide' in n.field(pr[key],'effects')
        text=text[:a]+emit(s)+text[b:]; found+=1; break
    assert found==1; changes[p]=text
    p='engineering/whole-amp/pcb-measured-r/boards/Renegade_Reverb.kicad_pcb'; text=(ROOT/p).read_text()
    for a,b in spans(text,'footprint'):
        f=n.parse(text[a:b]); pr=props(f)
        if pr['Reference'][2]!='"C607"':continue
        f[1]=Q(fp); n.field(f,'at')[1:]=list(map(str,c['mount']['origin_mm']))
        n.field(f,'descr')[1]=Q('MPP105J2W10KN22605; 1uF 450VDC; maximum body13 x8.1 xH16.4mm; pitch10+/-0.5mm; round leads0.6+/-0.05mm; hand-form pitch before insertion.')
        n.field(f,'tags')[1]=Q('KNSCHA CBB22 1uF 450V P10')
        pr['Selected_MPN'][2]=Q(c['mpn']); pr['Datasheet'][2]=Q(c['datasheet'])
        n.field(pr['Reference'],'at')[1:]=['5','-5.3','0']; n.field(pr['Value'],'at')[1:]=['5','5.3','0']
        for key,value in {'Rating':rating,'Package_Status':'Exact manufacturer max-body envelope; finished-hole tolerance and hand-forming to verify'}.items():
            if key not in pr:
                field=copy.deepcopy(pr['Status']); field[1]=Q(key); n.field(field,'uuid')[1]=uid(key); f.append(field); pr[key]=field
            pr[key][2]=Q(value)
        f=[x for x in f if not (isinstance(x,list) and x[0] in ['fp_line','fp_rect','fp_text','model'])]
        for layer,box,width in [('F.Fab',[-1,-3.55,11,3.55],.1),('F.SilkS',[-1.12,-3.67,11.12,3.67],.12),('F.CrtYd',[-1.75,-4.3,11.75,4.3],.05)]:
            x1,y1,x2,y2=box
            f.append(n.parse(f'(fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width {width}) (type default)) (fill no) (layer "{layer}") (uuid {uid(layer)}))'))
        for pad in n.children(f,'pad'):
            n.field(pad,'at')[1:]=['0' if pad[1]=='"1"' else '10','0']
            n.field(pad,'size')[1:]=['1.9','1.9']; n.field(pad,'drill')[1]='1.0'
        # Export a clean reusable library footprint from this exact geometry.
        lib=copy.deepcopy(f);lib[1]=Q(fp.split(':')[1]);lib.insert(2,['version','20241229']);lib.insert(3,['generator','"renegade"'])
        lib=[x for x in lib if not(isinstance(x,list) and x[0] in ['uuid','at','path','embedded_fonts'])]
        lp=props(lib);lp['Reference'][2]='"REF**"';lp['Value'][2]=Q(c['mpn'])
        for obj in lib:
            if isinstance(obj,list): obj[:]=[x for x in obj if not(isinstance(x,list) and x[0] in ['uuid','net'])]
        changes['engineering/component-selection/footprints/Renegade_Selected.pretty/'+fp.split(':')[1]+'.kicad_mod']=emit(lib)+'\n'
        text=text[:a]+emit(f)+text[b:];break
    else:raise AssertionError('C607 footprint missing')
    # Exact existing segment substitution. Other track/arc UUIDs remain byte-preserved.
    for route in c['routes']:
        for a,b in spans(text,'segment'):
            s=n.parse(text[a:b])
            if n.field(s,'uuid')[1].strip('"')!=route['old_segment_uuid']: continue
            assert n.field(s,'net')[1]==Q(route['net']) and n.field(s,'layer')[1]=='"F.Cu"'
            replacement=[]
            for i,(start,end) in enumerate(zip(route['new_points_mm'],route['new_points_mm'][1:])):
                t=copy.deepcopy(s);n.field(t,'start')[1:]=list(map(str,start));n.field(t,'end')[1:]=list(map(str,end))
                n.field(t,'uuid')[1]=uid(route['net']+'-escape-'+str(i));replacement.append(emit(t))
            text=text[:a]+'\n'.join(replacement)+text[b:];break
        else:raise AssertionError('C607 escape missing')
    n.parse(text);changes[p]=text
    for p,text in changes.items():(ROOT/p).write_text(text)
    (M/'results/integration.json').write_text(json.dumps({'changed_paths':list(changes),'after_sha256':{p:hashlib.sha256(t.encode()).hexdigest() for p,t in changes.items()},
          'component_value_changed':False,'pin_nets_changed':False,'changed_drill_count':2,'moved_pad_count':2,
          'removed_segments':2,'added_segments':4,'fabrication_ready':False},indent=2)+'\n')
    print('Adopted C607 1uF/450V, 10mm footprint, two 1mm holes and local 45-degree escape.')


if __name__=='__main__':main()
