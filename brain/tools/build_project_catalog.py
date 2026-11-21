"""Generate project-wide ICM views; never rewrite engineering/source material."""
import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BRAIN=ROOT/'brain'
OUT=BRAIN/'catalog'

def read_inputs():
    materials=json.loads((BRAIN/'materials/register.json').read_text())['materials']
    events=json.loads((BRAIN/'feedback/events.json').read_text())['events']
    errors=[]
    for rows,label in [(materials,'material'),(events,'feedback')]:
        ids=[r['id'] for r in rows]
        if len(ids)!=len(set(ids)):errors.append(f'duplicate {label} IDs')
    ids={r['id'] for r in events}
    for r in materials:
        for key in ['id','name','role','status','owner','paths','notes']:
            if not r.get(key):errors.append(f'{r.get("id")}: missing {key}')
        for p in r.get('paths',[]):
            if not (ROOT/p).exists():errors.append(f'{r["id"]}: missing material {p}')
    for r in events:
        for key in ['id','recorded_on','authority','kind','quote','source','interpretation','disposition','canonical_paths']:
            if not r.get(key):errors.append(f'{r.get("id")}: missing {key}')
        date.fromisoformat(r['recorded_on'])
        if r.get('occurred_on'):date.fromisoformat(r['occurred_on'])
        for p in r.get('canonical_paths',[]):
            if not (ROOT/p).is_file():errors.append(f'{r["id"]}: missing canonical record {p}')
        for old in r.get('supersedes',[]):
            if old not in ids or old==r['id']:errors.append(f'{r["id"]}: invalid supersedes {old}')
    return materials,events,errors

def visible_files():
    for p in sorted(ROOT.rglob('*')):
        rel=p.relative_to(ROOT)
        if not p.is_file() or any(n.startswith('.') or n=='__pycache__' for n in rel.parts):continue
        if rel.parts[:2]==('brain','catalog'):continue  # avoid self-referential hashes
        yield p,rel.as_posix()

def role(path):
    p=Path(path)
    if p.name=='CONTEXT.md':return 'contract'
    if p.name in ['AGENTS.md','INDEX.md','PROJECT_STATUS.md'] or p.name.startswith('README'):return 'catalog'
    if p.suffix in ['.py','.sh'] or any(n in p.parts for n in ['_templates','rules','models']):return 'factory/reference'
    if 'evidence' in p.parts or p.suffix in ['.pdf','.jpg','.png','.pptx','.zip'] or p.parts[0] in ['sources','Design Imperatives']:return 'evidence/source'
    return 'editable-product/record'

def link(path,label=None):
    return f'[{label or path}](<../../{path}>)'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--as-of',required=True,type=date.fromisoformat)
    args=parser.parse_args();materials,events,errors=read_inputs()
    coverage=json.loads((ROOT/'engineering/component-selection/coverage.json').read_text())
    refs=[ref for c in coverage for ref in c['refs']]
    duplicates=[ref for ref,n in Counter(refs).items() if n>1]
    if duplicates:errors.append('duplicate component reference ownership: '+str(duplicates))
    files=[]
    for p,path in visible_files():
        owners=[(len(route),m['id']) for m in materials for route in m['paths'] if path==route or path.startswith(route.rstrip('/')+'/')]
        owner=max(owners)[1] if owners else 'workspace-root/support'
        files.append({'path':path,'role':role(path),'owner_route':owner,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (OUT/'FILES.json').write_text(json.dumps({'as_of':str(args.as_of),'scope':'Visible project files; excludes hidden metadata, caches and generated catalog directory. File role is routing metadata, not a technical validation.','files':files},indent=2)+'\n')
    lines=['# Renegade project map','',f'Generated as of {args.as_of}. Edit brain/materials/register.json and brain/feedback/events.json, then rebuild.','',
           '## Start here','',
           '- Current state: '+link('PROJECT_STATUS.md'),
           '- Current circuit: '+link('engineering/whole-amp/reverb-600/review/review.md'),
           '- Selected parts: '+link('engineering/component-selection/selected-engineering-bom.csv'),
           '- Cabinet measurements: '+link('engineering/whole-amp/mechanical/review/measurement-guide.md'),
           '- Feedback workflow: '+link('brain/rules/feedback.md'),
           '- Decisions and evidence: '+link('brain/INDEX.md'),'',
           '## Materials and ownership','']
    for m in materials:
        lines += [f'### {m["id"]} — {m["name"]}',f'Role: {m["role"]}. Status: {m["status"]}. Owner: {m["owner"]}.','',m['notes'],'']
        lines += ['- '+link(p) for p in m['paths']]+['']
    lines += ['## Complete file inventory','',f'{len(files)} files cataloged with path, role, owner and SHA256 in [FILES.json](FILES.json). No existence/hash check establishes circuit safety or fit.','',
              'Historical native snapshots keep their existing paths and original internal layout. Their legacy scripts are not new-work templates. New active work separates tools/templates, editable registers and generated products.','',
              'Known missing evidence remains explicit in the mechanical register and engineering review. This backfill does not fabricate unavailable conversations, measurements, supplier answers or orders.']
    (OUT/'WORKSPACE.md').write_text('\n'.join(lines)+'\n')
    lines=['# Feedback and decision trail','',f'Generated as of {args.as_of}; source: ../feedback/events.json. Backfilled original timestamps may be unknown. Incorporated means recorded, not build-complete.','']
    for e in events:
        lines += [f'## {e["id"]} — {e["kind"]}',f'Authority: {e["authority"]}. Disposition: {e["disposition"]}. Recorded: {e["recorded_on"]}. Original date: {e["occurred_on"] or "unknown"}.','',f'> {e["quote"]}','',e['interpretation'],'',f'Source: {e["source"]}','']
        lines += ['- '+link(p) for p in e['canonical_paths']]+['']
    (OUT/'FEEDBACK.md').write_text('\n'.join(lines)+'\n')
    result={'as_of':str(args.as_of),'material_routes':len(materials),'feedback_events':len(events),'files':len(files),'component_reference_count':len(refs),'errors':errors,'passed':not errors}
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
