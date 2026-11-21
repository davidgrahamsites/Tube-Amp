"""Apply selected MPN metadata only; preserve native wires/geometry/values."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
ENG=ROOT.parents[1]
sys.path.insert(0,str(ENG/'updated-schematic/tools'))
from kicad_factory import parse,serialize,children,child
coverage=json.loads((ENG/'component-selection/coverage.json').read_text())
parts={r['mpn']:r for r in json.loads((ENG/'component-selection/candidate-register.json').read_text())}
refs={ref:parts[r['selected_mpn']] for r in coverage if 'selected_mpn' in r for ref in r['refs']}
used={}
for p in (ROOT/'cad').glob('07*.kicad_sch'):
    tree=parse(p.read_text())
    for s in children(tree,'symbol'):
        props={v[1]:v for v in children(s,'property')};ref=props['Reference'][2]
        if ref not in refs:continue
        r=refs[ref];used[ref]=r['mpn'];at=child(s,'at')
        for key,val in {'MPN':r['mpn'],'Supplier_SKU':r['supplier_sku'],'Part_source':r['supplier_url'],'Price_stock_observed':r['observed'],'Part_status':'Engineering selected; exact footprint integration and physical qualification pending'}.items():
            if key in props:props[key][2]=val
            else:s.append(['property',key,val,['at',*at[1:]],['effects',['font',['size','1','1']],'hide']])
    p.write_text(serialize(tree)+'\n')
(ROOT/'review/native-selected-parts.json').write_text(json.dumps(used,indent=2)+'\n')
print('Selected MPNs annotated on',len(used),'reverb references; no footprint or wire changes.')
