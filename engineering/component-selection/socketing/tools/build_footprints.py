"""Generate two provisional TE socket library footprints from reviewed bounds.

This factory owns package geometry only. Native integration is a separate tool.
Pin 1 is at (0,0), numbering counterclockwise viewed from component side.
"""
import json
from pathlib import Path
M=Path(__file__).resolve().parents[1]
LIB=M.parent/'footprints/Renegade_Selected.pretty'

def generate(c,e,package):
    p=e['packages'][package];common=e['common'];n=int(package.split('-')[1])
    name=c['assignments'][p['refs'][0]];cx=common['row_spacing_mm']/2;cy=p['pin_span_mm']/2
    w=common['socket_width_max_mm'];length=max(p['socket_length_max_mm'],p['ic_length_max_mm'])
    b=[cx-w/2,cy-length/2,cx+w/2,cy+length/2];m=c['courtyard_margin_mm']
    rect=lambda box,layer,width:f'(fp_rect (start {box[0]:.4f} {box[1]:.4f}) (end {box[2]:.4f} {box[3]:.4f}) (stroke (width {width}) (type solid)) (fill none) (layer "{layer}"))'
    # Fab outline is socket max body. Courtyard encloses both socket and IC max.
    socket=[cx-w/2,cy-p['socket_length_max_mm']/2,cx+w/2,cy+p['socket_length_max_mm']/2]
    text=[f'(footprint "{name}" (version 20260101) (generator "renegade_socket") (layer "F.Cu")',
      '(descr "TE C-2199298 Rev A; engineering draft; compare current A1 and sample before fabrication")',
      '(attr through_hole)',
      '(property "Reference" "REF**" (at 3.81 -4) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))',
      f'(property "Value" "{p["mpn"]}" (at 3.81 {cy}) (layer "F.Fab") hide (effects (font (size 1 1) (thickness .15))))',
      rect(socket,'F.Fab',.1),rect([b[0]-m,b[1]-m,b[2]+m,b[3]+m],'F.CrtYd',.05),
      # End mark clear of through-hole lands; rectangular pad also identifies pin1.
      f'(fp_line (start 2.81 {socket[1]:.4f}) (end 4.81 {socket[1]:.4f}) (stroke (width .12) (type solid)) (layer "F.SilkS"))']
    for pin in range(1,n+1):
        x=0 if pin<=n//2 else common['row_spacing_mm'];y=(pin-1 if pin<=n//2 else n-pin)*common['pitch_mm']
        shape='roundrect' if pin==1 else 'circle';extra=' (roundrect_rratio .15625)' if pin==1 else ''
        text.append(f'(pad "{pin}" thru_hole {shape} (at {x:g} {y:g}) (size {c["pad_size_mm"]} {c["pad_size_mm"]}) (drill {c["drill_mm"]}) (layers "*.Cu" "*.Mask"){extra})')
    return '\n '.join(text)+'\n)\n'

def main():
    c=json.loads((M/'footprint-contract.json').read_text());e=json.loads((M/'socket-envelope.json').read_text())
    assert (c['pad_size_mm']-c['finished_hole_max_mm'])/2-c['provisional_registration_allowance_mm']>=c['minimum_residual_annulus_mm']-1e-9
    for package,p in e['packages'].items():
        name=c['assignments'][p['refs'][0]]; (LIB/(name+'.kicad_mod')).write_text(generate(c,e,package))
        print(name)
if __name__=='__main__':main()
