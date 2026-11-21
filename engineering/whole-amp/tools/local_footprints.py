from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'libraries/Renegade_Whole.pretty';D.mkdir(parents=True,exist_ok=True)
head='(footprint "Panasonic_EZPV60506MTC" (version 20241229) (generator "renegade") (layer "F.Cu") (descr "Panasonic EZPV60506MTC; RDL0000C251 p2; body max58x26, H41; P1=52.5 P2=10.2; 4-pin") (attr through_hole)\n'
s=head+'(fp_text reference "REF**" (at 26.25 -10) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))\n(fp_text value "50u 600V" (at 26.25 20) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))\n'
for layer,stroke,margin in [('F.Fab',.1,0),('F.SilkS',.15,.2),('F.CrtYd',.05,1)]:
 s+=f'(fp_rect (start {-2.75-margin} {-7.9-margin}) (end {55.25+margin} {18.1+margin}) (stroke (width {stroke}) (type default)) (fill none) (layer "{layer}"))\n'
for num,x,y in [('1',0,0),('1',0,10.2),('2',52.5,0),('2',52.5,10.2)]:s+=f'(pad "{num}" thru_hole circle (at {x} {y}) (size 4 4) (drill 1.8) (layers "*.Cu" "*.Mask"))\n'
(D/'Panasonic_EZPV60506MTC.kicad_mod').write_text(s+')\n')
