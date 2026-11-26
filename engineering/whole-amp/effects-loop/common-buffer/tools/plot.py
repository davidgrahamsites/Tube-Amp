"""Render the declared near-power and overload comparison from saved samples."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

M=Path(__file__).resolve().parents[1]
fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
inputs=[]
for ax,stem,hz,title in zip(axes,['clean-25w-probe','clean-bass'],[1000,82.4],
        ['Near 25 W · 1 kHz','Overload · 82.4 Hz']):
    for suffix,label,color in [('unlimited','Unlimited common buffer','#215e89'),
                               ('12','12 V ceiling','#c34b30')]:
        path=M/'results'/f'{stem}-{suffix}.csv';inputs.append(path)
        data=np.genfromtxt(path,delimiter=',',names=True)[-512:]
        x=(data['time_s']-data['time_s'][0])*hz
        ax.plot(x,data['SPEAKER'],label=label,color=color,lw=1.6,
                linestyle='-' if suffix=='unlimited' else '--')
    ax.set_title(title);ax.set_xlabel('Cycles');ax.set_ylabel('Speaker voltage (V)')
    ax.grid(alpha=.2);ax.legend(fontsize=8,loc='lower left')
fig.suptitle('Common loop buffer: power alone does not establish overload equivalence',fontsize=12)
fig.savefig(M/'results/waveform-comparison.png',dpi=150)
(M/'results/plot-receipt.json').write_text(json.dumps(dict(
    inputs={str(p.relative_to(M)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
    factory_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    output_sha256=hashlib.sha256((M/'results/waveform-comparison.png').read_bytes()).hexdigest(),
    scope='Generic tube / assumed transformer simulation; not measured hardware'),indent=2)+'\n')
