from spice_runtime import *
import csv
rows=[]
try:
 for line in [198,220,235.4,242]:
  for loadma in [0,70,150]:
   for reg in [1,1.12]:
    a=300*line/220*reg*math.sqrt(2)
    text=f'''HV supply reference winding stress, 220V primary
 .options method=gear reltol=.003
VA a 0 SIN(0 {a} 50)
VB b 0 SIN(0 {-a} 50)
RA a aa 100
RB b bb 100
D3 aa midA DM
D4 midA raw DM
D5 bb midB DM
D6 midB raw DM
.model DM D(Is=5n Rs=.05 N=1.8 BV=1000 IBV=5u Cjo=15p Tt=2u)
C29 raw cm 220u
C30 cm 0 220u
R501 raw cm 220k
R502 cm 0 220k
ILOAD raw 0 {loadma/1000}
Rch raw ch 75
Lch ch screen 8
C26 screen 0 50u
R35 screen pre 10k
C25 pre 0 50u
C13 pre 0 50u
R17 pre early 10k
C12 early 0 50u
* Resistor load approximation, not tube warmup model.
Rpre pre 0 {80000 if loadma else 1e12}
Rearly early 0 {80000 if loadma else 1e12}
.end
'''
    name=f'HV-{line}-{loadma}-{reg}';(OUT/(name+'.cir')).write_text(text);load(text);cmd('tran 50u 3 2.8 50u');t=vector('time');raw=vector('v(raw)');scr=vector('v(screen)');ia=vector('i(VA)');ib=vector('i(VB)')
    def rms(vals):return math.sqrt(sum(v*v for v in vals)/len(vals))
    row={'line_V':line,'extra_load_mA':loadma,'secondary_multiplier':reg,'raw_mean_V':sum(raw)/len(raw),'raw_peak_V':max(raw),'raw_ripple_Vpp':max(raw)-min(raw),'screen_peak_V':max(scr),'half_winding_A_rms':max(rms(ia),rms(ib))};rows.append(row);cmd('destroy all')
 (OUT/'supply-results.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
finally:(OUT/'supply-ngspice.log').write_text('\n'.join(logs))
