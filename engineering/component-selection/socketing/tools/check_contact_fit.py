#!/usr/bin/env python3
"""Read-only contact sizing screen; never selects parts or edits native CAD."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def screen(contact, lead_min_mm, lead_max_mm):
    low = contact['minimum_in'] * 25.4
    high = contact['maximum_in'] * 25.4
    compliance = contact['compliancy_in'] * 25.4
    assert 0 < low <= high and compliance > 0
    initial = low <= lead_min_mm and lead_max_mm <= high
    replacement_min = max(low, lead_max_mm - compliance)
    return {
        'contact': contact['number'],
        'acceptance_mm': [low, high],
        'full_tolerance_initial_fit': initial,
        'minimum_replacement_after_largest_lead_mm': replacement_min if lead_max_mm <= high else None,
        'full_tolerance_replacement_fit': initial and lead_min_mm >= replacement_min,
        'lower_end_margin_mm': lead_min_mm - low,
        'upper_end_margin_mm': high - lead_max_mm,
    }


def main():
    contract_path = ROOT / 'contact-fit-contract.json'
    c = json.loads(contract_path.read_text())
    evidence = ROOT / c['contact_source']['local_file']
    assert hashlib.sha256(evidence.read_bytes()).hexdigest() == c['contact_source']['sha256']
    lead = c['lead_mm']
    minimum = math.hypot(lead['width_min'], lead['thickness_min'])
    maximum = math.hypot(lead['width_max'], lead['thickness_max'])
    rows = [screen(x, minimum, maximum) for x in c['contacts']]
    # A virgin fit is not sufficient: this hypothetical clip loses its ability
    # to accept the smallest replacement after the largest device is inserted.
    hypothetical = {'number': 'test-only', 'minimum_in': .030, 'maximum_in': .046, 'compliancy_in': .010}
    replacement_control = screen(hypothetical, minimum, maximum)
    assert replacement_control['full_tolerance_initial_fit']
    assert not replacement_control['full_tolerance_replacement_fit']
    compliant_control = screen({**hypothetical, 'compliancy_in': .020}, minimum, maximum)
    assert compliant_control['full_tolerance_replacement_fit']
    # Explicitly compare a manufactured rectangular lead's diagonal, not width.
    assert maximum > lead['width_max']
    assert not any(x['full_tolerance_initial_fit'] for x in rows)
    output = {
        'contract_sha256': hashlib.sha256(contract_path.read_bytes()).hexdigest(),
        'evidence_sha256': c['contact_source']['sha256'],
        'lead_diagonal_mm': [minimum, maximum],
        'lead_diagonal_in': [minimum / 25.4, maximum / 25.4],
        'contacts': rows,
        'checks': {'evidence_fresh': True, 'replacement_negative_control': True, 'compliant_positive_control': True},
        'qualification': 'None of the three screened contacts covers the complete published lead tolerance.',
        'socket_selected': False,
        'native_changes': False,
        'fabrication_ready': False,
    }
    (ROOT / 'results/contact-fit.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
