"""Generate selected Panasonic long-lead packages. Run with KiCad bundled Python."""
import json
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT.parent/'Renegade_Selected.pretty'
def main():
 c=json.loads((ROOT/'package-contract.json').read_text()); report=[]; keep=[]
 for a in c['parts']:
  pitch=a['pitch_mm']; d=a['body_diameter_mm']; radius=d/2
  max_d=d+a['body_diameter_tolerance_mm']; court=max_d/2+c['engineering_assumptions']['courtyard_radial_margin_over_max_body_mm']
  drill=a['finished_hole_mm']; pad=a['pad_diameter_mm']; name=a['footprint']; cx=pitch/2
  lines=[f'(footprint "{name}" (version 20250108) (generator "renegade_exact_parts") (layer "F.Cu")',
   f'(descr "{a["mpn"]}; long-lead; pin1 positive; body max D{max_d} H{a["body_length_mm"]+a["body_length_tolerance_mm"]}; vent space additional; finished drill {drill}+/-0.10mm requires fabricator confirmation")',
   '(attr through_hole)',
   f'(fp_text reference "REF**" (at {cx} {-court-1}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))',
   f'(fp_text value "{a["mpn"]}" (at {cx} 0) (layer "F.Fab") hide (effects (font (size 1 1) (thickness .15))))']
  for layer,r,w in [('F.Fab',radius,.1),('F.SilkS',max_d/2,.12),('F.CrtYd',court,.05)]:
   lines.append(f'(fp_circle (center {cx} 0) (end {cx+r} 0) (stroke (width {w}) (type default)) (fill none) (layer "{layer}"))')
  # Plus sign outside left of body, away from solder pads.
  px=cx-max_d/2-.7
  for x1,y1,x2,y2 in [(px-.3,0,px+.3,0),(px,-.3,px,.3)]:
   lines.append(f'(fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width .12) (type default)) (layer "F.SilkS"))')
  for n,x in [(1,0),(2,pitch)]:
   lines.append(f'(pad "{n}" thru_hole {"rect" if n==1 else "circle"} (at {x} 0) (size {pad} {pad}) (drill {drill}) (layers "*.Cu" "*.Mask"))')
  lines.append(')'); (LIB/(name+'.kicad_mod')).write_text('\n'.join(lines)+'\n')
  f=p.FootprintLoad(str(LIB),name); keep.append(f); ps={q.GetNumber():q for q in f.Pads()}
  leadmax=a['round_lead_diameter_mm']+a['lead_tolerance_mm']; tol=c['engineering_assumptions']['finished_hole_tolerance_mm']; clear=drill-tol-leadmax
  checks={'two_pads':set(ps)=={'1','2'},'native_pitch':abs(p.ToMM(ps['2'].GetPosition().x-ps['1'].GetPosition().x)-pitch)<1e-6,
   'round_drills':all(q.GetDrillSize().x==q.GetDrillSize().y and abs(p.ToMM(q.GetDrillSize().x)-drill)<1e-6 for q in ps.values()),
   'minimum_hole_clearance':clear>=.2-1e-9,
   'positive_square':ps['1'].GetShape()==p.PAD_SHAPE_RECT,'max_body_courtyard':court>=max_d/2+.5-1e-9}
  assert all(checks.values()),(name,checks)
  report.append(dict(mpn=a['mpn'],checks=checks,lead_max_mm=leadmax,finished_hole_min_mm=drill-tol,insertion_clearance_mm=round(clear,3),max_body_mm=[max_d,round(a['body_length_mm']+1.5,3)],courtyard_diameter_mm=round(2*court,3)))
 (ROOT/'results/dimensions.json').write_text(json.dumps({'parts':report,'kicad':p.Version(),'fabrication_ready':False,'open':'Fabricator tolerances, formed leads, vent space, routing and populated fit'},indent=2)+'\n')
 print('Three exact packages passed native dimensional checks')
if __name__=='__main__':main()
