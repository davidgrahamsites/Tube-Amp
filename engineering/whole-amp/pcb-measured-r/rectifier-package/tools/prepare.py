"""Generate a non-overwriting, baseline-guarded rectifier package candidate."""
import copy
import hashlib
import json
import sys
import uuid
import shutil
from pathlib import Path

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[3]
sys.path.insert(0, str(ROOT/'engineering/whole-amp/tools'))
import native_sexpr as n
sys.path.insert(0, str(ROOT/'engineering/whole-amp/reverb-600/interface-voltage/tools'))
from correct_metadata import spans

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(x): return '('+' '.join(emit(y) if isinstance(y,list) else y for y in x)+')'
def props(x): return {p[1].strip('"'):p for p in n.children(x,'property')}
def uid(tag): return json.dumps(str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade-by255/'+tag)))

def setprop(obj,key,value):
    pr=props(obj)
    if key not in pr:
        p=copy.deepcopy(pr['Datasheet']);p[1]=json.dumps(key);obj.append(p);pr[key]=p
    pr[key][2]=json.dumps(value)

def patch(text,kind,fn):
    for a,b in reversed(list(spans(text,kind))):
        replacement=fn(n.parse(text[a:b]))
        if replacement is not None:text=text[:a]+(emit(replacement) if replacement else '')+text[b:]
    return text

def footprint(c):
    p=c['pitch_mm'];d=c['body_diameter_max_mm'];l=c['body_length_max_mm']
    left=(p-l)/2;right=(p+l)/2
    lines=[f'(footprint "{c["footprint"].split(":")[1]}" (version 20241229) (generator "renegade_rectifier") (layer "F.Cu") (attr through_hole)',
           '(descr "Vishay BY255P DO-201AD maximum body9.5x5.3mm, round lead1.32mm; formed pitch30.48mm. Full thermal/voltage qualification pending.")']
    for key,value,y,layer in [('Reference','REF**',-4,'F.SilkS'),('Value','BY255P',4,'F.Fab'),('Datasheet',c['datasheet'],0,'F.Fab')]:
        hide=' (hide yes)' if key=='Datasheet' else ''
        lines.append(f'(property "{key}" "{value}" (at {p/2} {y} 0) (layer "{layer}"){hide} (effects (font (size 1 1) (thickness .15))))')
    for layer,w in [('F.Fab',.1),('F.SilkS',.12)]:
        lines.append(f'(fp_rect (start {left} {-d/2}) (end {right} {d/2}) (stroke (width {w}) (type default)) (fill none) (layer "{layer}") (uuid {uid(layer+"body")}))')
        for a,b in [(1.6,left),(right,p-1.6)]:
            lines.append(f'(fp_line (start {a} 0) (end {b} 0) (stroke (width {w}) (type default)) (layer "{layer}") (uuid {uid(layer+str(a))}))')
        lines.append(f'(fp_line (start {left+1} {-d/2}) (end {left+1} {d/2}) (stroke (width {w}) (type default)) (layer "{layer}") (uuid {uid(layer+"cathode")}))')
    lines.append(f'(fp_rect (start -1.8 -3.15) (end {p+1.8} 3.15) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd") (uuid {uid("court")}))')
    for pin,x,shape in [('1',0,'rect'),('2',p,'circle')]:
        lines.append(f'(pad "{pin}" thru_hole {shape} (at {x} 0) (size {c["pad_mm"]} {c["pad_mm"]}) (drill {c["drill_mm"]}) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid {uid(pin)}))')
    return '\n'.join(lines+[')'])+'\n'

def main():
    out=Path(sys.argv[1]);assert not out.exists(),'Use a new candidate directory'
    c=json.loads((M/'contract.json').read_text());refs=set(c['references'])
    for p,h in c['input_sha256'].items():assert sha(ROOT/p)==h,p
    assert sha(ROOT/c['datasheet_path'])==c['datasheet_sha256']
    geom=footprint(c);changes={}
    lib='engineering/component-selection/footprints/Renegade_Selected.pretty/'+c['footprint'].split(':')[1]+'.kicad_mod'
    assert not (ROOT/lib).exists();changes[lib]=geom
    paths=list(c['input_sha256'])
    rating='1300V; 3A only under specified lead/thermal conditions; charging pulse, hot and transient qualification pending'
    fields={'value':c['display_value'],'selected_mpn':c['mpn'],'footprint':c['footprint'],'datasheet':c['datasheet'],'rating':rating,'selection_evidence':'engineering/component-selection/rectifier-selection.md','status':'selected identity integrated; system qualification pending'}
    for p in paths[:2]:
        data=json.loads((ROOT/p).read_text());seen=set()
        for row in data['components']:
            if row['reference'] in refs:
                assert row['value']=='1N4007';row.update(fields);seen.add(row['reference'])
        assert seen==refs;changes[p]=json.dumps(data,indent=2)+'\n'
    def sch_edit(s):
        if props(s)['Reference'][2].strip('"') not in refs:return
        for key,val in {'Value':c['display_value'],'Selected_MPN':c['mpn'],'Footprint':c['footprint'],'Datasheet':c['datasheet'],'Rating':rating}.items():setprop(s,key,val)
        return s
    changes[paths[2]]=patch((ROOT/paths[2]).read_text(),'symbol',sch_edit)
    def fp_edit(f):
        ref=props(f)['Reference'][2].strip('"')
        if ref in c.get('supporting_moves',{}):
            n.field(f,'at')[1:]=list(map(str,c['supporting_moves'][ref]));return f
        if ref not in refs:return
        oldpads={x[1]:x for x in n.children(f,'pad')};g=n.parse(geom)
        kinds={'pad','fp_line','fp_rect','fp_text','model','descr','tags'}
        f[:]=[x for x in f if not(isinstance(x,list) and x[0] in kinds)]
        for x in g:
            if isinstance(x,list) and x[0] in kinds:
                if n.children(x,'uuid'):n.field(x,'uuid')[1]=uid(ref+emit(x))
                if x[0]=='pad':
                    n.field(x,'uuid')[1]=n.field(oldpads[x[1]],'uuid')[1]
                    n.field(x,'at')[1:]=[n.field(x,'at')[1],'0',str(c['placements'][ref][2])]
                    x.append(copy.deepcopy(n.field(oldpads[x[1]],'net')))
                f.append(x)
        f[1]=json.dumps(c['footprint']);n.field(f,'at')[1:]=list(map(str,c['placements'][ref]))
        for key in ['Reference','Value']:n.field(props(f)[key],'at')[1:]=n.field(props(g)[key],'at')[1:]
        for key,val in {'Value':c['display_value'],'Selected_MPN':c['mpn'],'Datasheet':c['datasheet'],'Rating':rating}.items():setprop(f,key,val)
        return f
    text=patch((ROOT/paths[3]).read_text(),'footprint',fp_edit)
    removed=[]
    def remove(s):
        if n.field(s,'net')[1].strip('"') in c['nets']:
            removed.append(n.field(s,'uuid')[1]);return []
    for kind in ['segment','arc']:text=patch(text,kind,remove)
    additions=[]
    for i,(net,layer,points) in enumerate(c['routes']):
        for j,(a,b) in enumerate(zip(points,points[1:])):
            additions.append(f'(segment (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (width {c["route_width_mm"]}) (layer "{layer}") (net "{net}") (uuid {uid(str(i)+"-"+str(j))}))')
    end=text.rfind(')');changes[paths[3]]=text[:end]+'\n'+'\n'.join(additions)+'\n'+text[end:]
    for p,t in changes.items():
        if not p.endswith('.json'):n.parse(t)
        target=out/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(t)
    # Give native CLI checks the same project rules and libraries as the source.
    boarddir=Path(paths[3]).parent
    for name in ['Renegade_Power.kicad_pro','Renegade_Power.kicad_dru','fp-lib-table']:
        if (ROOT/boarddir/name).exists():shutil.copyfile(ROOT/boarddir/name,out/boarddir/name)
    for libdir in ['engineering/whole-amp/libraries/Renegade_Whole.pretty','engineering/component-selection/footprints/Renegade_Selected.pretty']:
        dest=out/libdir;dest.mkdir(parents=True,exist_ok=True)
        for f in (ROOT/libdir).iterdir():
            if not (dest/f.name).exists():(dest/f.name).symlink_to(f)
    schdir=Path(paths[2]).parent
    for f in (ROOT/schdir).iterdir():
        if not (out/schdir/f.name).exists():(out/schdir/f.name).symlink_to(f,target_is_directory=f.is_dir())
    receipt={'changed_paths':list(changes),'removed_track_uuids':removed,'after_sha256':{p:sha(out/p) for p in changes},'fabrication_ready':False}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Prepared four rectifier packages and',len(additions),'local tracks; native validation required.')

if __name__=='__main__':main()
