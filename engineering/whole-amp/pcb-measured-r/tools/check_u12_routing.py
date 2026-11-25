"""Independent exact-delta, tangent, drill and native DRC checks for U12 repair."""
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

def verify(before, after, contract):
    expected = copy.deepcopy(before)
    changes = {x['uuid']: x for x in contract['segment_changes']}
    for node in v.children(expected, 'segment'):
        if uid(node) not in changes: continue
        row = changes.pop(uid(node))
        assert float(v.field(node, 'width')[1]) == row['width_mm'] == .3
        assert v.field(node, 'net')[1].strip('"') == row['net']
        for key in ['start', 'end']:
            assert xy(node, key) == row['before'][key]
            v.field(node, key)[1:3] = list(map(str, row['after'][key]))
        a, b = xy(node, 'start'), xy(node, 'end')
        dx, dy = abs(a[0]-b[0]), abs(a[1]-b[1])
        assert min(dx, dy) < 1e-7 or abs(dx-dy) < 1e-7
    assert not changes
    arcs = {uid(n): n for n in v.children(after, 'arc')}
    rows = []
    for spec in contract['added_arcs']:
        arc = arcs[spec['uuid']]
        assert v.field(arc, 'width')[1] == '0.3'
        assert v.field(arc, 'net')[1] == '"OUT_BUF"'
        assert v.field(arc, 'layer')[1] == '"F.Cu"'
        for key in ['start', 'mid', 'end']: assert xy(arc, key) == spec[key]
        # Solve circle from its three native points independently of declared center.
        a, b, c = [xy(arc, k) for k in ['start', 'mid', 'end']]
        u = [b[i]-a[i] for i in range(2)]; w = [c[i]-a[i] for i in range(2)]
        det = 2*(u[0]*w[1]-u[1]*w[0]); assert abs(det) > 1e-7
        uu, ww = sum(x*x for x in u), sum(x*x for x in w)
        center = [a[0]+(uu*w[1]-ww*u[1])/det, a[1]+(u[0]*ww-w[0]*uu)/det]
        radius = math.dist(a, center)
        assert abs(radius-1) < 1e-7
        assert abs(center[0]-a[0]) < 1e-7  # horizontal tangent at common fork
        assert abs(center[1]-c[1]) < 1e-7  # vertical tangent at branch end
        assert math.dist(center, spec['center']) < 1e-7
        expected.append(copy.deepcopy(arc))
        rows.append(dict(uuid=spec['uuid'],radius_mm=radius,horizontal_start_tangent=True,vertical_end_tangent=True))
    assert expected == after, 'Unexpected board atom or missing/extra route change'
    return rows

def verify_current(before, after, contract):
    """Validate the later branch repair before the historical U12-only delta."""
    from check_branch_routing import baseline, verify as verify_branches
    branch_path = M / 'branch-routing-contract.json'
    branch = json.loads(branch_path.read_text())
    branch_before = v.parse(baseline(branch).decode())
    verify_branches(branch_before, after, branch)
    return verify(before, branch_before, contract)

def main():
    contract_path = M / 'u12-routing-contract.json'; c = json.loads(contract_path.read_text())
    active = ROOT / c['board']; candidate = Path(sys.argv[1]) if len(sys.argv)>1 else active
    baseline = subprocess.check_output(['/usr/bin/git', 'show', c['baseline_commit']+':'+c['board']], cwd=ROOT)
    assert hashlib.sha256(baseline).hexdigest() == c['before_sha256']
    a, b = v.parse(baseline.decode()), v.parse(candidate.read_text())
    rows = verify_current(a, b, c)
    bad = copy.deepcopy(b); v.field(v.children(bad, 'arc')[-1], 'width')[1] = '0.2'
    try: verify_current(a, bad, c)
    except AssertionError: pass
    else: raise AssertionError('Narrowed arc negative control escaped')
    bad = copy.deepcopy(b); bad.remove(v.children(bad, 'arc')[-1])
    try: verify_current(a, bad, c)
    except (AssertionError, KeyError): pass
    else: raise AssertionError('Missing branch negative control escaped')
    with tempfile.TemporaryDirectory(prefix='renegade-u12-check-') as td:
        tmp = Path(td); before = tmp / active.name; before.write_bytes(baseline)
        d0 = export(before, tmp/'before-drills'); d1 = export(candidate, tmp/'after-drills')
        for key in d0: assert read_hits(d0[key]) == read_hits(d1[key])
    out = M / 'review/u12-routing-drc.json'
    subprocess.run([CLI,'pcb','drc','--format','json','-o',str(out),str(candidate)],check=True,capture_output=True,timeout=90)
    drc = json.loads(out.read_text()); assert not drc['violations'] and not drc['unconnected_items']
    result = dict(passed=True,baseline_commit=c['baseline_commit'],source_feedback='FB-119',
        changed_segments=len(c['segment_changes']),added_arcs=rows,all_other_board_atoms_preserved=True,
        preservation_scope='U12 delta plus separately verified exact seven-branch follow-up',
        exported_drills_unchanged=True,drc_violations=0,unconnected_items=0,
        negative_controls_rejected=['narrowed arc','missing branch'],
        all_board_corner_qualification=False,current_capacity_qualification=False,fabrication_ready=False,
        source_sha256={str(M.relative_to(ROOT)/'branch-routing-contract.json'):hashlib.sha256((M/'branch-routing-contract.json').read_bytes()).hexdigest(),
                       str(contract_path.relative_to(ROOT)):hashlib.sha256(contract_path.read_bytes()).hexdigest(),
                       c['board']:hashlib.sha256(candidate.read_bytes()).hexdigest()})
    (M/'review/u12-routing-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
