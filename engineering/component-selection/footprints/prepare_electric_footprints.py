"""Exact-part mechanical envelopes from electric-parts-2026-11-21.md.
Run with KiCad bundled Python; generates editable library parts and verification.
"""
from pathlib import Path
import json
import pcbnew as pcb

ROOT=Path(__file__).resolve().parent
LIB=ROOT/'Renegade_Selected.pretty'
PARTS=[
 ('Tyohm_RN_halfWS_68K_P10.16','RN 1/2WS 68K F T/B A1',10.16,7.4,2.9,.9,False),
 ('Yageo_HHV1WS_10M_P17.78','HHV1WSJT-73-10M',17.78,12.5,5,1.2,False),
 ('Vishay_PR01_22K_P12.7','PR01000102202JR500',12.7,8,2.5,.9,False),
 ('Onsemi_1N4007RLG_P10.16','1N4007RLG',10.16,5.2,2.7,1.2,True),
]
reports=[]
def line(x1,y1,x2,y2,layer,width=.12):
 return f'(fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width {width}) (type default)) (layer "{layer}"))'
def rect(x1,y1,x2,y2,layer,width=.12):
 return f'(fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))'
def header(name,mpn,refy):
 return [f'(footprint "{name}" (version 20250108) (generator "renegade_exact_parts") (layer "F.Cu")',
  f'(descr "{mpn}; maximum package envelope; forming/received dimensions require check")',
  f'(fp_text reference "REF**" (at 0 {refy}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))',
  f'(fp_text value "{name}" (at 0 0) (layer "F.Fab") hide (effects (font (size 1 1) (thickness .15))))', '(attr through_hole)']
def pad(n,x,drill,polar=False):
 diam=drill+.8
 return f'(pad "{n}" thru_hole {"rect" if polar and n==1 else "circle"} (at {x} 0) (size {diam} {diam}) (drill {drill}) (layers "*.Cu" "*.Mask"))'
for name,mpn,pitch,length,diam,drill,polar in PARTS:
 x1=(pitch-length)/2;x2=(pitch+length)/2
 lines=header(name,mpn,-diam/2-1.2)
 lines += [rect(x1,-diam/2,x2,diam/2,'F.Fab'),rect(x1,-diam/2,x2,diam/2,'F.SilkS'),
           line(0,0,x1,0,'F.Fab'),line(x2,0,pitch,0,'F.Fab'),
           rect(-(drill+.8)/2-.25,-max(diam/2,(drill+.8)/2)-.25,pitch+(drill+.8)/2+.25,max(diam/2,(drill+.8)/2)+.25,'F.CrtYd',.05),
           pad(1,0,drill,polar),pad(2,pitch,drill,polar)]
 if polar: lines += [line(x1+.6,-diam/2,x1+.6,diam/2,'F.SilkS')]
 lines += [')'];(LIB/(name+'.kicad_mod')).write_text('\n'.join(lines)+'\n')
 reports.append({'name':name,'mpn':mpn,'pitch_mm':pitch,'max_body_mm':[length,diam], 'drill_mm':drill,'polarity':'pad1 cathode' if polar else 'nonpolar'})
name='Aishi_EGW2CM470G16OT_D10.5_P5';mpn='EGW2CM470G16OT';radius=5.25
lines=header(name,mpn,-radius-1.2)
for layer,width in [('F.Fab',.12),('F.SilkS',.12),('F.CrtYd',.05)]:
 r=radius+(.25 if layer=='F.CrtYd' else 0)
 lines.append(f'(fp_circle (center 2.5 0) (end {2.5+r} 0) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))')
lines += [pad(1,0,.9,True),pad(2,5,.9,True),line(-2,-1,-2,1,'F.SilkS'),line(-3,0,-1,0,'F.SilkS'),')']
(LIB/(name+'.kicad_mod')).write_text('\n'.join(lines)+'\n')
reports.append({'name':name,'mpn':mpn,'pitch_mm':5,'max_body_mm':[10.5,18], 'drill_mm':.9,'polarity':'pad1 positive HREF; pad2 negative GND','vent_clearance':'additional space required;18mm body is not installed envelope'})
keep=[]
for row in reports:
 f=pcb.FootprintLoad(str(LIB),row['name']); assert f;keep.append(f)
 ps={q.GetNumber():q for q in f.Pads()};assert set(ps)=={'1','2'}
 assert abs(pcb.ToMM(ps['2'].GetPosition().x-ps['1'].GetPosition().x)-row['pitch_mm'])<1e-5
 assert abs(pcb.ToMM(ps['1'].GetDrillSize().x)-row['drill_mm'])<1e-5
 row['native_parse_pad_pitch_drill_pass']=True
(ROOT/'electric-verification.json').write_text(json.dumps(reports,indent=2)+'\n')
print('Verified',len(reports),'native footprints')
