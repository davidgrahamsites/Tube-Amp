"""Apply only the declared JR1/JR5 ratings and inaccurate board legend repair."""
from pathlib import Path
import hashlib
import json
import sys

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[3]
sys.path.insert(0, str(ROOT/'engineering/whole-amp/tools'))
import native_sexpr as v


def spans(text, kind):
    depth = 0; quoted = False; escape = False; start = None
    for i, ch in enumerate(text):
        if quoted:
            if escape: escape = False
            elif ch == '\\': escape = True
            elif ch == '"': quoted = False
        elif ch == '"': quoted = True
        elif ch == '(':
            if depth == 1 and text.startswith('('+kind, i) and text[i+len(kind)+1].isspace(): start = i
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 1 and start is not None:
                yield start, i+1
                start = None


def main():
    assert sys.argv[1:] == ['--apply']
    c = json.loads((M/'contract.json').read_text()); m = c['metadata']
    for p,h in c['native_sha256'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p
    changes = {}
    for path in ['engineering/whole-amp/reverb-600/circuit.json',
                 'engineering/whole-amp/reverb-600/cad/design-connectivity.json']:
        data = json.loads((ROOT/path).read_text()); seen = set()
        for row in data['components']:
            if row['reference'] in m['references']:
                assert row['rating'] == m['old_rating']
                row['rating'] = m['new_rating']; seen.add(row['reference'])
        assert seen == set(m['references'])
        changes[path] = json.dumps(data, indent=2)+'\n'
    target = ROOT/'engineering/whole-amp/pcb-measured-r/boards/Renegade_Reverb.kicad_pcb'
    for path in [*(M.parent/'cad').glob('*.kicad_sch'), target]:
        text = path.read_text(); edits = []
        for a,b in spans(text, 'footprint' if path == target else 'symbol'):
            obj = v.parse(text[a:b]); props = {p[1].strip('"'):p for p in v.children(obj,'property')}
            if props['Reference'][2].strip('"') not in m['references']: continue
            assert props['Rating'][2] == json.dumps(m['old_rating'])
            old = text[a:b]; needle = '"Rating" '+json.dumps(m['old_rating'])
            assert old.count(needle) == 1
            edits.append((a,b,old.replace(needle, '"Rating" '+json.dumps(m['new_rating']))))
        for a,b,new in reversed(edits): text = text[:a]+new+text[b:]
        if path == target:
            assert text.count(json.dumps(m['old_silk'])) == 1
            text = text.replace(json.dumps(m['old_silk']), json.dumps(m['new_silk']))
        if text != path.read_text():
            v.parse(text); changes[str(path.relative_to(ROOT))] = text
    factory = ROOT/c['legacy_factory']
    text = factory.read_text(); assert text.count(m['old_silk']) == 1
    changes[c['legacy_factory']] = text.replace(m['old_silk'],m['new_silk'])
    assert len(changes) == 6, changes.keys()
    for p,t in changes.items(): (ROOT/p).write_text(t)
    (M/'results/integration.json').write_text(json.dumps({
        'changed_paths': list(changes), 'after_sha256': {p:hashlib.sha256(t.encode()).hexdigest() for p,t in changes.items()},
        'electrical_change':False, 'copper_or_drill_change':False, 'fabrication_ready':False
    },indent=2)+'\n')
    print('Corrected two connector ratings in source, native sheets/board and derived connectivity; removed LV board legend.')


if __name__ == '__main__': main()
