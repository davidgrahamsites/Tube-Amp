"""Guarded one-time R215 addition. Does not regenerate the existing native design."""
import copy,hashlib,json,subprocess,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];M=Path(__file__).resolve().parents[1]
BASE='5e8b78d0315b970baab26415d5225e15909db41a'
sys.path.insert(0,str(M.parent/'tools'))
import native_sexpr as v
parse,children,field=v.parse,v.children,v.field
Q=json.dumps
UID=lambda name:str(uuid.uuid5(uuid.NAMESPACE_URL,'renegade/preload/2026-11-24/'+name))
def emit(x):return '('+' '.join(emit(i) if isinstance(i,list) else str(i) for i in x)+')'
def prop(s,name):return next(p for p in children(s,'property') if p[1]==Q(name))
def renew(x):
 for t in x:
  if isinstance(t,list):
   if t[0]=='uuid':t[1]=UID(t[1])
   else:renew(t)
def main():
 assert sys.argv[1:]==['--apply']
 paths=['engineering/whole-amp/reverb-600/circuit.json','engineering/whole-amp/reverb-600/cad/08_control_supply.kicad_sch','engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb']
 old={p:(ROOT/p).read_text() for p in paths}
 for p,t in old.items():assert t==subprocess.check_output(['/usr/bin/git','show',BASE+':'+p],cwd=ROOT).decode(),p
 circuit=json.loads(old[paths[0]]);assert not any(c['reference']=='R215' for c in circuit['components'])
 name='UNI_ROYAL_MF0W4_P12.70mm';fp='Renegade_Selected:'+name
 ds='https://www.uni-royal.cn/images/upload/UniroyalCatalog2024.06.07.pdf'
 circuit['components'].append(dict(project='Renegade_220V_Reverb',sheet='08_control_supply',reference='R215',unit=1,value='820',symbol='Device_R',pins={'1':'+5V','2':'GND'},source='VAL-027 auxiliary minimum-load repair',rating='0.25W; 1%; 50ppm/C; 5V preload',status='engineering integrated; domestic procurement and populated qualification pending',datasheet=ds,footprint=fp,selected_mpn='MFR0W4F8200A50'))
 a=parse(old[paths[1]]);template=parse((ROOT/'engineering/whole-amp/reverb-600/cad/09b_latches_drivers.kicad_sch').read_text())
 lib=next(x for x in children(field(template,'lib_symbols'),'symbol') if x[1]=='"Renegade_Draft:Device_R"')
 res=copy.deepcopy(next(x for x in children(template,'symbol') if prop(x,'Reference')[2]=='"R332"'));renew(res)
 field(res,'at')[1:]=['464.82','83.82','0'];rid=field(res,'uuid')[1]
 vals={'Reference':'R215','Value':'820','Footprint':fp,'Datasheet':ds,'Source':'VAL-027','Rating':'0.25W 1%','Design_status':'Engineering; procurement pending','Assembly':'Control'}
 for p in children(res,'property'):
  p[2]=Q(vals[p[1].strip('"')]);field(p,'at')[1:]=['469.90','83.82','0']
 field(prop(res,'Reference'),'at')[2]='81.28';field(prop(res,'Value'),'at')[2]='85.09'
 inst=field(field(field(res,'instances'),'project'),'path');inst[1]=Q('/97ca3088-a174-52f9-956d-0a38bb8e2f56/06576ab5-afa1-5e26-bb42-7027176470f3');field(inst,'reference')[1]='"R215"'
 gnd=copy.deepcopy(next(x for x in children(a,'symbol') if prop(x,'Reference')[2]=='"#PWR5716"'));renew(gnd)
 ox,oy=map(float,field(gnd,'at')[1:3]);dx,dy=464.82-ox,91.44-oy
 for t in [field(gnd,'at')]+[field(p,'at') for p in children(gnd,'property')]:t[1]=str(round(float(t[1])+dx,5));t[2]=str(round(float(t[2])+dy,5))
 prop(gnd,'Reference')[2]='"#PWR5717"';field(field(field(field(gnd,'instances'),'project'),'path'),'reference')[1]='"#PWR5717"'
 extra=[emit(res),emit(gnd)]
 for i,(start,end) in enumerate([((449.58,60.96),(464.82,60.96)),((464.82,60.96),(464.82,80.01)),((464.82,87.63),(464.82,91.44))]):extra.append(f'(wire (pts (xy {start[0]} {start[1]}) (xy {end[0]} {end[1]})) (stroke (width 0) (type default)) (uuid {UID("wire"+str(i))}))')
 extra.append(f'(junction (at 449.58 60.96) (diameter 0) (color 0 0 0 0) (uuid {UID("junction")}))')
 extra.append(f'(text "5V minimum load\\n820 ohm / 1% / 0.25W" (at 486.41 83.82 0) (effects (font (size 1.2 1.2)) (justify left top)) (uuid {UID("note")}))')
 sch=old[paths[1]].replace('(lib_symbols ','(lib_symbols '+emit(lib)+' ',1).rstrip();sch=sch[:-1]+' '+' '.join(extra)+')\n'
 # Package: manufacturer's worst-case 7.5 x 2.5 body, 0.59mm round lead.
 # 0.90 +/-0.10 finished hole leaves >=0.21mm diametric clearance.
 fptext=f'''(footprint "{name}" (version 20260101) (generator "renegade_preload") (layer "F.Cu")
 (descr "UNI-ROYAL MF0W4; max body7.5x2.5; round lead0.54+/-0.05; formed pitch12.7; finished hole0.90+/-0.10")
 (property "Reference" "REF**" (at 6.35 -2.25) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
 (property "Value" "820" (at 6.35 2.25) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))
 (attr through_hole)
 (fp_rect (start 2.6 -1.25) (end 10.1 1.25) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))
 (fp_rect (start 2.5 -1.35) (end 10.2 1.35) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))
 (fp_rect (start -1.15 -1.5) (end 13.85 1.5) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))
 (fp_line (start 0 0) (end 2.6 0) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
 (fp_line (start 10.1 0) (end 12.7 0) (stroke (width 0.1) (type solid)) (layer "F.Fab"))
 (pad "1" thru_hole circle (at 0 0) (size 1.8 1.8) (drill 0.9) (layers "*.Cu" "*.Mask"))
 (pad "2" thru_hole circle (at 12.7 0) (size 1.8 1.8) (drill 0.9) (layers "*.Cu" "*.Mask")))\n'''
 f=parse(fptext);f[1]=Q(fp);f=[x for x in f if not isinstance(x,list) or x[0] not in ['version','generator']]
 f.extend([['uuid',Q(UID('board-footprint'))],['at','196.654','75.5'],['path',Q(inst[1].strip('"')+'/'+rid)]])
 prop(f,'Reference')[2]='"R215"';f.append(['property','"Selected_MPN"','"MFR0W4F8200A50"',['at','0','0','0'],['layer','"F.Fab"'],['hide','yes'],['effects',['font',['size','1','1']]]])
 for pad,net in zip(children(f,'pad'),['+5V','GND']):pad.extend([['net',Q(net)],['uuid',Q(UID('pad'+pad[1]))]])
 boardextra=[emit(f)];routes=[('F.Cu','+5V',(196.654,68.125),(196.654,75.5))]
 points=[(209.354,75.5),(209.354,77),(208.354,78),(195.114,78),(194.114,77),(194.114,68.125)]
 routes.extend(('B.Cu','GND',p,q) for p,q in zip(points,points[1:]))
 for i,(layer,net,p,q) in enumerate(routes):boardextra.append(f'(segment (start {p[0]} {p[1]}) (end {q[0]} {q[1]}) (width 0.4) (layer "{layer}") (net "{net}") (uuid "{UID("track"+str(i))}"))')
 board=old[paths[2]].rstrip();board=board[:-1]+'\n'+'\n'.join(boardextra)+')\n'
 for text in [sch,board,fptext]:parse(text)
 changes={paths[0]:json.dumps(circuit,indent=2)+'\n',paths[1]:sch,paths[2]:board}
 for p,t in changes.items():(ROOT/p).write_text(t)
 (ROOT/f'engineering/component-selection/footprints/Renegade_Selected.pretty/{name}.kicad_mod').write_text(fptext)
 covp=ROOT/'engineering/component-selection/coverage.json';cov=json.loads(covp.read_text());assert not any('R215' in c['refs'] for c in cov)
 cov.append(dict(id='P129',refs=['R215'],value='820',requirement='5V minimum load; 0.25W 1% 50ppm/C',candidate_mpns=['MFR0W4F8200A50'],selected_mpn='MFR0W4F8200A50',status='engineering selected and native integrated; domestic stock/address verification pending',selection_evidence='../whole-amp/aux-supply/preload-review.md',package_evidence='../whole-amp/aux-supply/results/preload/uniroyal-mf-excerpt.pdf'));covp.write_text(json.dumps(cov,indent=2)+'\n')
 (M/'results/preload/integration.json').write_text(json.dumps(dict(baseline_commit=BASE,added_reference='R215',symbol_uuid=rid,mpn='MFR0W4F8200A50',before_sha256={p:hashlib.sha256(t.encode()).hexdigest() for p,t in old.items()},after_sha256={p:hashlib.sha256(t.encode()).hexdigest() for p,t in changes.items()},fabrication_ready=False),indent=2)+'\n')
 print('R215 added: source, native schematic, Control PCB, exact-family footprint and P129.')
if __name__=='__main__':main()
