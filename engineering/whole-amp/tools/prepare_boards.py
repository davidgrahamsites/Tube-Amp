from pathlib import Path as _GuardPath
if (_GuardPath(__file__).resolve().parents[1]/'NATIVE_EDIT_GUARD').exists():
 raise RuntimeError('Saved native CAD is authoritative. Preserve it before intentionally regenerating this historical experiment.')
"""Whole-amplifier board partition and native footprint capture.
Every original component is accounted for. This is layout work, not release.
"""
from pathlib import Path
import json,copy,re
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'solid-state-reverb'
cs={}
for c in json.loads((OLD/'design-connectivity.json').read_text())['components']:
 r=c['reference']
 if r.startswith('#'):continue
 if r not in cs:cs[r]={**c,'pins':{},'units':[]}
 cs[r]['pins'].update(c['pins']);cs[r]['units'].append(c)
boards={'Main':{'size':[290,140],'refs':[]},'Power':{'size':[160,175],'refs':[]},'Control':{'size':[230,110],'refs':[]},'Reverb':{'size':[160,100],'refs':[]}}
off={}
socket={'R36','R37','R41','R42','R110','R111'}
for r,c in cs.items():
 sh=c['sheet']
 if sh.startswith(('07a','07b','07c')):b='Reverb'
 elif r in socket:off[r]='Solder directly at chassis valve socket; grid-stopper lead to grid pin <=15mm; screen parts kept clear of heat-sensitive wiring';continue
 elif r.startswith(('V','JPE')) or r in ['T1','T2','T3','L1','RT1','F1','F2','S1','S2','S3','J1','J2','J3','J4','J5','J7','JH1','JOT1','SW1','SW2','SW3','RV602','R100'] or (r.startswith('RV') and r!='RV10'):off[r]='Chassis/panel mounted or documented DNP; explicit harness required';continue
 elif sh.startswith(('01','02','03','04')):b='Main'
 elif sh.startswith(('05','06')):b='Power'
 elif sh.startswith(('08','09','10')):b='Control'
 else:raise ValueError((r,sh))
 boards[b]['refs'].append(r);c['assembly']=b
# Preserve each original 50uF value with a single 600V film capacitor.
# This avoids uncertain electrolytic leakage sharing and extra rail loading.
for ref in ['C12','C13','C25','C26']:
 cs[ref]['footprint']='Renegade_Whole:Panasonic_EZPV60506MTC'
 cs[ref]['selected_part']='Panasonic EZPV60506MTC'
 cs[ref]['rating']='50uF 600VDC film; official RDL0000C251 dimensional table; 57 x 25 x 40mm'
# Correct socket-loop requirements are retained rather than extending grid leads through a distant PCB.
for r in socket:cs[r]['assembly']='socket-local'
lib='Resistor_THT:'
for b,spec in boards.items():
 for r in spec['refs']:
  c=cs[r]
  if c.get('footprint'):continue
  if r.startswith('RV'):c['footprint']='Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical'
  elif r.startswith('R'):c['footprint']=lib+('R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal' if r in ['R17','R35','R501','R502','R506'] else 'R_Axial_DIN0207_L6.3mm_D2.5mm_P15.24mm_Horizontal')
  elif r.startswith('C'):
   v=c['value'].split()[0]
   if r in ['C29','C30']:c['footprint']='Capacitor_THT:CP_Radial_D25.0mm_P10.00mm_SnapIn'
   elif r in ['C12','C13','C25','C26']:c['footprint']='Capacitor_THT:CP_Radial_D30.0mm_P10.00mm_SnapIn'
   elif 'u' in v and float(v.replace('u',''))>=10:c['footprint']='Capacitor_THT:CP_Radial_D10.0mm_P5.00mm'
   elif 'p' in v:c['footprint']='Capacitor_THT:C_Disc_D7.5mm_W5.0mm_P10.00mm'
   else:c['footprint']='Capacitor_THT:C_Rect_L26.5mm_W10.5mm_P22.50mm_MKS4'
  elif r.startswith('D'):c['footprint']='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal' if '4007' in c['value'] else 'Diode_THT:D_DO-35_SOD27_P10.16mm_Horizontal'
  elif r in ['U1','U2']:c['footprint']='Package_DIP:DIP-14_W7.62mm'
  elif r=='U3':c['footprint']='Package_TO_SOT_SMD:SOT-23-6'
  elif r in ['U4','U5','U6','U7']:c['footprint']='Package_TO_SOT_THT:TO-220-3_Vertical'
  elif r.startswith('Q'):c['footprint']='Package_TO_SOT_THT:TO-92_Inline_Wide'
  elif r.startswith('K'):c['footprint']='Relay_THT:Relay_DPDT_Omron_G5V-2'
  else:raise ValueError((r,c))
# Low-voltage parts use their own compact, voltage-appropriate envelope.
for r in boards['Control']['refs']:
 c=cs[r]
 if r.startswith('R'):c['footprint']='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
 if r.startswith('C'):
  if r in ['C201','C208']:c['footprint']='Capacitor_THT:CP_Radial_D16.0mm_P7.50mm'
  elif float(c['value'].split()[0].replace('u','').replace('n','')) and 'u' in c['value']:c['footprint']='Capacitor_THT:CP_Radial_D8.0mm_P3.50mm'
  else:c['footprint']='Capacitor_THT:C_Rect_L7.2mm_W3.5mm_P5.00mm'
for r in boards['Main']['refs']:
 c=cs[r]
 if r.startswith('C') and c['value'] in ['22n','47n','100n']:c['footprint']='Capacitor_THT:C_Rect_L18.0mm_W7.0mm_P15.00mm_FKS3_FKP3'
 if r in ['C7','C10','C14']:c['footprint']='Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm'
 if r in ['C1','C5']:c['footprint']='Capacitor_THT:CP_Axial_L25.0mm_D10.0mm_P30.00mm_Horizontal'
for r in ['C29','C30']:
 cs[r]['footprint']='Capacitor_THT:CP_Radial_D22.0mm_P10.00mm_SnapIn'
 cs[r]['selected_part']='Nichicon LGL2G221MELZ30'
 cs[r]['rating']='220uF 400V; 22x30mm nominal, max23.5x32mm; 2mm board holes at10mm; series stack110uF'
for r in ['D3','D4','D5','D6']:
 cs[r]['selected_part']='STMicroelectronics STTH112'
 cs[r]['value']='STTH112'
 cs[r]['rating']='1200V 1A DO41; axial part, not STTH112A SMA'
 cs[r]['footprint']='Diode_THT:D_DO-41_SOD81_P12.70mm_Horizontal'
# Ports are soldered wire terminals, not guessed commercial connectors.
for b,spec in boards.items():
 refs=set(spec['refs']);nets={n for r in refs for n in cs[r]['pins'].values() if n};external={n for r,c in cs.items() if r not in refs for n in c['pins'].values() if n}
 spec['ports']=sorted(nets&external)
(ROOT/'board-plan.json').write_text(json.dumps({'revision':'0.5-development','boards':boards,'chassis_parts':off,'components':cs},indent=2))
print({b:(len(s['refs']),len(s['ports'])) for b,s in boards.items()});print('Chassis parts',len(off))
