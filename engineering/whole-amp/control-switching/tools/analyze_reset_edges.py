"""Datasheet-bound edge budget and unmodified vendor-model discrepancy audit."""
import hashlib,json,math
from pathlib import Path
M=Path(__file__).resolve().parents[1]

def main():
    c=json.loads((M/'edge-contract.json').read_text())
    model=M/'models/TPS389001_TRANS.LIB';raw=model.read_bytes();text=raw.decode()
    digest=hashlib.sha256(raw).hexdigest()
    assert digest=='0d2f974f84e65ffdad0f69f1381d6a0bd4a3767f96137cab6875ecdc45e2a18e'
    lines=[line for line in text.splitlines() if any(key in line for key in ['G_U1_ABMI2','X_U1_U18','X_U1_S4','X_U34','X_U50'])]
    assert any('SENSE_CT' in line and '1.19u' in line for line in lines)
    assert any('MR_OUT' in line and 'N17060149' in line for line in lines)
    screen=json.loads((M/'results/reset-screen.json').read_text())
    manual=next(x['result'] for x in screen['refinements'] if x['id']=='manual-reset')
    release=manual['transitions'][-1]['time_s']
    edge=c['hc14']['transition_max_s'];limit=c['hc74']['input_transition_limit_s_at_4p5V']
    load_remaining=c['hc14']['test_load_max_F']-c['hc74']['input_capacitance_max_F']*c['hc74']['clear_inputs']
    assert edge<limit and load_remaining>0
    report=dict(scope='Steady powered logic edge bound; startup and rail-collapse behavior NOT qualified',
        model_sha256=digest,vendor_model_relevant_lines=lines,
        manual_reset_model_release_time_s=release,manual_reset_input_fully_high_time_s=.420001,
        model_release_delay_after_MR_rise_s=release-.420001,
        model_limitation='MR gates RESET but does not discharge CT in this model; datasheet requires CT discharge and repeated delay. Do not treat this as a physical-device failure or patch the model to obtain a pass.',
        raw_RC_10_to_90_s=[dict(capacitance_F=cap,rise_s=math.log(9)*c['raw_pullup_ohm']*cap) for cap in c['raw_capacitance_screen_F']],
        conditioned_edge_max_s=edge,hc74_transition_limit_s=limit,edge_margin_factor=limit/edge,
        two_gate_propagation_bound_s=2*c['hc14']['propagation_each_max_s'],
        output_socket_trace_capacitance_budget_F=load_remaining,
        existing_TPS3808G50_conservative_release_max_V=4.65*1.02*1.025,
        minimum_5V_rail_V=4.75,existing_supervisor_release_guaranteed=False,
        assumptions=['4.5 V datasheet test point, -40..85 C, <=50 pF each gate output','Two HC74 clear inputs at <=10 pF each; no extra output loads','2% TPS3808 threshold and 2.5% hysteresis combined multiplicatively as conservative screen'],
        pending=['actual output capacitance and socket parasitics','supervisor threshold/carrier selection','fast rail collapse and power-up state','reset release coincident with external clocks; HC74 recovery timing'],fabrication_ready=False)
    (M/'results/edge-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='vendor_model_relevant_lines'},indent=2))

if __name__=='__main__':main()
