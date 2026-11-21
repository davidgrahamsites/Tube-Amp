"""Conservative electrical screen; actual transformer and enclosure temperature pending."""
from pathlib import Path
import json,math
root=Path(__file__).resolve().parent
# Existing 77.14V scoped bias-supply peak rounded upward; no claim for unspecified PT.
vbound=78.;r38_min=22000*.95;stop_min=33000*.95;track_max=50000*1.1
rows=[]
for ambient in [70,85,100]:
 rated=.5*(125-ambient)/55
 for frac in [0,.01,.25,.5,.75,1]:
  active=track_max*frac
  current=vbound/(r38_min+stop_min+active)
  # Uniform resistive track power density: I²*R_total <= full-track rating.
  equivalent=current**2*track_max
  rows.append(dict(ambient_C=ambient,track_fraction=frac,current_mA=current*1000,active_track_W=current**2*active,full_track_equivalent_W=equivalent,derated_full_track_W=rated,utilization=equivalent/rated,pass_density_screen=equivalent<=rated))
result={'part':'Bourns3296W-1-503LF','assumed_bias_filter_bound_V':vbound,'tolerances':'pot+10%; R38/R503-5%','rows':rows,'max_utilization':max(x['utilization'] for x in rows),'end_resistance_max_ohm':550,'limit':'Only proposed ambient<=100C; no actual PT, fault or hot-enclosure qualification. Wiper current/manufacturer application review remains required.'}
(root/'trimmer-rating-screen.json').write_text(json.dumps(result,indent=2)+'\n')
assert all(x['pass_density_screen'] for x in rows)
print('18 partial-track checks passed; maximum utilization',result['max_utilization'])
