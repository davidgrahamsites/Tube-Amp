"""HD012 endpoint enumeration; references declared allocations, not measurements."""
from pathlib import Path
import itertools,json
M=Path(__file__).resolve().parents[1]
def calculate(c,reset):
 rows=[];f=c['resistor_fraction']
 for signs in itertools.product([-1,1],repeat=9):
  a,b,d,e,g,h,i,j,k=signs;ref=c['reference_V']*(1+a*c['reference_fraction']);ri=c['isolation_ohm']*(1+b*f);rr=reset*(1+d*f);low=c['hold_low_V'][0 if e<0 else 1];ip=g*c['input_bias_plus_board_A'];offset=h*c['main_offset_V'];top=c['sense_upper_ohm']*(1+i*f);bot=c['sense_lower_ohm']*(1+j*f);isen=k*c['input_bias_plus_board_A']
  pos=low if not reset else (ref/ri+low/rr-ip)/(1/ri+1/rr)
  out=(pos+offset)*(1+top/bot)+isen*top
  rows.append(dict(signs=signs,positive_V=pos,reset_V=out,resistor_W=0 if not reset else (pos-low)**2/rr))
 return dict(reset_resistor_ohm=reset,minimum_V=min(x['reset_V'] for x in rows),maximum_V=max(x['reset_V'] for x in rows),maximum_resistor_W=max(x['resistor_W'] for x in rows),corners=rows)
if __name__=='__main__':
 c=json.loads((M/'reset-contract.json').read_text());d=dict(old=calculate(c,0),candidate=calculate(c,c['reset_ohm']),qualified=False);(M/'results/reset-bounds.json').write_text(json.dumps(d,indent=2)+'\n');print({k:{q:v for q,v in a.items() if q!='corners'} if isinstance(a,dict) else a for k,a in d.items()})
