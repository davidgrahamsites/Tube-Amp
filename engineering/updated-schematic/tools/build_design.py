"""Build reviewable baseline and revised native schematics from explicit pin maps.
Run only before manual KiCad editing, or copy the module to a new revision.
"""
from kicad_factory import *
import hashlib
OUT=Path(__file__).resolve().parents[1]
guard=OUT/'generated-files.json'
if guard.exists():
 for name,digest in json.loads(guard.read_text()).items():
  path=OUT/name
  if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
   raise SystemExit('Native file changed after generation; preserve/reconcile manual edits before regeneration: '+name)
f=Factory(OUT)
main=f.custom_box('PowerTransformer_Logical',[(n,l,y,s) for n,l,y,s in [('L','PRI_L',10.16,'L'),('N','PRI_N',-10.16,'L'),('HV1','HV_A',15.24,'R'),('CT','HV_CT',10.16,'R'),('HV2','HV_B',5.08,'R'),('B','BIAS_TAP',0,'R'),('H1','6V3_A',-5.08,'R'),('H2','6V3_B',-10.16,'R')]],30.48)
ctrl=f.custom_box('ControlTransformer_Logical',[('L','PRI_L',5.08,'L'),('N','PRI_N',-5.08,'L'),('S1','SEC_A',7.62,'R'),('CT','SEC_CT',0,'R'),('S2','SEC_B',-7.62,'R')],25.4)
ot=f.custom_box('OutputTransformer_Logical',[('PA','PLATE_A',10.16,'L'),('CT','BPLUS',0,'L'),('PB','PLATE_B',-10.16,'L'),('COM','COM',15.24,'R'),('4','4_OHM',5.08,'R'),('8','8_OHM',-5.08,'R'),('16','16_OHM',-15.24,'R')],25.4)
rt=f.custom_box('ReverbTransformer_Logical',[('P1','PRI_SUPPLY',5.08,'L'),('P2','PRI_PLATE',-5.08,'L'),('S1','TANK_IN',5.08,'R'),('S2','RETURN',-5.08,'R')],25.4)
tank=f.custom_box('SpringTank_Logical',[('1','INPUT',5.08,'L'),('2','IN_RETURN',-5.08,'L'),('3','OUTPUT',5.08,'R'),('4','OUT_RETURN',-5.08,'R')],30.48)
SOURCE='OpenValve / AX84 v1.2, 2001-10-17; source slide '
JJ='https://www.jj-electronic.com/images/stories/product/preamplifying_tubes/pdf/'
led=f.custom_box('LED_InternalResistor_Logical',[('A','ANODE',0,'L'),('K','CATHODE',0,'R')],10.16)
projects=[]
def build(revised):
 project='Renegade_220V_Reverb' if revised else 'Renegade_Source_Baseline';dest=OUT if revised else OUT/'baseline';dest.mkdir(exist_ok=True)
 rootid=uid(project+'/root');sheets=[]
 def sh(name,title):
  sid=uid(project+'/sheet/'+name);s=Sheet(f,project,name,title,len(sheets)+2,rootid,sid);sheets.append((s,sid));return s
 def R(s,ref,val,a,b,i,rating='0.5 W minimum; exact part pending',src='1'):
  old={'R33':'220k','R34':'220k','R38':'56k','R39':'15k','R40':'220k'}.get(ref)
  modified=revised and old and val!=old
  s.grid('Device:R',ref,val,{'1':a,'2':b},i,source=(SOURCE+src+(' / changed from '+old if modified else '')) if int(ref[1:])<100 else 'Revision v0.2',rating=rating,status='modified from source' if modified else ('source value retained' if int(ref[1:])<100 else 'proposed'))
 def C(s,ref,val,a,b,i,polar=False,rating='630 V film',src='1'):
  s.grid('Device:C_Polarized' if polar else 'Device:C',ref,val,{'1':a,'2':b},i,source=SOURCE+src if int(ref[1:])<100 else 'Revision v0.2',rating=rating,status='modified from source' if revised and ref in ('C29','C30') else ('source value retained' if int(ref[1:])<100 else 'proposed'))
 def P(s,ref,val,a,w,b,i,src='1'):
  s.grid('Device:R_Potentiometer',ref,val,{'1':a,'2':w,'3':b},i,source=SOURCE+src,rating='Off-board; voltage, taper and drawing review pending')
 def tri(s,ref,p,g,k,i,half=1,typ='ECC83'):
  # KiCad unit 2 has pins 1/2/3; unit 1 has pins 6/7/8.
  ns={'1':p,'2':g,'3':k} if half==1 else {'6':p,'7':g,'8':k}
  s.grid('Valve:'+typ,ref,'12AT7 / ECC81' if typ=='ECC81' else '12AX7 / ECC83S',ns,i,unit=2 if half==1 else 1,source=SOURCE+('2' if ref=='V4' else '1') if int(ref[1:])<=4 else 'Revision v0.2',datasheet=JJ+('ecc81.pdf' if typ=='ECC81' else 'ecc83s.pdf'),rating='JJ reference; actual purchased tube/model pending')
 def relay(s,ref,unit,nets,i):s.grid('Relay:G5V-2_Split',ref,'G5V-2-H1 DC12 (candidate)',nets,i,unit=unit,rating='12 V high-sensitivity coil; 150 mW reference; verify exact suffix',datasheet='https://components.omron.com/system/files/2023-01/datasheet_pdf/K046-E1.pdf')
 s=sh('01_clean','Clean channel - original values and actual valve pins')
 tri(s,'V1','CL_P1','CL_IN','CL_K1',0);R(s,'R4','100k','B_EARLY','CL_P1',1);R(s,'R2','1M','CL_IN','GND',2);R(s,'R3','1.5k','CL_K1','GND',3);C(s,'C1','25u','CL_K1','GND',4,True,'50 V')
 R(s,'R5','100k','CL_P1','CL_TONE',5);C(s,'C2','250p','CL_P1','CL_TREBLE_TOP',6);C(s,'C3','100n','CL_TONE','CL_BASS_TOP',7);C(s,'C4','47n','CL_TONE','CL_BASS_BOTTOM',8)
 P(s,'RV1','250k LIN TREBLE','CL_TREBLE_TOP','CL_TREBLE_W','CL_BASS_TOP',9);P(s,'RV2','1M LOG BASS','CL_BASS_TOP','CL_BASS_TOP','CL_BASS_BOTTOM',10);R(s,'R6','15k','CL_BASS_BOTTOM','GND',11);P(s,'RV3','1M LOG VOLUME','CL_TREBLE_W','CL_G2','GND',12)
 tri(s,'V1','CL_P2','CL_G2','CL_K2',15,half=2);R(s,'R7','100k','B_EARLY','CL_P2',16);R(s,'R8','1.5k','CL_K2','GND',17);C(s,'C5','25u','CL_K2','GND',18,True,'50 V');C(s,'C6','47n','CL_P2','CLEAN_OUT',19);R(s,'R43','10M','CLEAN_OUT','GND',20)
 s.text('V1 assignment: source lower envelope. V1A = pins 1/2/3; V1B = pins 6/7/8.\nRV1/RV2/RV3 map Treble1/Bass1/Vol1. Bass wiper strapped to top.\nNamed nets are electrical connections, including K1 inactive-channel grid grounding.',18,235)
 s=sh('02_dirty','Dirty channel - gain stages, cathode follower and Marshall tone stack')
 tri(s,'V2','DR_P1','DR_IN','DR_K1',0);R(s,'R12','100k','B_EARLY','DR_P1',1);R(s,'R10','1M','DR_IN','GND',2);R(s,'R11','2.7k','DR_K1','GND',3);C(s,'C7','680n','DR_K1','GND',4,rating='50 V film')
 C(s,'C8','22n','DR_P1','DR_GAIN_TOP',5);P(s,'RV4','1M LOG GAIN','DR_GAIN_TOP','DR_GAIN_W','GND',6);R(s,'R13','470k','DR_GAIN_W','DR_G2',7);C(s,'C9','470p','DR_GAIN_W','DR_G2',8);R(s,'R14','470k','DR_G2','GND',9)
 tri(s,'V2','DR_P2','DR_G2','DR_K2',10,half=2);R(s,'R15','100k','B_EARLY','DR_P2',11);R(s,'R16','1.8k','DR_K2','GND',12);C(s,'C10','1u','DR_K2','GND',13,True,'50 V');C(s,'C11','22n','DR_P2','DR_C3',14)
 R(s,'R18','470k','DR_C3','DR_G3',15);R(s,'R19','470k','DR_G3','GND',16);tri(s,'V3','DR_P3','DR_G3','DR_K3',17);R(s,'R21','100k','B_PRE','DR_P3',18);R(s,'R20','820','DR_K3','GND',19);C(s,'C14','1u','DR_K3','GND',20,True,'50 V')
 s.text('V2A/V2B gain stages feed V3A. Physical pin numbers govern the source mapping.\nGain knob RV4 maps the source unlabelled 1M Log control.',18,238)
 s=sh('02b_dirty_tone','Dirty cathode follower, tone controls and master volume')
 s.grid_offset=21
 tri(s,'V3','B_PRE','DR_P3','DR_CF',21,half=2);R(s,'R22','100k','DR_CF','GND',22,rating='2 W minimum; Vk stress pending');R(s,'R23','33k','DR_CF','DR_TONE',23);C(s,'C15','470p','DR_CF','DR_TREBLE_TOP',24)
 C(s,'C16','22n','DR_TONE','DR_BASS_TOP',25);C(s,'C17','22n','DR_TONE','DR_BASS_BOTTOM',26);P(s,'RV5','250k LIN TREBLE','DR_TREBLE_TOP','DR_TREBLE_W','DR_BASS_TOP',27);P(s,'RV6','1M LOG BASS','DR_BASS_TOP','DR_BASS_TOP','DR_BASS_BOTTOM',28);P(s,'RV7','25k LIN MID','DR_BASS_BOTTOM','GND','GND',29);P(s,'RV8','1M LOG MASTER','DR_TREBLE_W','DIRTY_OUT','GND',30)
 s.text('V2 = source first dirty envelope; V3 = source last dirty envelope.\nV3B is a DC-coupled cathode follower: plate 6 to B_PRE, grid 7 to DR_P3.\nReview V3 heater/cathode stress at every corner. R9/C18 are source numbering gaps.',18,276,1.0)
 s=sh('03_routing','Channel relays, input and normalled effects loop')
 s.grid('Connector_Audio:AudioJack2_SwitchT','J1','INPUT / grounded normal',{'S':'GND','T':'INPUT','TN':'GND'},0)
 R(s,'R1','68k','INPUT','INPUT_STOP',1)
 # Omron split unit 2: COM4 NC6 NO8; unit 3: COM13 NC11 NO9.
 relay(s,'K1',2,{'4':'INPUT_STOP','6':'CL_IN','8':'DR_IN'},2)
 relay(s,'K1',3,{'13':'GND','11':'DR_G2','9':'CL_G2'},3)
 relay(s,'K2',2,{'4':'FX_SEND','6':'CLEAN_OUT','8':'DIRTY_OUT'},4)
 relay(s,'K2',3,{'13':'GND','11':None,'9':None},5)
 s.grid('Connector_Audio:AudioJack2','J3','EFFECTS SEND',{'S':'GND','T':'FX_SEND'},6)
 s.grid('Connector_Audio:AudioJack2_SwitchT','J4','EFFECTS RETURN / normalled',{'S':'GND','T':'FX_RETURN','TN':'FX_SEND'},7)
 if revised:R(s,'R100','1M','FX_RETURN','GND',8)
 s.text('K1/K2 off = CLEAN. K1 selects input and grounds the inactive second-stage grid.\nK2 selects channel output. K2 spare pole is unused and explicitly marked.\nJ4 normal contact TN preserves the dry path with no external loop cable.\nJ6 is unassigned in the source BOM; no extra function has been invented.\nRelay candidate is high-sensitivity H1; source relays had no actual part identity.',18,160)
 s=sh('04_output','Long-tail phase inverter, EL34 pair, output and feedback')
 inp='MIX_OUT' if revised else 'FX_RETURN'
 R(s,'R24','10M',inp,'GND',0,src='2');C(s,'C19','22n',inp,'PI_G1',1,src='2');R(s,'R25','1M','PI_G1','PI_TAIL_TOP',2,src='2');tri(s,'V4','PI_P1','PI_G1','PI_K',3)
 tri(s,'V4','PI_P2','PI_G2','PI_K',4,half=2);R(s,'R29','82k','B_PRE','PI_P1',5,src='2');R(s,'R30','100k','B_PRE','PI_P2',6,src='2');C(s,'C22','47p','PI_P1','PI_P2',7,src='2');R(s,'R26','470','PI_K','PI_TAIL_TOP',8,src='2');R(s,'R28','10k','PI_TAIL_TOP','NFB_NODE',9,src='2');R(s,'R27','1M','PI_G2','PI_TAIL_TOP',10,src='2');C(s,'C20','100n','PI_G2','NFB_NODE',11,src='2')
 R(s,'R31','100k','OT_4','NFB_NODE',12,src='2');R(s,'R32','47k','NFB_NODE','GND',13,src='2');C(s,'C21','100n','NFB_NODE','PRES_TOP',14,src='2');P(s,'RV9','25k LIN PRESENCE','PRES_TOP','GND','GND',15,src='2')
 C(s,'C23','22n','PI_P1','GRID_A_FEED',16,src='2');C(s,'C24','22n','PI_P2','GRID_B_FEED',17,src='2');R(s,'R33','100k' if revised else '220k','GRID_A_FEED','BIAS_OUT',18,src='2');R(s,'R34','100k' if revised else '220k','GRID_B_FEED','BIAS_OUT',19,src='2');R(s,'R36','1.5k','GRID_A_FEED','EL34_GA',20,src='2');R(s,'R37','1.5k','GRID_B_FEED','EL34_GB',21,src='2');R(s,'R41','1k','B_SCREEN','EL34_SA',22,rating='5 W; screen current stress pending',src='2');R(s,'R42','1k','B_SCREEN','EL34_SB',23,rating='5 W; screen current stress pending',src='2')
 for ref,pl,gr,sc,i,k in [('V5','OT_PA','EL34_GA','EL34_SA',24,'K_A'),('V6','OT_PB','EL34_GB','EL34_SB',25,'K_B')]:
  kn=k if revised else 'GND';s.grid('Valve:EL34',ref,'EL34',{'1':kn,'3':pl,'4':sc,'5':gr,'8':kn},i,source=SOURCE+'2',datasheet='https://www.jj-electronic.com/images/stories/product/power_tubes/pdf/el34_e34l.pdf')
 if revised:R(s,'R110','1','K_A','GND',26,rating='1 W 1%; cathode test resistor');R(s,'R111','1','K_B','GND',27,rating='1 W 1%; cathode test resistor')
 s.text('C23/C24 drive the individually biased EL34 grids. K_A/K_B are cathode measurement points.\nReview plate/screen dissipation, grid-return limits, feedback phase and load-line before release.',18,265,1.1)
 s=sh('04b_output_transformer','Output transformer, speaker taps and impedance selector')
 s.grid_offset=28
 s.grid(ot,'T2','1650F reference / 7k6 CT 25 W',{'PA':'OT_PA','CT':'B_MAIN','PB':'OT_PB','COM':'GND','4':'OT_4','8':'OT_8','16':'OT_16'},28,datasheet='https://www.hammfg.com/part/1650F',rating='Chinese equivalent not selected; winding phase/leakage/DCR pending')
 s.grid('Connector_Audio:AudioJack2','J5','SPEAKER via 4/8/16 selector',{'S':'GND','T':'SPEAKER_TAP'},29)
 s.grid('Switch:SW_SP3T','S3','4/8/16 OHM SELECT',{'1':'OT_4','2':'OT_8','3':'SPEAKER_TAP','4':'OT_16'},31)
 s.grid('Connector_Generic:Conn_01x03','JOT1','OT tap leads /insulate unused',{'1':'OT_4','2':'OT_8','3':'OT_16'},30)
 s.text('NFB always samples the 4-ohm tap, as drawn in the source. S3 retains the source 4/8/16-ohm speaker selector.\nMatch S3 to the actual speaker load; switch impedance with power off.\nConfirm feedback polarity at low level before closing the loop. 25 W is the OT rating, not measured power.\nRevised R33/R34 = 100k (fixed-bias review); R110/R111 add cathode measurement points.',18,265,1.1)
 s=sh('05_supplies','Mains, HV, bias, heater elevation and reverb supply' if revised else 'Original mains / HV / bias - historical baseline')
 s.grid('Connector_Generic:Conn_01x03','J7','MAINS INLET L/N/PE',{'1':'MAINS_L','2':'MAINS_N','3':'PE'},0)
 s.grid('Device:Fuse','F1','T1.6A / 250VAC provisional' if revised else '3A source',{'1':'MAINS_L','2':'L_FUSED'},1,rating='HBC and inrush coordination pending')
 s.grid('Switch:SW_DPST','S1','POWER / double pole',{'1':'L_FUSED','2':'L_SW','3':'MAINS_N','4':'N_SW'},2,rating='250 VAC / inrush suitability pending')
 s.grid(main,'T1','372HX ref: 220V 50Hz' if revised else '272FX source: 115V 60Hz',{'L':'L_SW','N':'N_SW','HV1':'HV_A' if revised else 'HV_A_SRC','CT':'GND','HV2':'HV_B' if revised else 'HV_B_SRC','B':'BIAS_AC' if revised else None,'H1':'HEAT_A','H2':'HEAT_B'},3,datasheet='https://www.hammfg.com/part/372HX' if revised else 'https://www.hammfg.com/part/272FX',rating='300-0-300 VAC 230mA; 6.3 VAC 6A; 50V bias tap' if revised else 'Original magnetic identity only')
 # CT goes to ground. Series diode pairs, one on each HV half, implement the drawn doubler PIV stack.
 for ref,k,a,i in [('D3','HV_MID_A','HV_A',4),('D4','B_RECT','HV_MID_A',5),('D5','HV_MID_B','HV_B',6),('D6','B_RECT','HV_MID_B',7)]:s.grid('Device:D',ref,'1N4007',{'1':k,'2':a},i,source=SOURCE+'2',rating='1000 V diode reference; charging/inrush stress pending')
 s.grid('Device:Fuse','F2','HV fuse TBD >=600VDC' if revised else '500mA source',{'1':'B_RECT','2':'B_RAW'},8,rating='Value, breaking capacity and DC holder rating pending')
 if revised:
  C(s,'C29','220u','B_RAW','HV_CAP_MID',9,True,'350 V each; series pair');C(s,'C30','220u','HV_CAP_MID','GND',10,True,'350 V each; series pair');R(s,'R501','220k','B_RAW','HV_CAP_MID',11,'2 W; 350 V working minimum');R(s,'R502','220k','HV_CAP_MID','GND',12,'2 W; 350 V working minimum')
 else:C(s,'C29','50u','B_RAW','GND',9,True,'Source rating unstated');C(s,'C30','50u','B_RAW','GND',10,True,'Source rating unstated')
 if revised:s.grid('Switch:SW_SPST','S2','STANDBY / HVDC rated TBD',{'1':'B_RAW','2':'B_MAIN'},13,rating='Bias remains powered; actual HV DC switch/arc rating pending')
 else:
  s.grid('Switch:SW_DPST','S2','SOURCE STANDBY / HV secondary',{'1':'HV_A_SRC','2':'HV_A','3':'HV_B_SRC','4':'HV_B'},13)
  s.items.append(f'(wire (pts (xy 30.48 234.95) (xy 64.77 234.95)) (stroke (width 0) (type default)) (uuid {uid(project+"rawbond")}))')
  for net,x in [('B_RAW',30.48),('B_MAIN',64.77)]:s.items.append(f'(global_label {q(net)} (shape passive) (at {x} 234.95 0) (effects (font (size 0.95 0.95)) (justify left)) (uuid {uid(project+"rawbond"+net)}) (property "Intersheetrefs" "" (at {x} 234.95 0) (effects (font (size 1 1)) hide)))')
 s.grid('Device:L','L1','193D ref 8H /150mA',{'1':'B_MAIN','2':'B_SCREEN'},14,datasheet='https://www.hammfg.com/part/193D',rating='Feeds screens and small-signal stages, not output plate current')
 C(s,'C26','50u','B_SCREEN','GND',15,True,'600 V minimum',src='2');R(s,'R35','10k','B_SCREEN','B_PRE',16,'5 W',src='2');C(s,'C25','50u','B_PRE','GND',17,True,'600 V minimum',src='2');R(s,'R17','10k','B_PRE','B_EARLY',18,'5 W');C(s,'C13','50u','B_PRE','GND',19,True,'600 V minimum');C(s,'C12','50u','B_EARLY','GND',20,True,'600 V minimum')
 s.text('''Centre-tapped full-wave HV rectifier: two series diodes per half.
Output plate CT is before the choke; choke carries screens/small-signal load.
Revised C29/C30 = 110u effective /700V series bank with balance bleeders.
Native validity is not a supply/fuse/insulation release.''',18,257,1.15)
 s=sh('05b_bias_reverb_supply','Bias supply, heater elevation and bounded reverb rail')
 s.grid_offset=21
 # Negative rectifier: cathode faces AC, electrolytic positive terminal at GND.
 R(s,'R40','1k' if revised else '220k','BIAS_AC' if revised else 'HV_B_SRC','BIAS_DIODE_AC',21,'1 W',src='2');s.grid('Device:D','D7','1N4007',{'1':'BIAS_DIODE_AC','2':'BIAS_RAW'},22,source=SOURCE+'2');C(s,'C28','10u','GND','BIAS_RAW',23,True,'100 V',src='2');R(s,'R39','4.7k' if revised else '15k','BIAS_RAW','BIAS_FILTER',24,'1 W',src='2');C(s,'C27','10u','GND','BIAS_FILTER',25,True,'100 V',src='2');R(s,'R38','22k' if revised else '56k','BIAS_FILTER','BIAS_OUT',26,'1 W',src='2');P(s,'RV10','50k LIN BIAS','BIAS_OUT','BIAS_MIN' if revised else 'GND','BIAS_MIN' if revised else 'GND',27,src='2')
 if revised:
  R(s,'R503','33k','BIAS_MIN','GND',28,'1 W; minimum negative-bias stop')
  R(s,'R504','15k','B_SCREEN','B_REV',29,'15 W; chassis spacing and temperature review')
  for ref,k,a,i in [('D501','B_REV','Z_MID',30),('D502','Z_MID','GND',31)]:s.grid('Device:D_Zener',ref,'1N5380B 120V /5W',{'1':k,'2':a},i,datasheet='https://www.onsemi.com/pdf/datasheet/1n5333b-d.pdf',rating='Series nominal 240V clamp; low-current knee and derating pending')
  C(s,'C503','47u','B_REV','GND',32,True,'450 V');R(s,'R505','4.7k','B_REV','B_REC',33,'2 W');C(s,'C504','22u','B_REC','GND',34,True,'450 V')
  R(s,'R506','220k','B_SCREEN','HREF',35,'2 W; voltage rating pending');R(s,'R507','39k','HREF','GND',36,'1 W');C(s,'C505','47u','HREF','GND',37,True,'160 V');R(s,'R508','100','HEAT_A','HREF',38,'0.5 W');R(s,'R509','100','HEAT_B','HREF',39,'0.5 W')
 # Many supply components: split heater/bonding onto its own sheet instead of overfilling A3.
 s.text('220 V /50 Hz applies to BOTH T1 and control T3. Transformer labels are design references.\nD3-D6 are two series diodes per HV half, not a bridge; HV CT is grounded.\nRevised reservoir C29/C30 is 110u effective /700V series bank; balance/bleeder R501/R502.\nSupply and fuse choices require stress/startup review; exact Chinese transformer remains pending.',18,273,1.0)
 s=sh('06_heaters','Heater pin wiring, protective earth and chassis interfaces')
 for i,ref in enumerate(['V1','V2','V3','V4']+(['V7','V8'] if revised else [])):
  s.grid('Valve:ECC81' if ref=='V7' else 'Valve:ECC83',ref,'12AT7 / ECC81' if ref=='V7' else '12AX7 / ECC83S',{'4':'HEAT_A','5':'HEAT_A','9':'HEAT_B'},i,unit=3,source='6.3 V: pins 4+5 together; pin9 opposite')
 for i,ref in enumerate(['V5','V6'],8):s.grid('Valve:EL34',ref,'EL34',{'2':'HEAT_A','7':'HEAT_B'},i,unit=2)
 s.grid('Connector_Generic:Conn_01x02','JH1','6.3V PILOT /current TBD',{'1':'HEAT_A','2':'HEAT_B'},10,rating='Pilot allowance 0.15 A; actual part pending')
 s.grid('Connector_Generic:Conn_01x01','JPE1','CHASSIS PE STUD',{'1':'PE'},11,rating='Dedicated permanent protective-earth bond; no switch/fuse')
 s.grid('Connector_Generic:Conn_01x01','JPE2','EXPOSED METAL BOND',{'1':'PE'},12)
 # A deliberate direct copper bond represented as wire with labels, not a resistor.
 s.items.append(f'(wire (pts (xy 60.96 185.42) (xy 100.33 185.42)) (stroke (width 0) (type default)) (uuid {uid(project+"bondwire")}))')
 for net,x in [('PE',60.96),('GND',100.33)]:s.items.append(f'(global_label {q(net)} (shape passive) (at {x} 185.42 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid {uid(project+"bond"+net)}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {x} 185.42 0) (effects (font (size 1 1)) hide)))')

 for net,i in [('HEAT_A',15),('HEAT_B',16),('GND',17)]:s.grid('power:PWR_FLAG','#FLG'+str(i),'PWR_FLAG',{'1':net},i,source='Externally supplied winding or physical star ground declaration')
 s.text('SINGLE AUDIO-COMMON / CHASSIS BOND (physical star point)',45,174,1.4,True)
 s.text('PE inlet bonds directly to chassis and exposed metal. Audio common bonds once at the star.\nPCB/control/audio return routing must preserve this physical wiring intent.\nRevised heater load = 6 x 0.3A + 2 x 1.5A = 4.8A, plus pilot and tolerances.\nArtificial centre tap references HEAT_A/B to HREF; do not also ground a real heater centre tap.\nT1 unused 5V winding, if fitted: individually insulate every lead; do not connect to this circuit.',18,218)
 if revised:
  s=sh('07_reverb','Parallel 12AT7 spring driver, 12AX7 recovery and common mixer')
  C(s,'C101','2.2n','FX_RETURN','SEND_TOP',0);P(s,'RV101','250k LIN SEND trim','SEND_TOP','SEND_W','GND',1);R(s,'R101','220k','SEND_W','REV_DG',2);R(s,'R102','1M','REV_DG','GND',3)
  tri(s,'V7','REV_DP','REV_DG','REV_DK',4,typ='ECC81');tri(s,'V7','REV_DP','REV_DG','REV_DK',5,half=2,typ='ECC81');R(s,'R103','2.2k','REV_DK','GND',6,'3 W');C(s,'C102','22u','REV_DK','GND',7,True,'50 V')
  s.grid(rt,'T4','1750A reference /22k8:8',{'P1':'B_REV','P2':'REV_DP','S1':'TANK_IN','S2':'GND'},8,datasheet='https://www.hammfg.com/part/1750A',rating='n≈53.4; primary DC capability, DCR and insulation pending')
  s.grid(tank,'RT1','4AB3C1B candidate /8:2250',{'1':'TANK_IN','2':'GND','3':'TANK_OUT','4':'GND'},9,rating='Tank case/connector bonding/orientation/real impedances pending')
  R(s,'R104','220k','TANK_OUT','GND',10);R(s,'R105','68k','TANK_OUT','REV_RG',11);tri(s,'V8','REV_RP','REV_RG','REV_RK',12);R(s,'R106','100k','B_REC','REV_RP',13);R(s,'R107','1.5k','REV_RK','GND',14);C(s,'C103','22u','REV_RK','GND',15,True,'50 V');C(s,'C104','22n','REV_RP','WET_TOP',16);P(s,'RV102','100k LOG REVERB','WET_TOP','WET_W','GND',17)
  relay(s,'K3',2,{'4':'WET_W','6':'GND','8':None},18);relay(s,'K3',3,{'13':None,'11':None,'9':None},19)
  R(s,'R108','470k','WET_W','MIX_G',20);R(s,'R109','3.3M','FX_RETURN','MIX_G',21);C(s,'C105','10p','FX_RETURN','MIX_G',22);R(s,'R112','100k','MIX_G','GND',23)
  tri(s,'V8','MIX_P','MIX_G','MIX_K',24,half=2);R(s,'R113','100k','B_REC','MIX_P',25);R(s,'R114','1.5k','MIX_K','GND',26);C(s,'C106','22u','MIX_K','GND',27,True,'50 V');C(s,'C107','22n','MIX_P','MIX_OUT',28);R(s,'R115','1M','MIX_OUT','GND',29)
  s.text('Both channels pass through the common dry path. Reverb is a parallel branch after J4.\nK3 off shorts only the AC-coupled wet control wiper: immediate wet mute; dry remains connected.\nMixing stage changes dry gain and polarity; determine level/feedback interaction in simulation and bench.\nThe 240V clamp is a proposed driver-plate limit, not a validated regulator or transformer match.\nTank symbol terminals are logical IDs. Do not infer physical case bonding from input/output returns.',18,265,1.05)
 s=sh('08_control_supply','Isolated low-voltage relay and 5V logic supply' if revised else 'Historical relay supply and latching pedal')
 s.grid(ctrl,'T3','220V 50Hz /15VAC 0.5A spec' if revised else '120VAC /12V CT as printed',{'L':'L_SW','N':'N_SW','S1':'CTRL_AC1','CT':None if revised else 'GND','S2':'CTRL_AC2'},0,rating='Separate isolated supply; exact part/insulation/thermal-fuse evidence pending')
 if revised:
  for ref,k,a,i in [('D201','CTRL_RAW','CTRL_AC1',1),('D202','CTRL_RAW','CTRL_AC2',2),('D203','CTRL_AC1','GND',3),('D204','CTRL_AC2','GND',4)]:s.grid('Device:D',ref,'1N4007',{'1':k,'2':a},i)
  C(s,'C201','1000u','CTRL_RAW','GND',5,True,'35 V');s.grid('Regulator_Linear:L7812','U4','L7812CV',{'1':'CTRL_RAW','2':'GND','3':'+12V'},6);s.grid('Regulator_Linear:L7805','U5','L7805CV',{'1':'+12V','2':'GND','3':'+5V'},7)
  for ref,val,a,b,i,polar,rating in [('C202','330n','CTRL_RAW','GND',8,False,'50 V'),('C203','100n','+12V','GND',9,False,'50 V'),('C204','100u','+12V','GND',10,True,'25 V'),('C205','330n','+12V','GND',11,False,'50 V'),('C206','100n','+5V','GND',12,False,'50 V'),('C207','47u','+5V','GND',13,True,'16 V')]:C(s,ref,val,a,b,i,polar,rating)
  s.grid('power:PWR_FLAG','#FLG18','PWR_FLAG',{'1':'CTRL_RAW'},16,source='Rectified isolated winding supply declaration')
  for ref,k,a,i in [('D205','CTRL_RAW','+12V',14),('D206','+12V','+5V',15)]:s.grid('Device:D',ref,'1N4007 discharge bypass',{'1':k,'2':a},i)
  s.text('T3 secondary is 15 VAC, not 12 VAC, to retain 7812 dropout margin at 198 V input.\nLogic and pedal share isolated secondary common at the physical star; pedal carries low voltage only.\nCoil load budget uses three H1 relays (12.5mA each). Standard non-H1 relays need recalculation.\nBoth regulators need input/output decoupling near pins; verify dropout, dissipation and startup.',18,205)
 else:
  for ref,ac,i in [('D1','CTRL_AC1',1),('D2','CTRL_AC2',2)]:s.grid('Device:D',ref,'1N4007',{'1':'+12V','2':ac},i,source=SOURCE+'1')
  C(s,'C31','4700u','+12V','GND',3,True,'Source rating unstated')
  s.grid('Connector_Audio:AudioJack2','J2','Legacy latching pedal',{'S':'GND','T':'COIL_CH'},4)
  s.grid('Switch:SW_SPST','SW1','PEDAL LATCH',{'1':'COIL_CH','2':'GND'},5)
  s.grid(led,'LED1','12V LED + internal R',{'A':'+12V','K':'COIL_CH'},6,source=SOURCE+'1',rating='Source internal current limiting; actual model/value not specified')
  s.grid(led,'LED2','Pedal LED + internal R',{'A':'COIL_CH','K':'GND'},7,source=SOURCE+'1',rating='Source quantity/scope ambiguous; LED may load open pedal through coils')
  s.text('Source T3 label 12V CT is ambiguous: 6-0-6 vs 12-0-12 changes rectified rail.\nThe printed 120 VAC legacy primary is incompatible with the requested revision.\nLED1/LED2 are boxed built-in-resistor indicators; source quantity/scope remains ambiguous.\nLegacy coil suppression is absent in source; not silently inserted into baseline.',18,160)
 for ref,i in [('K1',18),('K2',19)]+([('K3',20)] if revised else []):relay(s,ref,1,{'1':'+12V','16':'COIL_REV' if ref=='K3' else 'COIL_CH'},i)
 if revised:
  s=sh('09_controller','Debounced momentary controls, reset and relay drivers')
  s.grid('Connector_Audio:AudioJack3','J2','TRS passive pedal assumption',{'T':'PEDAL_CH','R':'PEDAL_REV','S':'GND'},0)
  for prefix,base,un,i in [('CH',301,1,1),('REV',311,2,10)]:
   R(s,'R'+str(base),'1k','PEDAL_'+prefix,'BTN_'+prefix,i,'0.25 W; cable current limiter')
   s.grid('Switch:SW_Push','SW'+str(un),'LOCAL '+prefix,{'1':'BTN_'+prefix,'2':'GND'},i+1)
   R(s,'R'+str(base+1),'10k','+5V','BTN_'+prefix,i+2,'0.25 W');R(s,'R'+str(base+2),'15k','BTN_'+prefix,'DB_'+prefix,i+3,'1% 0.25 W');C(s,'C'+str(base),'1u','DB_'+prefix,'GND',i+4,rating='16 V; effective capacitance/tolerance pending')
   s.grid('74xx:74HC14','U1','SN74HC14N',{'1' if un==1 else '3':'DB_'+prefix,'2' if un==1 else '4':'CLK_'+prefix},i+5,unit=un,datasheet='https://www.ti.com/lit/ds/symlink/sn74hc14.pdf')
   for suffix,k,a,j in [('H','+5V','BTN_'+prefix,i+6),('L','BTN_'+prefix,'GND',i+7)]:s.grid('Device:D_Schottky','D'+str(base if suffix=='H' else base+1),'BAT43 input clamp',{'1':k,'2':a},j,rating='ESD TVS/connector shell termination still requires selection')
  s.text('''Two independent protected RC / Schmitt channels; local switches parallel the pedal.
1us or threshold-only idealization does not prove hot-plug or EMC behavior.''',18,223)
  s=sh('09b_latches_drivers','Toggle latches, brownout reset and relay drivers')
  s.grid_offset=19
  s.grid('74xx:74HC74','U2','SN74HC74N',{'1':'RESET_N','2':'CH_QN','3':'CLK_CH','4':'+5V','5':'CH_Q','6':'CH_QN'},19,unit=1,datasheet='https://www.ti.com/lit/ds/symlink/sn74hc74.pdf')
  s.grid('74xx:74HC74','U2','SN74HC74N',{'8':'REV_QN','9':'REV_Q','10':'+5V','11':'CLK_REV','12':'REV_QN','13':'RESET_N'},20,unit=2)
  s.grid('Power_Supervisor:TPS3808DBV','U3','TPS3808G50DBVR',{'1':'RESET_N','2':'GND','3':'MR_N','4':'RESET_CT','5':'+5V','6':'+5V'},21,datasheet='https://www.ti.com/lit/ds/symlink/tps3808.pdf',rating='4.65V sense; CT timing value subject to datasheet tolerance')
  C(s,'C321','47n','RESET_CT','GND',22,rating='16 V');R(s,'R321','10k','+5V','RESET_N',23,'0.25 W');R(s,'R322','10k','+5V','MR_N',24,'0.25 W');s.grid('Switch:SW_Push','SW3','RESET /clean +rev off',{'1':'MR_N','2':'GND'},25)
  for prefix,base,i in [('CH',331,26),('REV',341,31)]:
   R(s,'R'+str(base),'1k',prefix+'_Q',prefix+'_GATE',i,'0.25 W');R(s,'R'+str(base+1),'100k',prefix+'_GATE','GND',i+1,'0.25 W')
   s.grid('Transistor_FET:2N7000','Q'+str(1 if prefix=='CH' else 2),'2N7000',{'1':'GND','2':prefix+'_GATE','3':'COIL_'+prefix},i+2,rating='60 V; verify coil drain transient and gate drive',datasheet='https://www.onsemi.com/pdf/datasheet/2n7000-d.pdf')
   s.grid('Device:D','D'+str(base),'1N4007 flyback',{'1':'+12V','2':'COIL_'+prefix},i+3)
  s.text('Active-low switch -> HC14 rising edge on press -> HC74 D=/Q toggle. CLR establishes clean /reverb off.\nRC press constant is about 16ms; Schmitt thresholds set the actual debounce delay.\nLocal and pedal buttons are parallel. No pedal battery or tube voltage.\nCable insertion/removal can still toggle: connect pedal with power off until detect/inhibit design is resolved.\nDebounce is implemented; relay/audio pop suppression and ESD qualification remain separate checks.',18,277,0.98)
  s=sh('10_logic_power','Logic power units, unused inputs and supply decoupling')
  for unit,i in [(3,0),(4,1),(5,2),(6,3)]:
   pmap={3:('5','6'),4:('9','8'),5:('11','10'),6:('13','12')}[unit];s.grid('74xx:74HC14','U1','SN74HC14N',{pmap[0]:'GND',pmap[1]:None},i,unit=unit)
  s.grid('74xx:74HC14','U1','SN74HC14N',{'7':'GND','14':'+5V'},5,unit=7);s.grid('74xx:74HC74','U2','SN74HC74N',{'7':'GND','14':'+5V'},6,unit=3)
  for ref,i in [('C351',7),('C352',8),('C353',9)]:C(s,ref,'100n','+5V','GND',i,rating='16 V; one at each IC')
  s.text('Unused HC14 inputs tied to GND; unused outputs explicitly no-connect.\nAll package units and physical heater pins are captured.\nThe source pedal LEDs are replaced by passive switches; chassis indication remains a future option.\nNo firmware is required. Brownout/held-switch/reset and simultaneous-press bench tests still pending.',18,150)
 # Create cover and hierarchy.
 root=Sheet(f,project,'root','Renegade 220 V /50 Hz tube reverb draft' if revised else 'Renegade original source baseline',1,rootid);root.id=rootid
 root.text('RENEGADE  |  '+('220 V / 50 Hz + TUBE SPRING REVERB' if revised else 'SOURCE BASELINE / HISTORICAL SUPPLIES'),18,28,2.3,True)
 root.text('Editable engineering schematic, revision 0.2. Imported source unchanged.\nBlack named nets are electrical connections across this hierarchy.\nReference parts guide design; supplier selection, complete model qualification and cabinet fit remain open.\nThis revision is not a construction or PCB release.',18,41,1.4)
 for i,(s,sid) in enumerate(sheets):
  x=25+(i%4)*96;y=85+(i//4)*40
  root.items.append(f'(sheet (at {x} {y}) (size 80 27) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(s.title)} (at {x} {y-1.27} 0) (effects (font (size 1.1 1.1)) (justify left bottom))) (property "Sheetfile" {q(s.name+".kicad_sch")} (at {x} {y+28.27} 0) (effects (font (size 1 1)) (justify left top))) (instances (project {q(project)} (path "/{rootid}" (page "{s.page}")))))')
  s.write(dest)
 root.text('Audio: INPUT -> clean/dirty -> channel select -> FX send/return -> '+('dry + spring mix -> PI -> EL34 -> speaker' if revised else 'PI -> EL34 -> speaker'),18,257,1.15)
 root.text('Review priorities: bias envelope, transformer stress/phase, heater elevation, reverb drive/mix, relay pops, mains protection.',18,267,1.15)
 root.write(dest);(dest/(project+'.kicad_sch')).write_text((dest/'root.kicad_sch').read_text());(dest/'root.kicad_sch').unlink()
 (dest/(project+'.kicad_pro')).write_text(json.dumps({'meta':{'filename':project+'.kicad_pro','version':1}},indent=2)+'\n')
 path='${KIPRJMOD}/libraries/Renegade_Draft.kicad_sym' if revised else '${KIPRJMOD}/../libraries/Renegade_Draft.kicad_sym'
 (dest/'sym-lib-table').write_text(f'(sym_lib_table (version 7) (lib (name "Renegade_Draft") (type "KiCad") (uri "{path}") (options "") (descr "Project-local native draft symbols; see provenance")))\n')
 projects.append({'project':project,'path':str(dest/(project+'.kicad_sch')),'sheets':len(sheets)+1})
build(False);build(True);f.save_library()
(OUT/'design-connectivity.json').write_text(json.dumps({'revision':'0.2-DRAFT','projects':projects,'components':f.records},indent=2)+'\n')
print(json.dumps(projects,indent=2))

paths=list(OUT.glob('*.kicad_sch'))+list((OUT/'baseline').glob('*.kicad_sch'))+list(OUT.glob('*.kicad_pro'))+list((OUT/'baseline').glob('*.kicad_pro'))+[OUT/'sym-lib-table',OUT/'baseline'/'sym-lib-table',OUT/'libraries'/'Renegade_Draft.kicad_sym']
guard.write_text(json.dumps({str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
