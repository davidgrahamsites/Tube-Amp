from pathlib import Path
import itertools,json,math
p=Path(__file__).resolve().parent;v=510.31
# Heater elevation divider tolerances, static rail assumption.
corners=[]
for rt,rb in itertools.product([220e3*.95,220e3*1.05],[39e3*.95,39e3*1.05]):
 i=v/(rt+rb);corners.append({'upper_V':i*rt,'lower_V':i*rb,'upper_W':i*i*rt,'lower_W':i*i*rb})
reservoir=json.loads((p/'reservoir-balance-results.json').read_text());n=next(x for x in reservoir['results'] if x['mpn']=='LGU2G221MELB')
rows=[]
for refs,volts,power in [('R501/R502',n['max_cap_V'],n['max_balancing_resistor_W']),('R506',max(x['upper_V'] for x in corners),max(x['upper_W'] for x in corners)),('R507',max(x['lower_V'] for x in corners),max(x['lower_W'] for x in corners))]:
 for temp in [70,100,125]:
  allowed=2*(155-temp)/85;rows.append(dict(references=refs,ambient_C=temp,voltage_V=volts,power_W=power,derated_W=allowed,voltage_limit_V=500,pass_screen=power<=allowed and volts<=500))
r={'assumed_Bplus_V':v,'scope':'Static bound only; reservoir20C leakage assumptions retained. Heater-divider5%tolerances, no heater/tube leakage or fault.','cases':rows,'required_selected_ambient_ceiling_C':100}
assert all(x['pass_screen'] for x in rows if x['ambient_C']<=100)
(p/'power-divider-resistor-screen.json').write_text(json.dumps(r,indent=2)+'\n');print(rows)
