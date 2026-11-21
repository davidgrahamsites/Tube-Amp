"""Independent turns-ratio, impedance reflection and power-balance checks."""
from spice_runtime import *
p=OUT/'ideal-transformer-candidate';n=math.sqrt(7600/8)/2;rows=[]
for freq in [50,1000,20000]:
 text=f'''Ideal centre-tapped transformer fixture qualification
Vdrive pa pb DC 0 AC {2*n}
EPA pa 0 out 0 {n}
EPB 0 pb out 0 {n}
FSA 0 out EPA {n}
FSB 0 out EPB {n}
RLOAD out 0 8
.end
'''
 load(text);cmd(f'ac lin 1 {freq} {freq}');v=vector('v(out)')[0];ip=-vector('i(Vdrive)')[0];zin=2*n/ip;input_power=(2*n*ip.conjugate()).real;output_power=abs(v)**2/8
 assert abs(v-1)<1e-9 and abs(zin-7600)<1e-5 and abs(input_power-output_power)<1e-9
 rows.append(dict(frequency_Hz=freq,secondary_V=abs(v),reflected_primary_ohm=zin.real,input_power_W=input_power,output_power_W=output_power,passed=True));cmd('destroy all')
(p/'fixture-qualification.json').write_text(json.dumps(rows,indent=2));print('Three ideal transformer ratio/impedance/power-balance checks passed.')
