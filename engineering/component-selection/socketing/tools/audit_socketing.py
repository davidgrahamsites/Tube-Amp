"""Read-only device/socket coverage audit; inventory success is not qualification."""
import copy
import hashlib
import json
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
PROJECT = MODULE.parents[2]
CIRCUIT = PROJECT / 'engineering/whole-amp/reverb-600/circuit.json'


def device_inventory(circuit):
    devices = {}
    for part in circuit['components']:
        ref = part['reference']
        if ref.startswith(('U', 'V')):
            if ref in devices and devices[ref] != part['value']:
                raise ValueError('Conflicting unit identities: ' + ref)
            devices[ref] = part['value']
    return devices


def audit(circuit, plan):
    actual = device_inventory(circuit)
    rows = plan['devices']
    by_ref = {row['reference']: row for row in rows}
    checks = {
        'one_row_per_device': len(by_ref) == len(rows),
        'complete_reference_coverage': set(actual) == set(by_ref),
        'values_match_source': all(by_ref.get(ref, {}).get('source_value') == value
                                   for ref, value in actual.items()),
        'all_require_sockets': all(row['required'] is True for row in rows),
        'qualification_has_evidence': all(
            not row['qualified'] or (row['selected_socket_mpn'] and
                                    row['qualification_evidence'] and
                                    not row['open_gates']) for row in rows),
        'unqualified_devices_have_actions': all(
            row['qualified'] or bool(row['open_gates']) for row in rows),
    }
    pending = [row['reference'] for row in rows if not row['qualified']]
    return dict(checks=checks, inventory_passed=all(checks.values()),
                device_count=len(actual), unqualified_references=pending,
                fabrication_ready=all(checks.values()) and not pending)


def main():
    plan_path = MODULE / 'socket-plan.json'
    circuit = json.loads(CIRCUIT.read_text())
    plan = json.loads(plan_path.read_text())
    result = audit(circuit, plan)
    missing = copy.deepcopy(plan)
    missing['devices'] = [x for x in missing['devices'] if x['reference'] != 'U7']
    added = copy.deepcopy(circuit)
    added['components'].append(dict(reference='U999', value='unreviewed IC'))
    false_release = copy.deepcopy(plan)
    false_release['devices'][0]['qualified'] = True
    controls = dict(
        missing_negative_regulator_detected=not audit(circuit, missing)['inventory_passed'],
        added_ic_detected=not audit(added, plan)['inventory_passed'],
        unsupported_socket_release_detected=not audit(circuit, false_release)['inventory_passed'])
    result.update(negative_controls=controls,
                  source_sha256={str(p.relative_to(PROJECT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (CIRCUIT, plan_path, Path(__file__))},
                  scope='All current source IC/tube references; native socket implementation and physical qualification remain open.')
    (MODULE / 'results/socket-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'source_sha256'}, indent=2))
    assert result['inventory_passed'] and all(controls.values())


if __name__ == '__main__':
    main()
