"""Selected engineering parts only; not an order/released full amplifier BOM."""
from pathlib import Path
import json,csv,math
p=Path(__file__).resolve().parent;c=json.loads((p/'coverage.json').read_text());a=json.loads((p/'candidate-register.json').read_text());grouped={}
for r in c:
 if 'selected_mpn' in r:grouped.setdefault(r['selected_mpn'],[]).extend(r['refs'])
rows=[]
for mpn,refs in grouped.items():
 matches=[r for r in a if r['mpn']==mpn];assert len(matches)==1,mpn;r=matches[0];moq=r['minimum_quantity'];buy=math.ceil(len(refs)/moq)*moq;price=r['unit_price_cny']
 rows.append(dict(references=';'.join(refs),quantity_fitted=len(refs),mpn=mpn,supplier_sku=r['supplier_sku'],supplier_url=r['supplier_url'],price_observed=r['observed'],moq=moq,planned_purchase_quantity=buy,unit_cny_at_recorded_tier=price,estimated_cny=round(price*buy,4),status='ENGINEERING SELECTED; not procurement release'))
with (p/'selected-engineering-bom.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'selected_mpn_count':len(rows),'selected_reference_count':sum(r['quantity_fitted'] for r in rows),'selected_group_count':len([r for r in c if 'selected_mpn'in r]),'total_group_count':len(c),'estimated_selected_subset_purchase_CNY':round(sum(r['estimated_cny'] for r in rows),2),'limitations':['Partial selected subset, not full amplifier cost','MOQ-priced quantities rounded to MOQ multiples; actual order increments and tier prices must be rechecked','Excludes unselected parts, taxes/shipping and PCB/cabinet fabrication','Engineering selections still carry individually documented qualification/fit gaps']}
(p/'selected-engineering-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
