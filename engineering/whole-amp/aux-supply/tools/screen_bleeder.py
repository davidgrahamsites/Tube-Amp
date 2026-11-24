"""Three targeted raw-supply repeats with the proposed820ohm5V preload."""
import copy
import hashlib
import json
from screen_envelope import MODULE, evaluate


def main():
    c=json.loads((MODULE/'envelope-contract.json').read_text())
    p=MODULE/'results/envelope'
    original=json.loads((p/'screen.json').read_text())
    checked=json.loads((p/'checks.json').read_text())
    assert checked['screen_sha256']==hashlib.sha256((p/'screen.json').read_bytes()).hexdigest()
    rows=[]
    for profile in ['idle','working_reserve','expansion_stress']:
        baseline=max((r for r in original['cases'] if r['case']['load']['name']==profile),key=lambda r:r['conditional_total_W'])
        case=copy.deepcopy(baseline['case'])
        case['id']+='-preload'
        case['load']['logic_5V_A']+=checked['bleeder_proposal']['maximum_current_A']
        result,deck=evaluate(c,case,c['simulation']['max_step_s'])
        assert 'U5_below_minimum_regulation_load' not in result['screen_flags']
        rows.append({'baseline_id':baseline['case']['id'],'result':result,'deck':deck,
                     'conditional_added_regulator_heat_W':result['conditional_total_W']-baseline['conditional_total_W']})
    output={'proposal':checked['bleeder_proposal'],'case_count':3,'cases':rows,
            'baseline_screen_sha256':checked['screen_sha256'],
            'limits':'Unadopted preload; only worst-heating baseline case of each profile repeated. Not a new full matrix, regulator startup/stability or physical qualification.'}
    (p/'bleeder-screen.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'cases':3,'max_added_regulator_heat_W':max(r['conditional_added_regulator_heat_W'] for r in rows),'native_changes':False}))


if __name__=='__main__':main()
