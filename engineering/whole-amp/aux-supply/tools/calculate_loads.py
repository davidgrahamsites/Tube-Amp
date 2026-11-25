"""Supply load facts with explicit source binding; no CAD writes or width approval."""
import hashlib
import json
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calculate(contract, control, circuit):
    parts = {(p['reference'], p['unit']): p for p in circuit['components']}
    coil = control['coil']
    groups = {}
    for ref, net in contract['relay_references'].items():
        part = parts[ref, 1]
        assert part['selected_mpn'] == coil['mpn'], (ref, 'coil family changed')
        assert part['pins'] == {'1': '+12V', '16': net}, (ref, 'coil wiring changed')
        groups.setdefault(net, []).append(ref)
    # Copper temperature coefficient is an engineering approximation shared with
    # the relay driver screen, not a manufacturer's guaranteed cold resistance.
    cold_r = coil['resistance_23C_ohm'] * (1-coil['resistance_tolerance']) * (
        1+coil['copper_tcr_screen_per_C']*(min(control['relay_temperature_C'])-23))
    assert cold_r > 0
    one = max(coil['voltage_V'])/cold_r
    room = max(coil['voltage_V'])/(coil['resistance_23C_ohm']*(1-coil['resistance_tolerance']))
    heaters = []
    for family, item in contract['heater_packages'].items():
        for ref in item['references']:
            part = parts[ref, item['unit']]
            assert family in part['value'] and part['pins'] == item['pins'], (ref, 'heater changed')
            heaters.append({'reference': ref, 'nominal_A': item['current_per_package_A']})
    assert len({p['reference'] for p in heaters}) == len(heaters), 'Double-counted tube package'
    for ref, net in [('R508', 'HEAT_A'), ('R509', 'HEAT_B')]:
        assert parts[ref, 1]['pins'] == {'1': net, '2': 'HREF'}
    balance_r = sum(float(parts[ref, 1]['value']) for ref in ['R508', 'R509'])
    balance = contract['heater_nominal_V']/balance_r
    assert parts['JH1', 1]['pins'] == {'1': 'HEAT_A', '2': 'HEAT_B'}
    return {
        'relay': {'cold_screen_resistance_ohm': cold_r, 'one_coil_A': one,
                  'room_temperature_one_coil_A': room,
                  'increase_over_room_fraction': one/room-1,
                  'groups_A': {net: len(refs)*one for net, refs in groups.items()},
                  'all_coils_A': len(contract['relay_references'])*one,
                  'voltage_bound_V': max(coil['voltage_V']),
                  'temperature_screen_C': min(control['relay_temperature_C'])},
        'heater': {'packages': heaters, 'tube_nominal_total_A': sum(x['nominal_A'] for x in heaters),
                   'balance_pair_nominal_A': balance, 'pilot_allowance_A': contract['pilot_allowance_A'],
                   'nominal_plus_pilot_allowance_A': sum(x['nominal_A'] for x in heaters)+balance+contract['pilot_allowance_A']},
        'complete_current_budget': False, 'copper_qualified': False,
        'limitations': contract['unqualified']}


def load():
    path = MODULE/'load-contract.json'
    contract = json.loads(path.read_text())
    control_path = MODULE/contract['control_contract']
    circuit_path = MODULE/contract['source_circuit']
    result = calculate(contract, json.loads(control_path.read_text()), json.loads(circuit_path.read_text()))
    result['input_sha256'] = {str(p.relative_to(MODULE.parent)): sha(p) for p in
                              [path, control_path.resolve(), circuit_path.resolve()]}
    return result


if __name__ == '__main__':
    result = load()
    (MODULE/'results/loads/budget.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
