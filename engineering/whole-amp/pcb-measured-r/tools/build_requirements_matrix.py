"""Join reviewed dispositions to the immutable 364-rule source inventory.

No inferred pass status: the assessment is human review input. Outputs are CSV
traceability and a coverage manifest. Does not alter CAD or source imperatives.
"""
import csv
import hashlib
import json
import re
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
ROOT = MODULE.parents[2]
inventory_path = ROOT / 'Design Imperatives/review/inventory.json'
assessment_path = MODULE / 'requirements-assessment.json'
inventory = json.loads(inventory_path.read_text())
assessment = json.loads(assessment_path.read_text())
groups = {g['check_id']: g for g in assessment['groups']}
membership = {}
for group in groups.values():
    text = group['source_rule_refs'] + ' ' + assessment['extra_rule_groups'].get(group['check_id'], '')
    for prefix, start, end in re.findall(r'\b(TUBE|CN|PWR|AUD|APCB|LAY|TRACE)-(\d+)(?:\.\.(\d+))?', text):
        for i in range(int(start), int(end or start) + 1):
            membership.setdefault(f'{prefix}-{i:03d}', set()).add(group['check_id'])
failures = {rule: finding for finding, rules in assessment['confirmed_rule_failures'].items() for rule in rules.split()}
rows = []
for source in inventory['files']:
    for rule in source['rules']:
        rid = rule['id']
        assert rid in membership, f'Unassigned requirement: {rid}'
        linked = sorted(membership[rid])
        status, reason = assessment['default_rule_status'], assessment['default_reason']
        if rid in failures:
            status, reason = 'FAIL', f"Confirmed {failures[rid]} in requirements-audit.md; remaining clauses still need qualification."
        if rid in assessment['rule_exceptions']:
            status, reason = assessment['rule_exceptions'][rid]
        rows.append({'rule_id': rid, 'source': source['file'], 'source_line': rule['line'], 'source_sha256': source['sha256'],
                     'requirement_first_line': rule['first_line'], 'groups': '; '.join(linked), 'status': status, 'disposition': reason,
                     'observed_evidence': ' | '.join(groups[g]['assessment'] for g in linked),
                     'required_closure': ' | '.join(groups[g]['evidence_needed'] for g in linked),
                     'acceptance_basis': ' | '.join(groups[g]['acceptance_basis'] for g in linked),
                     'owner': '; '.join(sorted({groups[g]['responsible_owner'] for g in linked})),
                     'report': 'requirements-audit.md'})
assert len(rows) == 364 and len({r['rule_id'] for r in rows}) == 364
assert set(membership) == {r['rule_id'] for r in rows}, 'Unknown mapped requirement'
out = MODULE / 'review'
for name, data in [('requirements-matrix.csv', rows), ('requirements-groups.csv', list(groups.values()))]:
    with (out / name).open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(data[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(data)
summary = {'requirements': len(rows), 'groups': len(groups), 'statuses': {s: sum(r['status'] == s for r in rows) for s in sorted({r['status'] for r in rows})},
           'inventory_sha256': hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
           'assessment_sha256': hashlib.sha256(assessment_path.read_bytes()).hexdigest(), 'fabrication_ready': False,
           'limit': 'Complete requirement indexing is not complete engineering verification. NOT_VERIFIED items remain release blockers where applicable.'}
(out / 'requirements-coverage.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
