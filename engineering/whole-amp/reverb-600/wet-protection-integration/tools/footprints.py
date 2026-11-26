"""Manufacturer-dimensional axial packages; round leads, hand-formed pitch."""
from pathlib import Path
import json,uuid
M=Path(__file__).resolve().parents[1];R=M.parents[3]
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade-wet-package/'+s))
def main():
 c=json.loads((M/'contract.json').read_text());dest=R/'engineering/component-selection/footprints/Renegade_Selected.pretty'
 for name,g in c['hole_geometry'].items():
  p=g['pitch'];l=g['body_length_max'];d=g['body_diameter_max'];left=(p-l)/2;right=(p+l)/2;dia=g['pad'];courtx=dia/2+.25;courty=max(d/2+.5,dia/2+.25)
  lines=[f'(footprint "{name}" (version 20241229) (generator "renegade_wet_protection") (layer "F.Cu") (descr "Manufacturer max dimensions; hand-form {p}mm pitch. Finished drill tolerance provisional +/-0.1mm.") (attr through_hole)',f'(property "Reference" "REF**" (at {p/2} {-courty-1} 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))',f'(property "Value" "{name}" (at {p/2} {courty+1} 0) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))']
  for layer,width in [('F.Fab',.1),('F.SilkS',.12)]:
   lines += [f'(fp_rect (start {left} {-d/2}) (end {right} {d/2}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}") (uuid "{uid(name+layer)}"))']
   for a,b in [(0,left),(right,p)]:lines += [f'(fp_line (start {a if layer=="F.Fab" or a else dia/2+.25} 0) (end {b if layer=="F.Fab" or b!=p else p-dia/2-.25} 0) (stroke (width {width}) (type default)) (layer "{layer}") (uuid "{uid(name+layer+str(a))}"))']
  if 'BZX55' in name:
   for layer in ['F.Fab','F.SilkS']:lines += [f'(fp_line (start {left+.5} {-d/2}) (end {left+.5} {d/2}) (stroke (width .2) (type default)) (layer "{layer}") (uuid "{uid(name+layer+"band")}"))']
  lines += [f'(fp_rect (start {-courtx} {-courty}) (end {p+courtx} {courty}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd") (uuid "{uid(name+"court")}"))']
  for pin,x in [('1',0),('2',p)]:lines += [f'(pad "{pin}" thru_hole circle (at {x} 0) (size {dia} {dia}) (drill {g["drill"]}) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{uid(name+pin)}"))']
  lines += [')'];(dest/(name+'.kicad_mod')).write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
