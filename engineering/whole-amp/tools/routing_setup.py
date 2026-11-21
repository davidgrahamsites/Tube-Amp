from pathlib import Path as _GuardPath
if (_GuardPath(__file__).resolve().parents[1]/'NATIVE_EDIT_GUARD').exists():
 raise RuntimeError('Saved native CAD is authoritative. Preserve it before intentionally regenerating this historical experiment.')
from pathlib import Path
import pcbnew as pcb,json,re,sys
R=Path(__file__).resolve().parents[1];data=json.loads((R/'board-plan.json').read_text())
HV={'B_EARLY','B_PRE','CL_P1','CL_P2','CL_TONE','DR_P1','DR_P2','DR_P3','DR_CF','DR_TONE','PI_P1','PI_P2','PI_K','PI_TAIL_TOP','NFB_NODE','PI_G1','PI_G2','HV_A','HV_B','HV_MID_A','HV_MID_B','B_RECT','B_RAW','B_MAIN','B_SCREEN','HV_CAP_MID'}
for name in [sys.argv[1]]:
 out=R/'pcb'/name;pn='Renegade_'+name;path=out/(pn+'.kicad_pcb');b=pcb.LoadBoard(str(path));nets=[n.GetNetname() for n in b.GetNetInfo().NetsByNetcode().values() if n.GetNetCode()]
 hv=sorted(set(nets)&HV);lv=sorted(set(nets)-HV)
 rule='(version 1)\n(rule "Default clearance" (constraint clearance (min 0.25mm)))\n(rule "Tracks" (constraint track_width (min 0.30mm)))\n(rule "Board edge" (constraint edge_clearance (min 1.0mm)))\n'
 if hv:
  cond=' || '.join("A.NetName == '"+n+"' || B.NetName == '"+n+"'" for n in hv)
  rule+='(rule "HV functional copper spacing" (condition "'+cond+'") (constraint clearance (min 5.5mm)))\n'
 (out/(pn+'.kicad_dru')).write_text(rule)
 project={'meta':{'filename':pn+'.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.25,'min_track_width':.3,'min_via_diameter':.6,'min_through_hole_diameter':.3,'min_hole_clearance':.25,'min_copper_edge_clearance':1}}},'net_settings':{'classes':[{'name':'Default','clearance':.25,'track_width':.4,'via_diameter':.6,'via_drill':.3,'nets':lv},{'name':'HV','clearance':5.5,'track_width':.6,'via_diameter':.6,'via_drill':.3,'nets':hv}]}}
 (out/(pn+'.kicad_pro')).write_text(json.dumps(project,indent=2));dsn=out/(pn+'.dsn');
 for track in list(b.GetTracks()):b.Remove(track);track.thisown=True
 assert pcb.ExportSpecctraDSN(b,str(dsn));s=dsn.read_text();start=s.index('    (class ');depth=0;end=None
 for i in range(start,len(s)):
  if s[i]=='(':depth+=1
  if s[i]==')':
   depth-=1
   if depth==0 and i>start+5:end=i+1;break
 classes=[]
 for cn,ns,clear,width in [('Default',lv,250,400),('HV',hv,5500,600)]:
  if ns:classes.append('    (class '+cn+' '+' '.join('"'+n+'"' for n in ns)+' (circuit (use_via "Via[0-1]_600:300_um")) (rule (width '+str(width)+') (clearance '+str(clear)+')))')
 s=s[:start]+'\n'.join(classes)+s[end:];s=s.replace('(width 200)','(width 400)').replace('(clearance 200)','(clearance 250)').replace('(clearance 50 (type smd_smd))','(clearance 250 (type smd_smd))');w,h=data['boards'][name]['size'];m=1000
 s=re.sub(r'\(path pcb 0[^)]+\)',f'(path pcb 0 {w*1000-m} {-h*1000+m} {m} {-h*1000+m} {m} {-m} {w*1000-m} {-m} {w*1000-m} {-h*1000+m})',s,count=1)
 dsn.write_text(s)
 print(name,len(hv),'HV nets',len(lv),'other nets')
