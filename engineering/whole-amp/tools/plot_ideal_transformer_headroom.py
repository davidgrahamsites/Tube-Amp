from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parents[1]/'simulation/ideal-transformer-candidate';data=(p/'200n-80m.raw').read_bytes();header,raw=data.split(b'Binary:\n',1);a=np.frombuffer(raw,dtype='<f8').reshape(-1,6);a=a[a[:,0]>=.075][::10]
fig,ax=plt.subplots(2,1,figsize=(10,6),sharex=True,layout='constrained')
ax[0].plot(a[:,0]*1000,a[:,1],label='Tube FX return',lw=1.2,color='#375c9c');ax[0].plot(a[:,0]*1000,a[:,2],label='Passive mix / PI input',lw=1.2,color='#c46b27');ax[0].set_ylabel('Dry signal (V)');ax[0].legend(loc='upper right',fontsize=8)
ax[1].plot(a[:,0]*1000,a[:,3],label='Attenuated reverb input',lw=1.2,color='#218379');ax[1].plot(a[:,0]*1000,a[:,4],label='TI-model buffer output',lw=1,ls='--',color='#723f8c');ax[1].set_ylabel('Reverb send input (V)');ax[1].set_xlabel('Time (ms)');ax[1].legend(loc='upper right',fontsize=8)
for x in ax:x.grid(alpha=.2);x.spines[['top','right']].set_visible(False)
fig.suptitle('Renegade low-frequency reference: ideal transformer, passive dry path',fontsize=13)
fig.text(.5,-.025,'Simulation only • generic valves • ideal ratio transformer / 400 V supply • 200 mV peak, 1 kHz dirty input • excludes real magnetics and HF stability',ha='center',fontsize=8)
fig.savefig(p/'ideal-transformer-headroom.png',dpi=170,bbox_inches='tight');fig.savefig(p/'ideal-transformer-headroom.pdf',bbox_inches='tight')
print('plot saved from',len(raw)//48,'raw points')
