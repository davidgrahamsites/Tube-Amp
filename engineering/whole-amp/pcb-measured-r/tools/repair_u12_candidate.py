"""Create a non-overwriting U12 routing candidate from an exact declared baseline."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[2]
sys.path.insert(0, str(M.parent / 'tools'))
import native_sexpr as v
from integrate_socket_footprints import spans
from integrate_drivers import emit

def transform(text, contract):
    changes = {x['uuid']: x for x in contract['segment_changes']}
    edits = []
    for start, end in spans(text, 'segment'):
        node = v.parse(text[start:end])
        uid = v.field(node, 'uuid')[1].strip('"')
        if uid not in changes:
            continue
        change = changes.pop(uid)
        assert v.field(node, 'net')[1].strip('"') == change['net']
        assert float(v.field(node, 'width')[1]) == change['width_mm']
        for key in ['start', 'end']:
            assert list(map(float, v.field(node, key)[1:3])) == change['before'][key]
            v.field(node, key)[1:3] = list(map(str, change['after'][key]))
        edits.append((start, end, emit(node)))
    assert not changes
    for start, end, replacement in reversed(edits):
        text = text[:start] + replacement + text[end:]
    arcs = []
    for a in contract['added_arcs']:
        node = ['arc', *[[k, *map(str, a[k])] for k in ['start', 'mid', 'end']],
                ['width', str(a['width_mm'])], ['layer', json.dumps(a['layer'])],
                ['net', json.dumps(a['net'])], ['uuid', json.dumps(a['uuid'])]]
        arcs.append(emit(node))
    pos = text.rfind(')')
    return text[:pos] + '\n' + '\n'.join(arcs) + '\n' + text[pos:]

def main():
    c = json.loads((M / 'u12-routing-contract.json').read_text())
    src = ROOT / c['board']
    assert hashlib.sha256(src.read_bytes()).hexdigest() == c['before_sha256']
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=False)
    (out / src.name).write_text(transform(src.read_text(), c))
    for ext in ['.kicad_pro', '.kicad_dru']:
        p = src.with_suffix(ext)
        if p.exists(): shutil.copyfile(p, out / p.name)
    table = (src.parent / 'fp-lib-table').read_text()
    table = table.replace('${KIPRJMOD}/../../../component-selection', str(ROOT / 'engineering/component-selection'))
    table = table.replace('${KIPRJMOD}/../../libraries', str(M.parent / 'libraries'))
    (out / 'fp-lib-table').write_text(table)
    print(out / src.name)

if __name__ == '__main__': main()
