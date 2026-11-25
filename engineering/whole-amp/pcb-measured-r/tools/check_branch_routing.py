"""Check declared branch geometry, exact native preservation, drills and DRC."""
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

def verify(before, after, c):
    expected = copy.deepcopy(before)
    changes = {s['uuid']:s for s in c['segment_changes']}
    assert len(changes)==21 and len(c['added_arcs'])==14 and len(c['junctions'])==7
    for n in v.children(expected, 'segment'):
        if uid(n) not in changes: continue
        row = changes.pop(uid(n))
        assert float(v.field(n,'width')[1]) == row['width_mm'] == .3
        assert v.field(n,'net')[1] == json.dumps(row['net'])
        assert v.field(n,'layer')[1] == json.dumps(row['layer'])
        for k in ['start','end']:
            assert xy(n,k) == row['before'][k]
            v.field(n,k)[1:3] = list(map(str,row['after'][k]))
        # Only shorten a straight segment, without reversing or moving its line.
        old = sub(row['before']['end'],row['before']['start'])
        new = sub(row['after']['end'],row['after']['start'])
        assert abs(old[0]*new[1]-old[1]*new[0]) < 1e-7 and dot(old,new)>0
        assert abs(math.hypot(*old)-math.hypot(*new)-c['radius_mm']) < 1e-7
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
        assert abs(math.dist(p,center)-c['radius_mm'])<1e-7
        assert abs(dot(sub(p,center),sub(r,center)))<1e-7  # quarter circle
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

def main():
    cp=M/'branch-routing-contract.json';c=json.loads(cp.read_text())
    p=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/c['board']
    raw=baseline(c);a=v.parse(raw.decode());b=v.parse(p.read_text());verify(a,b,c)
    for name,change in [('narrowed arc',lambda n:v.field(n,'width').__setitem__(1,'0.2')),
                        ('wrong net',lambda n:v.field(n,'net').__setitem__(1,'"WRONG"')),
                        ('non-tangent arc',lambda n:v.field(n,'mid').__setitem__(1,'0'))]:
        bad=copy.deepcopy(b);change(v.children(bad,'arc')[-1])
        try:verify(a,bad,c)
        except AssertionError:pass
        else:raise AssertionError(name+' escaped')
    bad=copy.deepcopy(b);bad.remove(v.children(bad,'arc')[-1])
    try:verify(a,bad,c)
    except (AssertionError,KeyError):pass
    else:raise AssertionError('missing branch escaped')
    with tempfile.TemporaryDirectory(prefix='renegade-branches-') as td:
        t=Path(td);before=t/p.name;before.write_bytes(raw)
        d0=export(before,t/'before');d1=export(p,t/'after')
        for k in d0:assert read_hits(d0[k])==read_hits(d1[k])
    drcp=M/'review/branch-routing-drc.json'
    subprocess.run([CLI,'pcb','drc','--format','json','-o',str(drcp),str(p)],check=True,capture_output=True,timeout=90)
    d=json.loads(drcp.read_text());assert not d['violations'] and not d['unconnected_items'],d
    result=dict(passed=True,baseline_commit=c['baseline_commit'],changed_segments=21,added_arcs=14,
        tangent_quarter_circle_forks=7,trace_width_mm=.3,all_other_native_atoms_preserved=True,
        exported_drills_unchanged=True,drc_violations=0,unconnected_items=0,
        negative_controls_rejected=['narrowed arc','wrong net','non-tangent arc','missing branch'],
        current_capacity_qualified=False,all_board_corners_qualified=False,fabrication_ready=False,
        source_sha256={c['board']:hashlib.sha256(p.read_bytes()).hexdigest(),str(cp.relative_to(ROOT)):hashlib.sha256(cp.read_bytes()).hexdigest()})
    (M/'review/branch-routing-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
