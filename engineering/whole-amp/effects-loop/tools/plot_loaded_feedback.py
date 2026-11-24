"""Render retained numeric evidence; owns no circuit parameters or acceptance."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parents[1]/'results'
curves = json.loads((OUT/'loaded-feedback-curves.json').read_text())
summary = json.loads((OUT/'loaded-feedback-summary.json').read_text())
burst = json.loads((OUT/'loaded-burst-summary.json').read_text())
fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
colors = ['#236c83', '#c3562d', '#668335', '#933b72']
labels = ['Nominal assumptions', 'High leakage, unchanged', 'High leakage, C22 100 pF + 22 pF feedback', 'Rejected 220 pF feedback']
for (key, data), label, color in zip(curves.items(), labels, colors):
    f = np.array(data['frequency_Hz'])
    t = np.array(data['loop_real']) + 1j*np.array(data['loop_imag'])
    h = np.array(data['gain'])
    ref = h[np.argmin(abs(f-1000))]
    axes[0, 0].semilogx(f, 20*np.log10(abs(t)), color=color, label=label)
    axes[0, 1].semilogx(f, 20*np.log10(h/ref), color=color)
axes[0, 0].set(title='Measured global loop gain', xlim=(1000, 1e6), ylim=(-40, 20), ylabel='dB')
axes[0, 0].axhline(0, color='#888', lw=.8)
axes[0, 0].legend(fontsize=8, loc='lower left')
axes[0, 1].set(title='Closed-loop AC response*', xlim=(1000, 1e5), ylim=(-20, 25), ylabel='dB relative to 1 kHz')
for row in burst['cases']:
    if 'negative' in row['name']:
        w = row['waveform']
        axes[1, 0].plot(np.array(w['time_s'])*1000, w['speaker_V'], lw=.9, label=row['name'].replace('loaded-burst-', ''))
axes[1, 0].set(title='Rejected candidate: sustained oscillation', xlim=(9.5, 9.7), xlabel='Time (ms)', ylabel='Speaker voltage (V)')
axes[1, 0].legend(fontsize=8)
by = {r['name']: r for r in summary['cases']}
base = by['loaded-pi47-fb0-lk80-pres0']['analysis']['points']
for prefix, label, color in [('pi100-fb0', 'C22 100 pF', colors[0]), ('pi100-fb22', 'C22 100 pF + 22 pF feedback', colors[2]), ('pi150-fb22', 'C22 150 pF + 22 pF feedback', colors[3])]:
    points = by[f'loaded-{prefix}-lk80-pres0']['analysis']['points']
    hz = [1000, 5000, 10000, 20000]
    delta = [20*np.log10(points[str(f)]['gain_V_V']/base[str(f)]['gain_V_V']) for f in hz]
    axes[1, 1].plot(np.array(hz)/1000, delta, 'o-', color=color, label=label)
axes[1, 1].set(title='Treble change: matched high-leakage / Presence 0', xlabel='Frequency (kHz)', ylabel='dB versus unchanged circuit')
axes[1, 1].legend(fontsize=8)
for ax in axes.flat:
    ax.grid(True, alpha=.2)
for ax in axes[0]:
    ax.set_xlabel('Frequency (Hz)')
fig.suptitle('Loaded transformer feedback — model checks, not a fabrication release', fontsize=15)
fig.supxlabel('*An AC curve can be computed for an unstable circuit; it is not evidence of stable operation.\nNo compensation or damping branch adopted. Transformer, speaker and hardware qualification remain open.', fontsize=9)
fig.savefig(OUT/'loaded-feedback-diagnosis.png', dpi=160)
fig.savefig(OUT/'loaded-feedback-diagnosis.pdf')
