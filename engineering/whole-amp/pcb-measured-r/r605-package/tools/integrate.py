"""Guarded R605 package correction; no board regeneration or value change."""
from pathlib import Path
import copy
import hashlib
import json
import re
import sys
import uuid

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[3]
sys.path.insert(0, str(ROOT/'engineering/whole-amp/tools'))
import native_sexpr as n
sys.path.insert(0, str(ROOT/'engineering/whole-amp/reverb-600/interface-voltage/tools'))
from correct_metadata import spans

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def emit(x):
    return '('+' '.join(emit(y) if isinstance(y, list) else y for y in x)+')'

def props(obj):
    return {p[1].strip('"'):p for p in n.children(obj, 'property')}

def setprop(obj, key, value):
    pr = props(obj)
    if key not in pr:
        p = copy.deepcopy(pr['Datasheet'])
        p[1] = json.dumps(key)
        obj.append(p)
        pr[key] = p
    pr[key][2] = json.dumps(value)

def patch(text, kind, fn):
    for a,b in reversed(list(spans(text, kind))):
        obj = n.parse(text[a:b])
        replacement = fn(obj)
        if replacement is not None:
            text = text[:a]+(emit(replacement) if replacement else '')+text[b:]
    return text

def uid(tag):
    return json.dumps(str(uuid.uuid5(uuid.NAMESPACE_URL, 'renegade-r605-package/'+tag)))

def footprint(c):
    p=c['pitch_mm']; length=c['body_length_max_mm']; d=c['body_diameter_max_mm']
    left=(p-length)/2; right=(p+length)/2; pad=c['pad_diameter_mm']
    cx=pad/2+c['courtyard_margin_mm']; cy=d/2+c['courtyard_margin_mm']
    name=c['footprint'].split(':')[1]
    lines=[f'(footprint "{name}" (version 20241229) (generator "renegade_r605") (layer "F.Cu") (attr through_hole)',
           '(descr "FMP200 candidate; maximum body 9.5x4.2mm, round lead0.60mm; formed pitch15.24mm; provisional 3mm body standoff. Hot/fault qualification pending.")',
           '(tags "Yageo FMP200 axial flameproof 2W at70C")']
    for key,value,y,layer in [('Reference','REF**',-3.7,'F.SilkS'),('Value','FMP200',3.7,'F.Fab'),('Datasheet',c['datasheet'],0,'F.Fab')]:
        hide=' (hide yes)' if key=='Datasheet' else ''
        lines.append(f'(property "{key}" "{value}" (at {p/2} {y} 0) (layer "{layer}"){hide} (effects (font (size 1 1) (thickness .15))))')
    for layer,w in [('F.Fab',.1),('F.SilkS',.12)]:
        lines.append(f'(fp_rect (start {left} {-d/2}) (end {right} {d/2}) (stroke (width {w}) (type default)) (fill none) (layer "{layer}") (uuid {uid(layer+"body")}))')
        for a,b in [(pad/2+.25,left),(right,p-pad/2-.25)]:
            lines.append(f'(fp_line (start {a} 0) (end {b} 0) (stroke (width {w}) (type default)) (layer "{layer}") (uuid {uid(layer+str(a))}))')
    lines.append(f'(fp_rect (start {-cx} {-cy}) (end {p+cx} {cy}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd") (uuid {uid("court")}))')
    for pin,x in [('1',0),('2',p)]:
        lines.append(f'(pad "{pin}" thru_hole circle (at {x} 0) (size {pad} {pad}) (drill {c["drill_mm"]}) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid {uid(pin)}))')
    return '\n'.join(lines+[')'])+'\n'

def main():
    assert sys.argv[1:]==['--apply']
    c=json.loads((M/'contract.json').read_text())
    for path,h in c['input_sha256'].items():
        assert sha(ROOT/path)==h, 'Changed input: '+path
    changes={}
    lib=ROOT/'engineering/component-selection/footprints/Renegade_Selected.pretty'/(c['footprint'].split(':')[1]+'.kicad_mod')
    assert not lib.exists(), 'Already integrated or footprint name collision'
    geometry=footprint(c)
    changes[str(lib.relative_to(ROOT))]=geometry
    for path in list(c['input_sha256'])[:2]:
        data=json.loads((ROOT/path).read_text())
        row=next(x for x in data['components'] if x['reference']=='R605')
        assert row['value']=='220' and row['pins']==c['pins']
        row.update(footprint=c['footprint'], rating=c['rating'], datasheet=c['datasheet'],
                   package_candidate_mpn=c['mpn_candidate'],
                   package_evidence=str(M.relative_to(ROOT)/'review.md'))
        changes[path]=json.dumps(data,indent=2)+'\n'
    sch=list(c['input_sha256'])[2]
    def sch_edit(s):
        if props(s)['Reference'][2]!='"R605"': return
        for key,val in {'Footprint':c['footprint'],'Rating':c['rating'],'Datasheet':c['datasheet'],
                        'Package_candidate':c['mpn_candidate'],'Part_status':'Conditional package; sourcing, hot and fault qualification pending'}.items():
            setprop(s,key,val)
        return s
    changes[sch]=patch((ROOT/sch).read_text(),'symbol',sch_edit)
    board=list(c['input_sha256'])[3]
    original=(ROOT/board).read_text()
    def fp_edit(f):
        if props(f)['Reference'][2]!='"R605"':return
        oldpads={x[1]:x for x in n.children(f,'pad')}
        g=n.parse(geometry)
        kinds={'pad','fp_line','fp_rect','fp_text','model','descr','tags'}
        f[:]=[x for x in f if not(isinstance(x,list) and x[0] in kinds)]
        for x in g:
            if isinstance(x,list) and x[0] in kinds:
                if x[0]=='pad':
                    n.field(x,'uuid')[1]=n.field(oldpads[x[1]],'uuid')[1]
                    x.append(copy.deepcopy(n.field(oldpads[x[1]],'net')))
                f.append(x)
        f[1]=json.dumps(c['footprint'])
        n.field(f,'at')[1:]=list(map(str,c['board_at_mm']))
        for key in ['Reference','Value']:
            n.field(props(f)[key],'at')[1:]=n.field(props(g)[key],'at')[1:]
        for key,val in {'Rating':c['rating'],'Datasheet':c['datasheet'],'Package_candidate':c['mpn_candidate']}.items():setprop(f,key,val)
        return f
    text=patch(original,'footprint',fp_edit)
    removed=[];changed=[]
    def route_edit(s):
        net=n.field(s,'net')[1];id=n.field(s,'uuid')[1].strip('"')
        if net=='"DRIVE_CAP"':
            removed.append(id);return []
    text=patch(text,'segment',route_edit)
    assert len(removed)==3 and len(changed)==0
    added=[]
    for i,(a,b) in enumerate([((91,50),(91,41))]):
        added.append(n.parse(f'(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (width .3) (layer "F.Cu") (net "DRIVE_CAP") (uuid {uid("route"+str(i))}))'))
    for i,(a,b) in enumerate([((75.76,50),(78,47.76)),((78,47.76),(78,41))]):
        added.append(n.parse(f'(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (width .3) (layer "F.Cu") (net "DRIVER") (uuid {uid("driverextension"+str(i))}))'))
    added.append(n.parse(f'(via (at 78 41) (size .8) (drill .4) (layers "F.Cu" "B.Cu") (net "DRIVER") (uuid {uid("drivervia")}))'))
    end=text.rfind(')')
    changes[board]=re.sub(r'(?m)^[ \t]+$', '', text[:end]+'\n'+'\n'.join(map(emit,added))+'\n'+text[end:])
    for path,text in changes.items():
        if path.endswith(('.kicad_sch','.kicad_pcb','.kicad_mod')):n.parse(text)
        (ROOT/path).write_text(text)
    receipt={'after_sha256':{p:sha(ROOT/p) for p in changes},'changed_track_uuids':changed,'removed_track_uuids':removed,'added_track_uuids':[n.field(s,'uuid')[1].strip('"') for s in added if s[0]=='segment'],'added_via_uuid':uid('drivervia').strip('"'),'purchasing_qualified':False,'thermal_fault_qualified':False}
    (M/'results/integration.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('R605 conditional package integrated; checks required.')

if __name__=='__main__':main()
