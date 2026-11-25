"""Limited lower-resistance transformer comparison; not a second qualification matrix."""
import copy
import itertools
import json
from pathlib import Path
from hold_up_screen import BASE, DEST, regulator_bounds, run, load, load_bounds, sha, spice


def main():
    c=json.loads((BASE/'hold-up-contract.json').read_text())
    c['transformer'].update(mpn='VPT36-1390',VA=50,series_current_A=1.39,
        datasheet='https://catalog.triadmagnetics.com/asset/vpt36-1390.pdf',
        procurement='Reference comparison only; no exact Chinese in-stock source verified.')
    c['comparison_scope']='Low mains, stress load, all shutdown phases and .95/1 winding factors; high mains/idle and stress at1.05. 6800uF only.'
    base=json.loads((BASE/'envelope-contract.json').read_text())
    base['reservoir_esr_ohm']=c['reservoir_esr_ohm']
    bounds=regulator_bounds(c);budget=load();preload=load_bounds(json.loads((BASE/'preload-contract.json').read_text()))
    original=json.loads((DEST/'screen.json').read_text())
    cases=[copy.deepcopy(r['case']) for r in original['cases'] if r['case']['nominal_cap_uF']==6800 and
        ('cutoff_s' in r['case'] or r['case']['winding_voltage_factor']==1.05)]
    high_stress=[]
    for x in cases:
        if 'cutoff_s' not in x:
            h=copy.deepcopy(x);h['id']+='-high-stress';h['load']=copy.deepcopy(base['loads'][-1]);high_stress.append(h)
    cases.extend(high_stress)
    rows=[];decks={};logs=[]
    for x in cases:
        x['id']='50VA-'+x['id']
        x['winding']['name']='VPT36-1390 typical-resistive surrogate'
        x['winding']['series_ohm_per_half']=18*.12/1.39
        row,text,log=run(c,base,budget,preload,bounds,x)
        rows.append(row);decks[x['id']]=text;logs.append(x['id']+'\n'+log)
    worst=min((r for r in rows if 'cutoff_s' in r['case']),key=lambda r:min(t if t is not None else 1e9 for t in r['hold_to_documented_headroom_loss_s'].values()))
    fine,text,log=run(c,base,budget,preload,bounds,worst['case'],10e-6)
    deltas={s:abs(fine['hold_to_documented_headroom_loss_s'][s]-worst['hold_to_documented_headroom_loss_s'][s])
            for s in ['positive','negative'] if fine['hold_to_documented_headroom_loss_s'][s] is not None and worst['hold_to_documented_headroom_loss_s'][s] is not None}
    assert max(deltas.values())<.0001
    decks['fine']=text;logs.append(log)
    report={'qualified':False,'native_adopted':False,'purchase_ready':False,'contract':c,'bounds':bounds,'cases':rows,
            'refinement':{'fine':fine,'hold_deltas_s':deltas},'decks':decks,'simulator':original['simulator'],
            'input_sha256':{str(p.relative_to(BASE.parent)):sha(p) for p in [Path(__file__),BASE/'tools/hold_up_screen.py',DEST/'screen.json']}}
    (DEST/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    (DEST/'comparison-simulator.log').write_text('\n\n'.join(logs)+'\n')
    print('Comparison cases',len(rows),'flags',sum(bool(r['screen_flags']) for r in rows))
    print('Worst shutdown',worst['case']['id'],worst['hold_to_documented_headroom_loss_s'])
    print('20ms fits',sum(r.get('hypothetical_total_mute_fits',{}).get('0.02',False) for r in rows))


if __name__=='__main__':main()
