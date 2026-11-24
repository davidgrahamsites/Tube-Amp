"""Draw the retained CAD poses and declared support budgets, not final artwork."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
ROOT=Path(__file__).resolve().parents[1];j=json.loads((ROOT/'review/board-fit-diagnostic.json').read_text());inv=json.loads((ROOT.parent/'pcb-measured-r/review/mechanical-inventory.json').read_text())
fig,axes=plt.subplots(2,1,figsize=(11,8),layout='constrained');colors={'Main':'#d5e9f5','Reverb':'#bfe3cd','Power':'#f1d3aa','Control':'#dbd0ed'}
for ax,tier in zip(axes,j['planes']):
    w,d,_=j['assumed_datum_mm'];sw,sd=tier['required_support_budget_mm']
    ax.add_patch(Rectangle((0,0),w,d,fill=False,ec='#323a45',lw=2,label='Assumed cabinet width/depth'))
    ax.add_patch(Rectangle((0,0),sw,sd,fill=False,ec='#bb3434',lw=1.8,ls='--',label='Trial support + flange budget'))
    for name in tier['boards']:
        q=j['poses'][name];x,y,_=q['bbox_min_mm'];bw,bd,_=q['bbox_size_mm'];ax.add_patch(Rectangle((x,y),bw,bd,fc=colors[name],ec='#43515c'))
        for hole in inv['boards'][name]['mounting_holes']:
            hx,hy=hole['at_from_outline_mm'];sx,sy,_=inv['boards'][name]['size_mm']
            if q['rotation_z_deg']:hx,hy=sy-hy,hx
            ax.add_patch(Circle((x+hx,y+hy),hole['diameter_mm']/2,fc='white',ec='#43515c',lw=.6))
        ax.text(x+bw/2,y+bd/2,f'{name}\n{bw:g} × {bd:g} mm',ha='center',va='center',fontsize=11)
    ax.set(xlim=(-5,530),ylim=(200,-5),aspect='equal',xlabel='X, left to right (mm)',ylabel='Y, front to rear (mm)',title=f"{' + '.join(tier['boards'])}: support budget {sw:g} × {sd:g} mm; excess {tier['width_excess_mm']:g} mm width / {tier['depth_excess_mm']:g} mm depth")
    ax.legend(loc='lower right',fontsize=8)
fig.suptitle('Current PCB fit diagnostic — NOT a chassis drawing\nDepth datum, components, removal paths and drill access remain unqualified',fontsize=12)
fig.savefig(ROOT/'review/board-fit-diagnostic.png',dpi=160);fig.savefig(ROOT/'review/board-fit-diagnostic.pdf');plt.close(fig)
