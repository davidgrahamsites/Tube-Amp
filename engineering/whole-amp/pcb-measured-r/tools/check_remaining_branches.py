"""Independently verify the declared remaining-branch delta and native DRC."""
import copy
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

M = Path(__file__).resolve().parents[1]; ROOT = M.parents[2]
sys.path.insert(0, str(M.parent / 'tools'))
import native_sexpr as v
sys.path.insert(0, str(M.parent / 'control-switching/tools'))
from check_drills import export, read_hits, CLI

def xy(node, key): return list(map(float, v.field(node, key)[1:3]))
def uid(node): return v.field(node, 'uuid')[1].strip('"')
def dot(a, b): return sum(x*y for x,y in zip(a,b))
def sub(a, b): return [x-y for x,y in zip(a,b)]

def baseline(c):
    raw = subprocess.check_output(['/usr/bin/git','show',c['baseline_commit']+':'+c['board']],cwd=ROOT)
    assert hashlib.sha256(raw).hexdigest() == c['before_sha256']
    return raw

def verify_current(name, after):
    """Validate later routing before projecting to an earlier socket baseline."""
    c=json.loads((M/'remaining-branches-contract.json').read_text())
    row=dict(c['boards'][name],baseline_commit=c['baseline_commit'])
    before=v.parse(baseline(row).decode())
    verify(before,after,row)
    return before

def verify(before, after, c):
    expected = copy.deepcopy(before)
    changes = {s['uuid']:s for s in c['segment_changes']}
    assert len(changes)==3*len(c['junctions']) and len(c['added_arcs'])==2*len(c['junctions'])
    for n in v.children(expected, 'segment'):
        if uid(n) not in changes: continue
        row = changes.pop(uid(n))
        assert float(v.field(n,'width')[1]) == row['width_mm']
        assert v.field(n,'net')[1] == json.dumps(row['net'])
        assert v.field(n,'layer')[1] == json.dumps(row['layer'])
        for k in ['start','end']:
            assert xy(n,k) == row['before'][k]
            v.field(n,k)[1:3] = list(map(str,row['after'][k]))
        # Only shorten a straight segment, without reversing or moving its line.
        old = sub(row['before']['end'],row['before']['start'])
        new = sub(row['after']['end'],row['after']['start'])
        assert abs(old[0]*new[1]-old[1]*new[0]) < 1e-7 and dot(old,new)>0
        assert abs(math.hypot(*old)-math.hypot(*new)-row['setback_mm']) < 1e-7
    assert not changes
    arcs = {uid(a):a for a in v.children(after,'arc')}
    for spec in c['added_arcs']:
        a=arcs[spec['uuid']]
        declared=['arc',*[[k,*map(str,spec[k])] for k in ['start','mid','end']],
                  ['width',str(spec['width_mm'])],['layer',json.dumps(spec['layer'])],
                  ['net',json.dumps(spec['net'])],['uuid',json.dumps(spec['uuid'])]]
        assert a==declared, 'Arc geometry, width, net, layer or other atom differs'
        p,q,r=[xy(a,k) for k in ['start','mid','end']]
        u,w=sub(q,p),sub(r,p); det=2*(u[0]*w[1]-u[1]*w[0]); assert abs(det)>1e-8
        center=[p[0]+(dot(u,u)*w[1]-dot(w,w)*u[1])/det,
                p[1]+(u[0]*dot(w,w)-w[0]*dot(u,u))/det]
        assert math.dist(center,spec['center'])<1e-7
        assert abs(math.dist(p,center)-spec['radius_mm'])<1e-7
        cosine=dot(sub(p,center),sub(r,center))/(spec['radius_mm']**2)
        assert min(abs(cosine),abs(cosine-math.sqrt(.5)))<1e-6  # 90 or 45 degree sweep
        # Each endpoint joins a same-net/layer segment on a circle tangent.
        for point in [p,r]:
            matches=[]
            for s in v.children(expected,'segment'):
                if v.field(s,'net')!=v.field(a,'net') or v.field(s,'layer')!=v.field(a,'layer'): continue
                for k,other in [('start','end'),('end','start')]:
                    if xy(s,k)==point: matches.append(sub(xy(s,other),point))
            assert matches and all(abs(dot(d,sub(point,center)))<1e-7 for d in matches)
        expected.append(copy.deepcopy(a))
    for fork in c['junctions']:
        assert len(set(fork['arcs']))==2
        assert all(xy(arcs[k],'start')==fork['common_start'] for k in fork['arcs'])
    assert expected==after, 'Undeclared native change'

def open_nets(drc):
    import collections,re
    out=collections.Counter()
    for item in drc['unconnected_items']:
        nets={re.search(r'\[([^]]+)\]',i['description']).group(1) for i in item['items']}
        assert len(nets)==1
        out[next(iter(nets))]+=1
    return out


def main():
    cp=M/'remaining-branches-contract.json';contract=json.loads(cp.read_text())
    directory=Path(sys.argv[1]) if len(sys.argv)>1 else M/'boards'
    results={}
    with tempfile.TemporaryDirectory(prefix='renegade-remaining-branches-check-') as td:
        temp=Path(td)
        for name,c0 in contract['boards'].items():
            c=dict(c0,baseline_commit=contract['baseline_commit'])
            p=directory/Path(c['board']).name;raw=baseline(c)
            before=v.parse(raw.decode());after=v.parse(p.read_text());verify(before,after,c)
            rejected=[]
            for label,edit in [('narrowed arc',lambda a:v.field(a,'width').__setitem__(1,'0.1')),
                               ('wrong net',lambda a:v.field(a,'net').__setitem__(1,'"WRONG"')),
                               ('non-tangent arc',lambda a:v.field(a,'mid').__setitem__(1,'0'))]:
                bad=copy.deepcopy(after);edit(v.children(bad,'arc')[-1])
                try:verify(before,bad,c)
                except AssertionError:rejected.append(label)
                else:raise AssertionError(label+' escaped')
            bad=copy.deepcopy(after);bad.remove(v.children(bad,'arc')[-1])
            try:verify(before,bad,c)
            except (AssertionError,KeyError):rejected.append('missing branch')
            else:raise AssertionError('missing branch escaped')
            old=temp/name/p.name;old.parent.mkdir();old.write_bytes(raw)
            for ext in ['.kicad_pro','.kicad_dru']:
                active=M/'boards'/p.with_suffix(ext).name
                if active.exists():
                    old.with_suffix(ext).write_bytes(active.read_bytes())
                    assert p.with_suffix(ext).read_bytes()==active.read_bytes()
            table=(M/'boards/fp-lib-table').read_text().replace('${KIPRJMOD}/../../../component-selection',str(ROOT/'engineering/component-selection')).replace('${KIPRJMOD}/../../libraries',str(M.parent/'libraries'))
            (old.parent/'fp-lib-table').write_text(table)
            d0=export(old,temp/name/'drill-before');d1=export(p,temp/name/'drill-after')
            slots=lambda s:[l for l in s.splitlines() if 'G85' in l or l.startswith(('G00','G01','M15','M16'))]
            for kind in d0:
                assert read_hits(d0[kind])==read_hits(d1[kind])
                assert slots(d0[kind])==slots(d1[kind])
            drcs=[]
            for label,path in [('before',old),('after',p)]:
                output=M/'review'/f'remaining-branches-{name.lower()}-{label}-drc.json'
                subprocess.run([CLI,'pcb','drc','--format','json','-o',str(output),str(path)],check=True,capture_output=True,timeout=90)
                drcs.append(json.loads(output.read_text()))
            assert drcs[0]['violations']==drcs[1]['violations'],name+' changed violations'
            assert open_nets(drcs[0])==open_nets(drcs[1]),name+' changed open-net counts'
            results[name]=dict(changed_segments=len(c['segment_changes']),added_arcs=len(c['added_arcs']),
                preserved_other_native_atoms=True,widths_preserved=True,drills_and_slots_preserved=True,
                drc_violations=len(drcs[1]['violations']),unconnected_items=len(drcs[1]['unconnected_items']),
                no_new_drc_findings=True,negative_controls_rejected=rejected,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    report=dict(passed=True,baseline_commit=contract['baseline_commit'],boards=results,
        contract_sha256=hashlib.sha256(cp.read_bytes()).hexdigest(),
        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        current_capacity_qualified=False,all_corner_review_complete=False,fabrication_ready=False)
    (M/'review/remaining-branches-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
