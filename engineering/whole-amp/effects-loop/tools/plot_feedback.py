"""Render retained numeric evidence; no new electrical results."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];r=ROOT/'results'
curves=json.loads((r/'feedback-curves.json').read_text());ring=json.loads((r/'feedback-ringdown.json').read_text())
fig,axes=plt.subplots(2,1,figsize=(10,8),layout='constrained')
for name in ['legacy-pessimistic','lm40-lk20-cp250','lm40-lk80-cp1000']:
    c=curves[name];f=np.array(c['frequency_Hz']);g=np.array(c['closed_gain']);i=np.argmin(abs(f-1000));axes[0].semilogx(f,20*np.log10(g/g[i]),label=name)
axes[0].set(xlim=(1000,200000),ylim=(-35,15),xlabel='Frequency (Hz)',ylabel='Gain relative to 1 kHz (dB)',title='Transformer assumptions change the response')
axes[0].legend(fontsize=8);axes[0].grid(alpha=.2)
for c in ring['cases']:
    w=c['waveform'];axes[1].plot((np.array(w['time_s'])-.0095)*1e6,w['speaker_V'],label=c['name'].replace('feedback-ring-',''),lw=1)
axes[1].set(xlabel='Time after 9.5 ms (µs)',ylabel='Speaker voltage (V)',title='Rejected 220 pF feedback candidate: coarse timesteps hide oscillation')
axes[1].legend(fontsize=8);axes[1].grid(alpha=.2)
fig.suptitle('Renegade feedback diagnosis — generic models, not hardware qualification',fontsize=12)
fig.savefig(r/'feedback-diagnosis.png',dpi=160);fig.savefig(r/'feedback-diagnosis.pdf');plt.close(fig)
