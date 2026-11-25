"""Non-overwriting candidate factory for the declared reverb branch repair."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
from repair_u12_candidate import transform

M = Path(__file__).resolve().parents[1]
ROOT = M.parents[2]

def main():
    c = json.loads((M / 'branch-routing-contract.json').read_text())
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
