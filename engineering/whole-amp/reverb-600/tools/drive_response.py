"""Report electrical drive shaping. Does not predict acoustic tone or saturation."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'tools'))
from spice_runtime import load,cmd,vector
results=json.loads((ROOT/'simulation/results.json').read_text())
r_in=results['assumptions']['input_Rdc_nominal_ohm']
deck=ROOT/f'simulation/coil-z600-r{r_in:g}.cir'
load(deck.read_text());cmd('ac dec 60 20 20000')
freq=[v.real for v in vector('frequency')]
curr=[abs(a-b)/r_in*20/(2**.5)*1000 for a,b in zip(vector('v(tankin)'),vector('v(ti)'))]
points=[]
for hz in [82,100,250,1000,3000,5000]:
    k=min(range(len(freq)),key=lambda k:abs(freq[k]-hz))
    points.append({'frequency_Hz':freq[k],'current_mArms':curr[k]})
(ROOT/'review/drive-response.json').write_text(json.dumps({'scope':'600 ohm at1kHz assumed, measured 76ohm input DC, derived series-RL coil;20Vpeak source with100k source resistance;full send trim. Not actual tank drive rating.','points':points},indent=2)+'\n')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(8,4))
ax.semilogx(freq,curr,color='#116778',linewidth=2)
ax.set(xlabel='Frequency (Hz)',ylabel='Tank current (mA RMS)',title='Electrical drive screen — full send trim, measured R / assumed L')
ax.grid(True,which='both',alpha=.2)
fig.text(.1,.01,'20 V peak source / 100 kΩ source resistance. This is not a safe-current limit for the received tank.',fontsize=8)
fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(ROOT/'review/drive-response.png',dpi=150)
print(json.dumps(points,indent=2))
