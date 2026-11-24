"""Validate the bounded reset repair against its immutable native baseline.

Read-only with respect to CAD. Reports do not qualify the supervisor or chassis.
"""
import collections, copy, hashlib, json, math, subprocess, sys, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[2]
sys.path.insert(0, str(M.parent / 'tools'))
import native_sexpr as v
from check_drills import export, read_hits

CIR = 'engineering/whole-amp/reverb-600/circuit.json'
PCB = 'engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb'
SHEETS = ['engineering/whole-amp/reverb-600/cad/' + n + '.kicad_sch'
          for n in ['09b_latches_drivers', '10_logic_power']]

def old(path, base):
    return subprocess.check_output(['/usr/bin/git', 'show', base + ':' + path], cwd=ROOT).decode()

def graph(path):
    out = {}
    for net in ET.parse(path).findall('./nets/net'):
        for node in net.findall('node'):
            out[node.get('ref') + '.' + node.get('pin')] = net.get('name')
    return out

def pad_map(board):
    return {ref + '.' + p[1].strip('"'): v.field(p, 'net')[1].strip('"')
            for ref, f in v.fps(board).items() for p in v.children(f, 'pad')
            if v.children(p, 'net')}

def expected_map(before, contract):
    result = dict(before)
    for key, (prior, after) in contract['pin_changes'].items():
        assert result[key] == prior if prior is not None else result[key].startswith('unconnected-')
        result[key] = after
    return result

def route_check(board, added):
    # Nodes carry layers; plated pads and vias join layers, crossings do not.
    adjacency = collections.defaultdict(set)
    point = lambda p: tuple(round(float(t), 5) for t in p)
    def join(a, b):
        adjacency[a].add(b); adjacency[b].add(a)
    pads = {}
    for ref, f in v.fps(board).items():
        at = v.field(f, 'at'); x, y = map(float, at[1:3])
        angle = math.radians(float(at[3]) if len(at) > 3 else 0)
        for p in v.children(f, 'pad'):
            if not v.children(p, 'net'): continue
            net = v.field(p, 'net')[1].strip('"')
            px, py = map(float, v.field(p, 'at')[1:3])
            pos = point((x + px*math.cos(angle) + py*math.sin(angle),
                         y - px*math.sin(angle) + py*math.cos(angle)))
            layers = ['F.Cu', 'B.Cu'] if p[2] == 'thru_hole' else ['F.Cu']
            nodes = [(net, layer, pos) for layer in layers]
            pads[ref + '.' + p[1].strip('"')] = nodes
            for a in nodes:
                for b in nodes: join(a, b)
    for x in added:
        net = v.field(x, 'net')[1].strip('"')
        if x[0] == 'via':
            assert float(v.field(x, 'drill')[1]) == .4
            pos = point(v.field(x, 'at')[1:3])
            join((net, 'F.Cu', pos), (net, 'B.Cu', pos))
        else:
            a, b = [point(v.field(x, k)[1:3]) for k in ['start', 'end']]
            dx, dy = [abs(a[i]-b[i]) for i in range(2)]
            assert min(dx, dy) < 1e-7 or abs(dx-dy) < 1e-7
            assert float(v.field(x, 'width')[1]) >= .3
            layer = v.field(x, 'layer')[1].strip('"')
            join((net, layer, a), (net, layer, b))
    for start, finish in [('U3.1', 'R321.2'), ('R321.2', 'U1.5'),
                          ('U1.6', 'U1.9'), ('U1.8', 'U2.1'), ('U1.8', 'U2.13')]:
        pending = list(pads[start]); seen = set(pending)
        while pending:
            for p in adjacency[pending.pop()]:
                if p not in seen: seen.add(p); pending.append(p)
        assert any(p in seen for p in pads[finish]), (start, finish)

def main():
    c = json.loads((M/'edge-contract.json').read_text()); base = c['baseline_commit']
    checks = {}
    a = json.loads(old(CIR, base)); b = json.loads((ROOT/CIR).read_text())
    expected = copy.deepcopy(a)
    for comp in expected['components']:
        for pin in comp['pins']:
            key = comp['reference'] + '.' + pin
            if key in c['pin_changes']:
                before, after = c['pin_changes'][key]
                assert comp['pins'][pin] == before
                comp['pins'][pin] = after
        if comp['reference'] == 'U1' and comp['unit'] in [3, 4]:
            comp['sheet'] = '09b_latches_drivers'
    assert b == expected
    checks['source_only_six_pins_and_two_unit_sheet_moves'] = True
    before = graph(M/'results/edge-before.xml'); after = graph(M/'results/edge-after.xml')
    # The formerly local wire had an automatic export name; the board/source
    # already called this net RESET_N. Verify membership before normalizing.
    alias = 'Net-(U2A-~{R})'
    assert {k for k,n in before.items() if n == alias} == {'U3.1','R321.2','U2.1','U2.13'}
    before = {k: 'RESET_N' if n == alias else n for k,n in before.items()}
    assert after == expected_map(before, c)
    checks['native_export_matches_exact_pin_contract'] = True
    a = v.parse(old(PCB, base)); b = v.parse((ROOT/PCB).read_text())
    assert pad_map(b) == expected_map(pad_map(a), c)
    expected = copy.deepcopy(a)
    for ref, f in v.fps(expected).items():
        for p in v.children(f, 'pad'):
            key = ref + '.' + p[1].strip('"')
            if key in c['pin_changes']: v.field(p, 'net')[1] = json.dumps(c['pin_changes'][key][1])
    assert b[:len(expected)] == expected
    added = b[len(expected):]
    assert all(x[0] in ['segment', 'via'] for x in added)
    route_check(b, added)
    checks['all_old_geometry_and_copper_preserved'] = True
    checks['five_reset_links_layer_aware_connected_HV45_min_0p3mm'] = True
    for kind in ['erc', 'drc']:
        aa = json.loads((M/f'results/edge-before-{kind}.json').read_text())
        bb = json.loads((M/f'results/edge-after-{kind}.json').read_text())
        aa.pop('date', None); bb.pop('date', None)
        if kind == 'drc':
            assert aa['violations'] == bb['violations']
            assert len(aa['unconnected_items']) == 84 and len(bb['unconnected_items']) == 79
        else: assert aa == bb
        checks[kind + '_no_new_violations'] = True
    with tempfile.TemporaryDirectory(prefix='renegade-reset-drills-') as td:
        t = Path(td); p = t/'before.kicad_pcb'; p.write_text(old(PCB, base))
        aa, bb = export(p, t/'before'), export(ROOT/PCB, t/'after')
        p0, p1 = read_hits(aa['PTH']), read_hits(bb['PTH'])
        assert not p0-p1 and p1-p0 == collections.Counter({(27.717, -42.3, .4): 1})
        assert read_hits(aa['NPTH']) == read_hits(bb['NPTH'])
        slots = lambda s: [l for l in s.splitlines() if 'G85' in l or l.startswith(('G00','G01','M15','M16'))]
        assert all(slots(aa[k]) == slots(bb[k]) for k in aa)
    checks['native_drill_delta_only_one_0p4mm_via_slots_preserved'] = True
    rejected = []
    for name, bad in [('omitted_reset_link', [x for x in added if x != added[0]]),
                      ('wrong_via_drill', copy.deepcopy(added))]:
        if name == 'wrong_via_drill':
            v.field(next(x for x in bad if x[0]=='via'), 'drill')[1] = '0.2'
        try: route_check(b, bad)
        except AssertionError: rejected.append(name)
        else: raise AssertionError('Negative control escaped: '+name)
    wrong = copy.deepcopy(after); wrong['U1.8'] = 'RESET_INV'
    assert wrong != expected_map(before, c); rejected.append('wrong_reset_polarity_net')
    report = dict(passed=True, baseline_commit=base, checks=checks,
                  new_tracks=sum(x[0]=='segment' for x in added), new_vias=sum(x[0]=='via' for x in added),
                  negative_controls_rejected=rejected, control_unconnected_items=79,
                  control_existing_drc_violations=13, native_erc_existing_violations=1,
                  source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [CIR,PCB,*SHEETS]},
                  fabrication_ready=False)
    (M/'results/edge-native-checks.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
