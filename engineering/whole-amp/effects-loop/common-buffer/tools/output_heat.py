"""CB-004: ideal output-pair load and heat calculation; no device selection."""
from pathlib import Path
import hashlib,json,math
import numpy as np
M=Path(__file__).resolve().parents[1];ROOT=M.parents[3];O=M/'results';P=M/'output-heat.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads(P.read_text());a=s['signal_peak_V'];r=s['load_ohm'];w=2*math.pi*s['frequency_Hz'];v=s['output_dc_V'];hv=s['supply_V'];theta=np.linspace(0,2*math.pi,65536,endpoint=False);rows=[];checks={}
 for cp in s['load_capacitance_pF']:
  c=cp*1e-12;ipk=math.hypot(a/r,w*c*a);wave=a/r*np.sin(theta)+w*c*a*np.cos(theta)
  checks[f'{cp}:current_peak']=abs(max(abs(wave))/ipk-1)<1e-8
  for bias in s['trial_bias_A']:
   follower=(hv-v-a*np.sin(theta))*(bias+wave);sink=(v+a*np.sin(theta))*bias
   mean_f=(hv-v)*bias-a*a/(2*r);mean_s=v*bias;pf0=(hv-v)*bias;ps0=v*bias;total=pf0+ps0
   checks[f'{cp}:{bias}:power_integral']=abs(follower.mean()-mean_f)<1e-10 and abs(sink.mean()-mean_s)<1e-10
   models=[]
   for dev in s['candidates']:
    local=max(pf0,ps0)*(dev['theta_JC_max_C_per_W']+s['insulating_interface_C_per_W_assumed']);sink_budget=(s['junction_design_limit_C_assumed']-s['ambient_C_assumed']-local)/total
    tj=s['ambient_C_assumed']+total*sink_budget+local
    checks[f'{cp}:{bias}:{dev["part"]}:thermal_balance']=abs(tj-s['junction_design_limit_C_assumed'])<1e-10
    models.append({'part':dev['part'],'common_sink_to_air_budget_C_per_W':sink_budget,'interface_is_assumed':True,'bare_air_junction_C_if_theta_JA_given':s['ambient_C_assumed']+max(pf0,ps0)*dev['theta_JA_max_C_per_W'] if 'theta_JA_max_C_per_W' in dev else None})
   rows.append({'load_pF':cp,'bias_A':bias,'load_peak_A':ipk,'load_current_margin_ratio':bias/ipk,'ideal_follower_min_A':bias-ipk,'load_current_floor_met':bias>=ipk,'follower_sine_mean_W_if_no_cutoff':mean_f if bias>=ipk else None,'sink_sine_mean_W':mean_s,'follower_standing_W':pf0,'sink_standing_W':ps0,'pair_standing_W':total,'mounting':models})
 checks['native_not_adopted']=s['selected_part'] is None and not s['native_adopted'];checks['all_cases']=len(rows)==12
 # Closed-form endpoints independently constrain the units and heat arithmetic.
 checks['500p_13mA_current']=abs(rows[-1]['load_peak_A']-.008491588296)<1e-12
 checks['500p_13mA_heat']=abs(rows[-1]['pair_standing_W']-5.2)<1e-12
 checks['500p_13mA_sink_budget']=abs(rows[-1]['mounting'][0]['common_sink_to_air_budget_C_per_W']-8.326923076923077)<1e-10
 checks={key:bool(value) for key,value in checks.items()}
 result={'id':s['id'],'date':s['date'],'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [P,Path(__file__)]},'checks':checks,'passed':all(checks.values()),'cases':rows,'selected_part':None,'native_adopted':False,'SOA_qualified':False,'physical_fit_qualified':False};(O/'output-heat.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks':len(checks),'passed':result['passed'],'500p_13mA':rows[-1]},indent=2));assert result['passed']
if __name__=='__main__':main()
