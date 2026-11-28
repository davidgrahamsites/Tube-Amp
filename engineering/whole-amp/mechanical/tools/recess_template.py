"""Make the CB-010 full-size card fit kit from the CB-009 cabinet stack."""
import json
from pathlib import Path

import pymupdf as pdf

from recess_guide import add_guide

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'review'
MM = 72 / 25.4
INK = (.10, .17, .21)
FOLD = (.0, .35, .42)
GUIDE = (.45, .46, .46)


def point(x, y):
    return pdf.Point(x*MM, y*MM)


def line(page, x, y, xx, yy, color=INK, dashed=False):
    page.draw_line(point(x,y),point(xx,yy),color=color,width=.65,
                   dashes='[4 3] 0' if dashed else None)


def label(page,x,y,s,size=10,bold=False,color=INK):
    page.insert_text(point(x,y),s,fontsize=size,fontname='hebo' if bold else 'helv',color=color)


def rectangle(page,x,y,w,h,color=INK,dashed=False):
    page.draw_rect(pdf.Rect(point(x,y),point(x+w,y+h)),color=color,width=.65,
                   dashes='[4 3] 0' if dashed else None)


def sheet(doc, number, name, instruction):
    page=doc.new_page(width=210*MM,height=297*MM)
    label(page,12,15,'RENEGADE    /    CB-010     |     CABINET FIT KIT',9,True,FOLD)
    label(page,12,27,name,21,True)
    label(page,12,36,instruction)
    line(page,12,42,198,42,GUIDE)
    label(page,12,244,'Scale check on every sheet',12,True)
    label(page,12,251,'Print A4 at Actual Size / 100%. Disable page fitting. Check both bars with a ruler.',9)
    line(page,15,265,115,265)
    for x in (15,115): line(page,x,263,x,267)
    label(page,48,273,'100 mm horizontal',9)
    line(page,201,55,201,255)
    for y in (55,255): line(page,199,y,203,y)
    label(page,141,265,'200 mm vertical at right',9)
    label(page,12,285,'FIT MODEL ONLY   /   Solid outside edge = cut. Dashed teal line = fold.',8,True,FOLD)
    label(page,183,285,f'{number+2} / 5',8)
    return page


def main():
    receipt=json.loads((OUT/'rear-cover-sink.json').read_text())
    p,fit=receipt['parameters'],receipt['direct_cover_on_check']
    w,h=receipt['stack_mm']['guarded_elevation_w_h']
    depth=receipt['stack_mm']['need_contact']
    pocket=fit['trial_recess_mm']
    width=fit['trial_recess_width_mm']
    height=p['tray_height']
    face=p['front_gap']+p['tray_depth']-pocket
    blocked=face+depth
    target=blocked+p['cover_gap_min']
    doc=pdf.open()
    add_guide(doc,fit,p,(MM,point,line,label,rectangle,INK,FOLD,GUIDE))
    a=sheet(doc,1,'Recessed wall','Cut one piece. Keep the print facing the rear cover.')
    x,y=(210-width)/2,67
    rectangle(a,x-pocket,y,width+2*pocket,height)
    for xx in (x,x+width):line(a,xx,y,xx,y+height,FOLD,True)
    gx,gy=x+(width-w)/2,y+(height-h)/2
    rectangle(a,gx,gy,w,h,GUIDE)
    label(a,gx+6,gy+22,'Seat the open end of the page 4 box here.',12,True)
    label(a,gx+6,gy+32,f'Guard envelope   {w:.1f} x {h:.1f} mm',10)
    label(a,gx+6,gy+42,f'Pocket face   {width:.1f} x {height:g} mm',10)
    label(a,12,171,'1   Fold both 15 mm side strips toward you through 90 degrees.',11,True)
    label(a,12,180,'The free strip edges represent the original flat tray wall. The pocket face sits forward.')
    label(a,12,192,'2   Centre the guard on the grey outline and tape its open end to this face.',11,True)
    label(a,12,201,'Leave both ends of the recess open for the airflow test.')
    label(a,12,217,'Keep this mock-up removable. Use tape on card only.')
    b=sheet(doc,2,'Guard, heatsink and bracket','Make one open-backed box. Its outside surfaces represent the occupied space.')
    x,y=(210-w)/2,87
    outline=[(x,y-depth),(x+w,y-depth),(x+w,y),(x+w+depth,y),(x+w+depth,y+h),
             (x+w,y+h),(x+w,y+h+depth),(x,y+h+depth),(x,y+h),(x-depth,y+h),
             (x-depth,y),(x,y)]
    for start,end in zip(outline,outline[1:]+outline[:1]):line(b,*start,*end)
    rectangle(b,x,y,w,h,FOLD,True)
    label(b,x+8,y+26,'GUARD FACE',15,True)
    label(b,x+8,y+37,'This face points toward the wood.')
    label(b,x+8,y+48,f'Outside depth from recessed wall   {depth:.1f} mm')
    label(b,12,193,'3   Cut around the cross. Fold the four flaps away from the printed face.',11,True)
    label(b,12,202,'Tape the corner seams. Leave the back open and attach it to the page 3 wall.')
    label(b,12,213,'Use stiff card. Check the finished width, height and depth against these labels.')
    label(b,12,222,'Count protruding tape, fasteners or hardware in the fit test.')
    c=sheet(doc,3,'Position and clearance','Use these two gauges at the proposed heatsink position in the empty cabinet.')
    x,y=21,65
    rectangle(c,x,y,face,22)
    label(c,x+4,y+9,'A     Speaker-board face',10,True)
    label(c,x+4,y+16,f'A to recessed wall   {face:.1f} mm')
    label(c,x+face-18,y+9,'WALL',9,True)
    rectangle(c,x,109,target,21)
    line(c,x+blocked,109,x+blocked,130,GUIDE)
    label(c,x+4,118,'A     Minimum clear depth',10,True)
    label(c,x+4,125,f'{target:.1f} mm includes the 5 mm cover gap.')
    label(c,x+blocked-8,103,'5 mm tip',9,True,FOLD)
    label(c,12,150,'4   Set the wall position.',11,True)
    label(c,12,158,'Rest the first gauge against the flat rear face of the speaker board at A.')
    label(c,12,165,'Put the recessed wall at its other end. Centre the guard about 45 mm below the top.')
    label(c,12,172,'Hold the wall on fixed supports. Refit the upper wooden cover with its screws.')
    label(c,12,184,'5   Check the whole guard.',11,True)
    label(c,12,192,'Slide the second gauge level at the centre, corners and any fastener or cleat.')
    label(c,12,199,'It must fit from A to the nearest obstruction without bending. Keep the tip intact.')
    label(c,12,206,'Confirm the cover and cassette each withdraw freely and the slots remain usable.')
    label(c,12,220,'Observed minimum gap __________ mm     Cover clears __________     Date __________',9)
    doc.set_metadata({'title':'Renegade CB-010 | Recessed Fischer heatsink fit kit','subject':'A4 actual-size card mock-up'})
    doc.save(OUT/'fischer-recess-fit-template.pdf',garbage=4,deflate=True,no_new_id=True)
    doc.close()


if __name__=='__main__':
    main()
