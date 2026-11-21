"""Render the canonical 2D fit screen; never a drilling template."""
from pathlib import Path
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

root = Path(__file__).resolve().parents[1]
r = json.loads((root/'fit-register.json').read_text())
fig, axs = plt.subplots(1, 3, figsize=(14, 5), layout='constrained')
b = r['baffle']
s = r['speaker_reference']
ax = axs[0]
ax.add_patch(Rectangle((0,0), b['width_mm'], b['height_mm'], fill=False, lw=2))
cx, cy = b['speaker_center_x_from_left_as_drawn_mm'], b['speaker_center_y_from_top_inferred_mm']
ax.add_patch(Circle((cx,cy), b['cutout_diameter_mm']/2, fill=False, color='gray'))
for dia, hole, color, label in [(b['speaker_hole_circle_mm'],5,'#b64235','Cabinet 312 mm PCD'),
                               (s['bolt_circle_mm'],7.9,'#236b95','Speaker 297 mm PCD')]:
    ax.add_patch(Circle((cx,cy),dia/2,fill=False,ls='--',color=color,label=label))
    for angle in [45,135,225,315]:
        x=cx+dia/2*math.cos(math.radians(angle)); y=cy+dia/2*math.sin(math.radians(angle))
        ax.add_patch(Circle((x,y),hole/2,color=color))
ax.set(xlim=(-15,485),ylim=(395,-15),title='Baffle: mounting mismatch',xlabel='mm; front-view coordinates')
ax.legend(loc='upper right', fontsize=8)
colors={'Main':'#d2e7df','Reverb':'#e9d5aa','Power':'#f0c8c2','Control':'#cdddec'}
for ax, key in zip(axs[1:], ['plane_A','plane_B']):
    w,h=r['layout_options']['two_plane_board_only']['assumed_tray_mm']
    ax.add_patch(Rectangle((0,0),w,h,fill=False,lw=2,ls='--'))
    x=5
    for name in r['layout_options']['two_plane_board_only'][key]:
        bw,bh,_=r['boards'][name]
        ax.add_patch(Rectangle((x,5),bw,bh,facecolor=colors[name],edgecolor='#35424c'))
        ax.text(x+bw/2,5+bh/2,f'{name}\n{bw} × {bh}',ha='center',va='center')
        x+=bw+r['layout_options']['two_plane_board_only']['gap_mm']
    ax.set(xlim=(-15,485),ylim=(240,-15),title=key.replace('_',' ').title()+' — board-only proposal',xlabel='Assumed tray 468 × 190 mm')
for ax in axs:
    ax.set_aspect('equal');ax.spines[['top','right']].set_visible(False)
fig.suptitle('Renegade cabinet fit screen — NOT A FIT RELEASE',fontsize=17,weight='bold')
fig.text(.5,.01,'No tube, transformer, populated-height, chassis or cable clearance is established. Two planes are not a 3D fit proof.',ha='center',fontsize=10)
for suffix in ['png','pdf']:
    fig.savefig(root/f'review/fit-screen.{suffix}',dpi=160,bbox_inches='tight')
