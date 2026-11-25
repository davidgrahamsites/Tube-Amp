"""Read-only arithmetic, evidence and native-preservation audit of hold-up screens."""
import copy
import hashlib
import json
import math
import subprocess
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
DEST=BASE/'results/hold-up'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def audit(report, expected_count):
    c=report['contract']; rows=report['cases'];checks=0;errors=[]
    def check(ok, label):
        nonlocal checks
        checks+=1
        if not ok:errors.append(label)
    check(all(report[k] is False for k in ['qualified','native_adopted','purchase_ready']),'release hold')
    check(len(rows)==expected_count,'case count')
    check(len({r['case']['id'] for r in rows})==len(rows),'unique cases')
    for group in ['input_sha256','load_dependency_sha256']:
        for name,h in report.get(group,{}).items():check(digest(BASE.parent/name)==h,'hash '+name)
    check('ngspice-45.2' in str(report['simulator']['version_output']),'simulator version')
    check(digest(BASE.parent/'tools/spice_runtime.py')==report['simulator']['runtime_sha256'],'runtime hash')
    f=c['set_resistor_total_fraction']
    for ref,p in c['regulators'].items():
        lo=min(c['regulator_reference_magnitude_V'])*(1+p['R2_ohm']*(1-f)/(p['R1_ohm']*(1+f)))+min(c['adjust_current_magnitude_A'])*p['R2_ohm']*(1-f)
        hi=max(c['regulator_reference_magnitude_V'])*(1+p['R2_ohm']*(1+f)/(p['R1_ohm']*(1-f)))+max(c['adjust_current_magnitude_A'])*p['R2_ohm']*(1+f)
        check(max(abs(x-y) for x,y in zip([lo,hi],report['bounds'][ref]['output_abs_V']))<1e-10,'divider bound '+ref)
        check(min(c['regulator_reference_magnitude_V'])/(p['R1_ohm']*(1+f))>=.01,'minimum load '+ref)
    max_discharge_error=0
    for r in rows:
        x=r['case'];text=report['decks'][x['id']]
        cap=x['nominal_cap_uF']*c['reservoir_min_fraction']
        check(abs(x['reservoir_uF']-cap)<1e-9,'cap tolerance '+x['id'])
        check(f'C201 cp 0 {cap}u' in text and f'C208 0 cn {cap}u' in text,'deck capacitance '+x['id'])
        check(r['kcl_max_error_A']<1e-5,'KCL '+x['id'])
        flags=[]
        for side in ['positive','negative']:
            m=r['rails'][side]
            refs=['U4','U6'] if side=='positive' else ['U7']
            floor=max(report['bounds'][ref]['output_abs_V'][1] for ref in refs)+c['required_input_output_headroom_V']
            check(abs(m['required_raw_floor_V']-floor)<1e-10,'floor '+x['id']+side)
            if m['min_V']<floor:flags.append(side+' insufficient regulated headroom')
            if m['max_V']>=c['raw_voltage_design_ceiling_V']:flags.append(side+' above raw design ceiling')
        if max(r['winding_rms_A'].values())>c['transformer']['series_current_A']:flags.append('winding RMS exceeds candidate rating')
        check(flags==r['screen_flags'],'flags '+x['id'])
        if 'cutoff_s' not in x:continue
        for delay in c['hypothetical_detection_plus_contact_s']:
            fits=not flags and all(t is None or t>=delay for t in r['hold_to_documented_headroom_loss_s'].values())
            check(fits==r['hypothetical_total_mute_fits'][str(delay)],'mute fit '+x['id'])
        sample=r['post_cutoff_sample'];rb=1e8;rs=c['reservoir_esr_ohm']
        for side in ['positive','negative']:
            t=r['hold_to_documented_headroom_loss_s'][side];v0=sample[side+'_V'];floor=r['rails'][side]['required_raw_floor_V'];i=r['raw_load_A'][side]
            if v0<=floor:continue
            # Independent constant-load RC solution after both winding sources reach zero.
            predicted=sample['elapsed_s']+cap*1e-6*(rb+rs)*math.log1p((v0-floor)/(floor+i*rb))
            if t is None:check(predicted>=c['shutdown_post_window_s']-1e-4,'censored discharge '+x['id'])
            else:
                err=abs(predicted-t);max_discharge_error=max(err,max_discharge_error)
                check(err<1e-4,'closed form discharge '+x['id']+side)
    if expected_count==134:
        check(sum('cutoff_s' in r['case'] for r in rows)==72,'shutdown coverage')
        for cap in c['reservoir_nominal_uF']:
            for factor in c['shutdown_winding_voltage_factors']:
                pairs={(r['case']['selector_V'],r['case']['phase_deg']) for r in rows if 'cutoff_s' in r['case'] and r['case']['nominal_cap_uF']==cap and r['case']['winding_voltage_factor']==factor}
                check(pairs=={(m['selector_V'],p) for m in c['modes'] for p in c['shutdown_phases_deg']},'shutdown grid')
        check(len(report['refinements'])==4,'refinement count')
        check(all(x['max_voltage_delta_V']<.02 and (x['max_hold_delta_s'] is None or x['max_hold_delta_s']<.0001) for x in report['refinements']),'refinement limits')
    else:
        check(sum('cutoff_s' in r['case'] for r in rows)==24,'comparison shutdown coverage')
        check(max(report['refinement']['hold_deltas_s'].values())<.0001,'comparison refinement')
    return {'passed':not errors,'checks':checks,'errors':errors,'max_closed_form_discharge_delta_s':max_discharge_error}


def main():
    report=json.loads((DEST/'screen.json').read_text());comparison=json.loads((DEST/'comparison.json').read_text())
    results={'primary':audit(report,134),'comparison':audit(comparison,28)}
    assert all(r['passed'] for r in results.values()),results
    controls=[]
    for name,mutate in [
        ('false release',lambda d:d.update(qualified=True)),
        ('missing case',lambda d:d['cases'].pop()),
        ('changed reservoir',lambda d:d['decks'].__setitem__(d['cases'][0]['case']['id'],d['decks'][d['cases'][0]['case']['id']].replace('C201 cp 0 800.0u','C201 cp 0 8000.0u'))),
        ('wrong output bound',lambda d:d['bounds']['U6']['output_abs_V'].__setitem__(1,14)),
        ('invented mute pass',lambda d:next(r for r in d['cases'] if 'cutoff_s' in r['case'])['hypothetical_total_mute_fits'].__setitem__('0.02',True)),
        ('stale input',lambda d:d['input_sha256'].__setitem__('aux-supply/hold-up-contract.json','0'*64))]:
        altered=copy.deepcopy(report);mutate(altered);a=audit(altered,134)
        assert not a['passed'],name
        controls.append({'mutation':name,'rejected':True,'first_error':a['errors'][0]})
    paths=subprocess.check_output(['git','ls-files','engineering/whole-amp/reverb-600/cad','engineering/whole-amp/pcb-measured-r/boards'],cwd=ROOT,text=True).splitlines()
    paths=[p for p in paths if p.endswith(('.kicad_sch','.kicad_pcb'))]
    native=[]
    for p in paths:
        old=subprocess.check_output(['git','show',report['contract']['baseline']+':'+p],cwd=ROOT)
        assert (ROOT/p).read_bytes()==old,p
        native.append({'path':p,'sha256':digest(ROOT/p)})
    assert len(native)==22,len(native)
    results.update(negative_controls=controls,native_preserved=native,qualified=False,purchase_ready=False)
    (DEST/'checks.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({k:v for k,v in results.items() if k not in ['native_preserved','negative_controls']},indent=2))
    print('Six corruptions rejected; 22 native CAD files unchanged.')


if __name__=='__main__':main()
