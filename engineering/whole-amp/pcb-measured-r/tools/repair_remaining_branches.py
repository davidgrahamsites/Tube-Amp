"""Generate a fresh candidate for the declared Power/Control branch repairs."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
from repair_u12_candidate import transform, M, ROOT


def main():
    contract=json.loads((M/'remaining-branches-contract.json').read_text())
    out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
    for c in contract['boards'].values():
        src=ROOT/c['board']
        assert hashlib.sha256(src.read_bytes()).hexdigest()==c['before_sha256']
        (out/src.name).write_text(transform(src.read_text(),c))
        for ext in ['.kicad_pro','.kicad_dru']:
            p=src.with_suffix(ext)
            if p.exists():shutil.copyfile(p,out/p.name)
    table=(src.parent/'fp-lib-table').read_text()
    table=table.replace('${KIPRJMOD}/../../../component-selection',str(ROOT/'engineering/component-selection'))
    table=table.replace('${KIPRJMOD}/../../libraries',str(M.parent/'libraries'))
    (out/'fp-lib-table').write_text(table)
    print(out)


if __name__=='__main__':main()
