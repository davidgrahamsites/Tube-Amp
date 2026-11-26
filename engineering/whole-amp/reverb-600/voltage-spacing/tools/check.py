"""Verify a conditional spacing review against native files and retained stress evidence."""
from pathlib import Path
from collections import Counter
import copy
import hashlib
import json
import subprocess
import sys

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[3]
sys.path.insert(0, str(ROOT/'engineering/whole-amp/tools'))
from native_sexpr import parse, children, field, fps


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(c, run, rules):
    assert set(c['nets']) == {'FX_RETURN', 'IN_AC', 'MIX_OUT', 'WET_AC'}
    assert not c['adoption_allowed'] and not run['adopted']
    assert c['screen']['clearance_mm'] == 2.5 and c['screen']['creepage_mm'] == 4.0
    for path, digest in c['native_sha256'].items():
        assert sha(ROOT/path) == digest, path
    for path, digest in run['input_sha256'].items():
        assert sha(M/path) == digest, path
    for path, digest in run['report_sha256'].items():
        assert sha(M/path) == digest, path
    assert '(constraint clearance (min 2.5mm))' in rules
    assert '(constraint creepage (min 4.0mm))' in rules
    for net in c['nets']:
        for operand in ['A', 'B']:
            assert f"{operand}.NetName == '{net}'" in rules


def main():
    c = json.loads((M/'contract.json').read_text())
    run = json.loads((M/'results/run.json').read_text())
    rules = (M/'results/candidate.kicad_dru').read_text()
    validate(c, run, rules)
    negatives = []
    for label in ['missing net', 'weakened clearance', 'stale native', 'missing rule operand']:
        bad = copy.deepcopy(c); text = rules
        if label == 'missing net': bad['nets'].remove('WET_AC')
        elif label == 'weakened clearance': bad['screen']['clearance_mm'] = .25
        elif label == 'stale native': bad['native_sha256'][c['target']] = '0'*64
        else: text = text.replace("B.NetName == 'WET_AC'", 'false')
        try:
            validate(bad, run, text)
        except AssertionError:
            negatives.append(label)
        else:
            raise AssertionError('Negative control escaped: '+label)

    circuit_path = 'engineering/whole-amp/reverb-600/circuit.json'
    old_bytes = subprocess.check_output(['git', 'show', '70b20d1:'+circuit_path], cwd=ROOT)
    stress_path = M.parent/'interface-voltage/results/stress.json'
    stress = json.loads(stress_path.read_text())
    historical_stress = subprocess.check_output(
        ['git', 'show', '70b20d1:'+str(stress_path.relative_to(ROOT))], cwd=ROOT)
    assert historical_stress == stress_path.read_bytes(), 'Retained evidence changed'
    for path, digest in stress['input_sha256'].items():
        if path != circuit_path:
            assert sha(ROOT/path) == digest, path
    assert hashlib.sha256(old_bytes).hexdigest() == stress['input_sha256'][circuit_path]
    old = json.loads(old_bytes)['components']
    current = json.loads((ROOT/circuit_path).read_text())['components']
    refs = ['R7', 'R43', 'C6', 'C601', 'R601', 'R602', 'R612', 'R616',
            'C607', 'R617', 'R618', 'R24', 'K3', 'JR1', 'JR5']
    def electrical(rows):
        return sorted((r['reference'], r['unit'], r['value'], sorted(r['pins'].items()))
                      for r in rows if r['reference'] in refs)
    assert electrical(old) == electrical(current), 'Retained fixture topology changed'
    # Independent DC reduction, using current native resistor values.
    parts = {r['reference']:r for r in current}
    def ohm(ref):
        value = parts[ref]['value']
        return float(value[:-1])*{'k':1000, 'M':1000000}[value[-1]]
    mixload = 1/(1/ohm('R24') + 1/(ohm('R618')+ohm('R617')))
    fxload = 1/(1/ohm('R43') + 1/(ohm('R612')+mixload))
    dc_error = 0
    for row in stress['dc_c6_short']:
        fx = row['supply_V']*fxload/(ohm('R7')+fxload)
        mix = fx*mixload/(ohm('R612')+mixload)
        wet = mix*ohm('R617')/(ohm('R618')+ohm('R617'))
        dc_error = max(dc_error, *(abs(row['nodes_V'][n]-v) for n,v in
                                  [('FX_RETURN',fx),('MIX_OUT',mix),('WET_AC',wet)]))
    assert dc_error < 1e-5

    board = parse((ROOT/c['target']).read_text()); footprints = fps(board)
    geometry = {}
    for ref, numbers in [('JR1', ['1','2']), ('JR5', ['1','2']), ('K3', ['13','11'])]:
        pads = {p[1].strip('"'):p for p in children(footprints[ref], 'pad')}
        a,b = [pads[n] for n in numbers]
        ax,ay = map(float, field(a,'at')[1:3]); bx,by = map(float,field(b,'at')[1:3])
        assert ax == bx, 'This independent formula requires vertically aligned pads'
        sizes = [list(map(float,field(p,'size')[1:3])) for p in [a,b]]
        assert all(x==y for x,y in sizes), 'Formula assumes equal X/Y pad sizes'
        gap = abs(ay-by) - (sizes[0][1]+sizes[1][1])/2
        geometry[ref] = dict(pads=numbers,center_spacing_mm=abs(ay-by),
                             copper_gap_mm=round(gap,6),
                             meaning='Planar copper edge gap; component body insulation is separate')
    assert geometry['JR1']['copper_gap_mm'] == geometry['JR5']['copper_gap_mm'] == .84
    assert geometry['K3']['copper_gap_mm'] == 3.28

    base = json.loads((M/'results/baseline-drc.json').read_text())
    candidate = json.loads((M/'results/candidate-drc.json').read_text())
    assert not base['violations'] and not base['unconnected_items']
    assert not candidate['unconnected_items']
    violations = candidate['violations']
    counts = dict(Counter(v['type'] for v in violations))
    assert counts == {'creepage':22, 'clearance':72}
    pairs = {(v['type'],tuple(sorted(i['uuid'] for i in v['items']))) for v in violations}
    pad_pairs = [v for v in violations if all('pad ' in i['description'] for i in v['items'])]
    out = dict(passed=True,negative_controls=negatives,retained_fixture_commit='70b20d1',
               unchanged_electrical_references=refs,dc_max_error_V=dc_error,
               stress_sha256=sha(stress_path),geometry=geometry,drc_counts=counts,
               unique_typed_item_pairs=len(pairs),pad_only_reports=len(pad_pairs),
               other_reports=len(violations)-len(pad_pairs),
               dc_fault_peak_V={n:max(abs(r['nodes_V'][n]) for r in stress['dc_c6_short'])
                                for n in ['FX_RETURN','MIX_OUT','WET_AC']},
               limits=['Conditional old passive fixture re-bound, not new whole-amp simulation',
                       'K3 open contact; fault-time switching and actual source envelope unqualified',
                       'DRC reports may repeat a physical constraint; counts are not unique defects',
                       'New loop and protection integration will require fresh voltage evidence'],
               native_unchanged=True,release_ready=False,
               checker_sha256=sha(Path(__file__)))
    (M/'results/checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__ == '__main__':
    main()
