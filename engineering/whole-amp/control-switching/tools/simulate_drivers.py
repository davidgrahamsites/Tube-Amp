"""Bounded relay switching surrogate. NOT an AOS/Omron device model.
Level-1 MOS conduction uses a conservative engineering multiplier; nonlinear gate charge,
avalanche, armature motion and EMI are not qualified by this screen.
"""
import hashlib,itertools,json,sys
from pathlib import Path
M=Path(__file__).resolve().parents[1];sys.path.insert(0,str(M.parent/'tools'))
import spice_runtime as s

def cases(c):
 for count,L,wire,suppression in itertools.product(c['coil']['parallel_counts'],c['coil']['inductance_reference_H'],c['coil']['wire_inductance_screen_H'],['remote_only','remote_and_local']):
  yield dict(id=f'{count}coils-L{L:g}-wire{wire:g}-{suppression}',count=count,L=L,wire=wire,suppression=suppression,temperature=-25,voltage=12.6,cap_multiplier=.5)
 for count in [1,2]:
  yield dict(id=f'{count}coils-hot-lowrail',count=count,L=3.99,wire=100e-6,suppression='remote_and_local',temperature=70,voltage=11.4,cap_multiplier=2)

def run(c,case,step):
 d=c['driver_candidate'];coil=c['coil']
 resistance=coil['resistance_23C_ohm']*(1+(-coil['resistance_tolerance'] if case['temperature']<23 else coil['resistance_tolerance']))*(1+coil['copper_tcr_screen_per_C']*(case['temperature']-23))
 # Each remote coil retains its own native diode. One optional local clamp spans
 # driver drain to the same +12 V rail; rail is ideal here (explicit limitation).
 branch='\n'.join(f'Rcoil{i} supply coil{i} {resistance}\nLcoil{i} coil{i} remote {case["L"]}\nDfly{i} remote supply DGEN' for i in range(case['count']))
 clamp='Dlocal drain supply DGEN' if case['suppression']=='remote_and_local' else '* No local controller clamp'
 f=case['cap_multiplier'];ron=d['rds_max_25C_at_2p5V_ohm']*d['rds_hot_multiplier_screen']
 deck=f'''AO3400A engineering surrogate; no vendor MOSFET or mechanical relay model
V12 supply 0 {case['voltage']}
Vlogic logic 0 PWL(0 0 .001 0 .0010001 3.84 .06 3.84 .0600001 0 .10 0)
Rdriver logic out 165
Rgate out gate 1010
Rdown gate 0 99000
Cgs gate 0 {(d['ciss_typ_F']-d['crss_typ_F'])*f}
Cgd gate drain {d['crss_typ_F']*f}
Cds drain 0 {(d['coss_typ_F']-d['crss_typ_F'])*f}
Mfet drain gate 0 0 FET
.model FET NMOS(Level=1 Vto=1.45 Kp={1/(ron*(2.5-1.45))} Lambda=0 Rd=.005 Rs=.005)
Dbody 0 drain DGEN
Lwire drain wire {case['wire']}
Rwire wire remote {coil['wire_resistance_screen_ohm']}
{branch}
{clamp}
.model DGEN D(Is=1n N=1.8 Rs=.2 Cjo=15p Tt=2u)
.options method=gear maxord=2 reltol=1e-4 abstol=1e-10 vntol=1e-7
.save v(drain) v(gate) i(lwire) i(lcoil0) v(remote)
.tran {step} .10 0 {step}
.end
'''
 s.cmd('destroy all');s.load(deck);s.cmd('run')
 t=s.vector('time');drain=s.vector('v(drain)');gate=s.vector('v(gate)');i=s.vector('i(lcoil0)');iw=s.vector('i(lwire)')
 assert t[-1]>=.1-1e-9
 before=[j for j,x in enumerate(t) if .055<x<.059]
 steady=sum(i[j] for j in before)/len(before)
 release=next((t[j]-.06 for j in range(len(t)) if t[j]>.06 and i[j]<steady*.05),None)
 flags=[]
 if max(drain)>24:flags.append('VDS_exceeds_24V_engineering_target')
 if max(drain)>30:flags.append('VDS_exceeds_30V_rating')
 if max(gate)>12 or min(gate)<-12:flags.append('VGS_exceeds_rating')
 if release is None:flags.append('coil_not_below_5percent_by_end')
 kcl=max(abs(iw[j]+case['count']*i[j]) for j in before)
 assert kcl<1e-6,kcl
 return dict(case=case,completed_time_s=t[-1],max_vds_V=max(drain),min_vds_V=min(drain),max_vgs_V=max(gate),min_vgs_V=min(gate),max_total_current_A=max(abs(x) for x in iw),steady_per_coil_A=steady,steady_kcl_error_A=kcl,current_decay_to_5percent_s=release,flags=flags,deck_sha256=hashlib.sha256(deck.encode()).hexdigest()),deck

def main():
 c=json.loads((M/'contract.json').read_text());rows=[];decks={};refinements=[]
 try:
  for case in cases(c):
   row,deck=run(c,case,2e-6);rows.append(row);decks[case['id']]=deck
   print(case['id'],round(row['max_vds_V'],4),row['flags'],flush=True)
  targets=sorted(rows,key=lambda r:r['max_vds_V'],reverse=True)[:2]+[max((r for r in rows if r['case']['suppression']=='remote_and_local'),key=lambda r:r['max_vds_V'])]
  for row in targets:
   fine,deck=run(c,row['case'],.5e-6);decks[row['case']['id']+'-fine']=deck
   finer,deck=run(c,row['case'],.125e-6);decks[row['case']['id']+'-finer']=deck
   delta=abs(finer['max_vds_V']-fine['max_vds_V'])
   refinements.append(dict(id=row['case']['id'],coarse_to_fine_peak_delta_V=abs(fine['max_vds_V']-row['max_vds_V']),fine_to_finer_peak_delta_V=delta,within_one_percent=delta/finer['max_vds_V']<.01,result=fine,finer_result=finer))
  (M/'results/driver-screen.json').write_text(json.dumps(dict(contract_sha256=hashlib.sha256((M/'contract.json').read_bytes()).hexdigest(),model_type='engineering Level-1 MOS/capacitance surrogate with generic diode; not manufacturer model',cases=rows,refinements=refinements,decks=decks,fabrication_ready=False),indent=2)+'\n')
 finally:(M/'results/driver-simulator.log').write_text('\n'.join(s.logs)+'\n')
if __name__=='__main__':main()
