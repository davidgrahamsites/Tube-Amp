"""Read-only comparison of selected footprints to preserved routed native boards."""
from pathlib import Path
import pcbnew,json,hashlib,csv
p=Path(__file__).resolve().parent;root=p.parents[2];selection=json.loads((p.parent/'coverage.json').read_text());lib=p/'Renegade_Selected.pretty';rows=[]
boards=[root/'engineering/whole-amp/pcb'/n/('Renegade_'+n+'.kicad_pcb') for n in ['Main','Power','Control']]+[root/'engineering/solid-state-reverb/pcb/Renegade_Reverb.kicad_pcb']
items={};hashes={};loaded=[]
for path in boards:
 hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest();b=pcbnew.LoadBoard(str(path));loaded.append(b)
 for f in b.GetFootprints():items[f.GetReference()]=(path,f)
for group in selection:
 mpn=group.get('selected_mpn')
 if not mpn:continue
 if mpn.startswith('CD11AT'):fp='CH_CD11AT_25u_400V_D8_P3.5'
 elif mpn.startswith('KP'):fp='KYET_'+mpn
 elif mpn.startswith('3296W'):fp='Bourns_3296W_TopAdjust_P2.54'
 elif mpn.startswith(('MFR50S','MF0207')):fp='Yageo_MFR50S_MF0207_P10.16'
 elif mpn.startswith('FMP200'):fp='Yageo_FMP200_L9.0_D3.9_P15.24'
 elif mpn.startswith('NFA200'):fp='Samyoung_NFA_10u_200V_D8_P3.5'
 else:continue
 f=pcbnew.FootprintLoad(str(lib),fp);assert f,fp
 for ref in group['refs']:
  if ref in ['R36','R37']:
   rows.append(dict(reference=ref,mpn=mpn,board='chassis/socket-local',old_footprint='not applicable',selected_footprint='not applicable: mount at EL34 grid pin',old_pad_count=0,new_pad_count=0,action='update assembly BOM; retain socket-local placement; check insulation/support/lead length'))
   continue
  assert ref in items,ref
  board,old=items[ref]
  rows.append(dict(reference=ref,mpn=mpn,board=str(board.relative_to(root)),old_footprint=str(old.GetFPID().GetLibItemName()),selected_footprint='Renegade_Selected:'+fp,old_pad_count=len(list(old.Pads())),new_pad_count=len(list(f.Pads())),action='replace with preserved net/pad mapping; reroute as needed; verify thermal/courtyard/netlist/ERC/DRC; not applied'))
for path in boards:assert hashlib.sha256(path.read_bytes()).hexdigest()==hashes[str(path.relative_to(root))]
(p/'integration-manifest.json').write_text(json.dumps({'status':'PLANNED ONLY; native boards unchanged','native_board_sha256':hashes,'changes':rows},indent=2)+'\n')
with (p/'integration-manifest.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(len(rows),'references mapped against four native boards; hashes unchanged')
