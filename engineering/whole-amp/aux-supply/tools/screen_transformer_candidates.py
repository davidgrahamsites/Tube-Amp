"""Bounded option comparison using existing raw-supply model; no native mutation."""
import copy
import itertools
import json
from calculate_loads import MODULE, load, sha
from check_preload import load_bounds
from screen_envelope import evaluate, spice


def scaling(mode, line_fraction):
    return mode['selector_V']*line_fraction/mode['primary_rating_V']


def main():
    contract = json.loads((MODULE/'transformer-candidates.json').read_text())
    base = json.loads((MODULE/'envelope-contract.json').read_text())
    budget = load(); preload = load_bounds(json.loads((MODULE/'preload-contract.json').read_text()))
    base['relay_min_resistance_ohm'] = budget['relay']['cold_screen_resistance_ohm']
    # Screen the proposed TI U4, whose guaranteed output range covers27V input.
    # U6 still restricts positive input to28V, so the shared rail limit is27V.
    base['raw_screen_V']['positive_max'] = min(28,contract['replacement_U4']['regulated_input_V'][1])
    base['iq_A']['U4'] = contract['replacement_U4']['iq_screen_A']
    base['load_basis']['relay'] = 'Cold-coil screen imported from control-switching through calculate_loads.load(); see retained budget, not the historical room-temperature assumption.'
    base['iq_basis'] += ' Proposed U4 instead uses the TI LM340 over-temperature bound and variations declared in transformer-candidates.json.'
    base['raw_screen_basis'] = 'Candidate TI U4 14.5-27V intersects unchanged ST U6 17.5-28V; negative ST U7 screen unchanged. No change to the actual native ST U4 rating.'
    assert base['thermal_output_bound_V']['U4'] == contract['replacement_U4']['output_V'][0]
    dest = MODULE/'results/transformer-candidates'; rows=[]; decks={}; logs=[]
    cases = itertools.product(contract['candidates'],contract['modes'],contract['line_fractions'],contract['reservoir_nominal_uF'],base['loads'])
    for index,(part,mode,line,cap,profile) in enumerate(cases):
        voltage=part['half_secondary_loaded_V']; reg=part['regulation_typ_fraction']
        case=dict(id=f'transformer{index:03d}',line_factor=scaling(mode,line),frequency_hz=mode['frequency_hz'],
                  winding=dict(name=part['mpn']+'-typical-resistive-surrogate',open_circuit_half_rms_V=voltage*(1+reg),series_ohm_per_half=voltage*reg/part['series_current_A']),
                  reservoir_uF=cap*contract['reservoir_min_fraction'],load=copy.deepcopy(profile))
        case['load']['logic_5V_A']+=preload['maximum_current_A']
        row,deck=evaluate(base,case,base['simulation']['max_step_s'])
        row.update(mpn=part['mpn'],selector_V=mode['selector_V'],primary_rating_V=mode['primary_rating_V'],mains_V=mode['selector_V']*line,nominal_cap_uF=cap)
        row['screen_flags']=[f for f in row['screen_flags'] if f!='half_winding_exceeds_provisional_0p25A']
        if max(row['half_winding_rms_A'].values())>part['series_current_A']:
            row['screen_flags'].append('half_winding_above_candidate_rating')
        row['existing_ST_U4_above_documented_range']=row['raw_positive_V']['max']>25
        rows.append(row); decks[case['id']]=deck; logs.append(case['id']+'\n'+'\n'.join(spice.logs))
    # Select low positive, low negative and highest heat for each part/cap pair.
    refine=set()
    for part,cap in itertools.product(contract['candidates'],contract['reservoir_nominal_uF']):
        indices=[i for i,r in enumerate(rows) if r['mpn']==part['mpn'] and r['nominal_cap_uF']==cap]
        for key in [lambda r:r['raw_positive_V']['min'],lambda r:r['raw_negative_magnitude_V']['min'],lambda r:-r['conditional_total_W']]:
            refine.add(min(indices,key=lambda i:key(rows[i])))
    refinements=[]
    for i in sorted(refine):
        row=rows[i]; fine,deck=evaluate(base,row['case'],base['simulation']['max_step_s']/2)
        dv=max(abs(fine[k][n]-row[k][n]) for k in ['raw_positive_V','raw_negative_magnitude_V'] for n in ['min','mean','max'])
        di=max(abs(fine['half_winding_rms_A'][k]/row['half_winding_rms_A'][k]-1) for k in row['half_winding_rms_A'])
        assert dv<.01 and di<.005
        refinements.append(dict(coarse_id=row['case']['id'],voltage_delta_V=dv,rms_relative_delta=di,fine=fine))
        decks[row['case']['id']+'-fine']=deck; logs.append(row['case']['id']+'-fine\n'+'\n'.join(spice.logs))
    summary=[]
    for part,cap in itertools.product(contract['candidates'],contract['reservoir_nominal_uF']):
        rs=[r for r in rows if r['mpn']==part['mpn'] and r['nominal_cap_uF']==cap]
        summary.append(dict(mpn=part['mpn'],cap_uF=cap,cases=len(rs),flagged=sum(bool(r['screen_flags']) for r in rs),
                            min_positive_V=min(r['raw_positive_V']['min'] for r in rs),min_negative_V=min(r['raw_negative_magnitude_V']['min'] for r in rs),
                            max_positive_V=max(r['raw_positive_V']['max'] for r in rs),max_winding_A=max(max(r['half_winding_rms_A'].values()) for r in rs),
                            max_conditional_heat_W=max(r['conditional_total_W'] for r in rs),existing_ST_U4_flagged=sum(r['existing_ST_U4_above_documented_range'] for r in rs)))
    result=dict(contract=contract,effective_model=base,budget=budget,preload=preload,summary=summary,cases=rows,refinements=refinements,decks=decks,
                input_sha256={p:sha(MODULE/p) for p in ['transformer-candidates.json','envelope-contract.json','preload-contract.json','load-contract.json']},
                factory_sha256=sha(__import__('pathlib').Path(__file__)),native_adopted=False,purchase_ready=False)
    (dest/'screen.json').write_text(json.dumps(result,indent=2)+'\n');(dest/'simulator.log').write_text('\n\n'.join(logs)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
