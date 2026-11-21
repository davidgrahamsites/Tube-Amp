"""Create v0.4 in a separate directory; never overwrite v0.3/source.
Controlled native-file edits followed by KiCad export and pin checks.
"""
import sys,copy,json,shutil,zipfile
from pathlib import Path
if (Path(__file__).resolve().parents[1]/'NATIVE_EDIT_GUARD').exists():
 raise SystemExit('Preserve native edits: initial generator disabled for completed v0.4 CAD. Copy/reconcile into a new revision instead.')

ROOT=Path(__file__).resolve().parents[1]; OLD=ROOT.parent/'updated-schematic'
sys.path.insert(0,str(OLD/'tools'))
from kicad_factory import *
PROJECT='Renegade_220V_Reverb'; rootid=uid(PROJECT+'/root')
f=Factory(ROOT)
oldlib=parse((OLD/'libraries/Renegade_Draft.kicad_sym').read_text())
f.symbols={s[1]:copy.deepcopy(s) for s in children(oldlib,'symbol')}
f.origin=json.loads((OLD/'libraries/symbol-provenance.json').read_text())
records=[copy.deepcopy(c) for c in json.loads((OLD/'design-connectivity.json').read_text())['components'] if c['project']==PROJECT]
remove={'07_reverb','08_control_supply','05b_bias_reverb_supply','06_heaters'}
kept=[c for c in records if c['sheet'] not in remove]
for p in OLD.glob('*.kicad_sch'):
 if p.stem not in remove: shutil.copy2(p,ROOT/p.name)
shutil.copy2(OLD/'sym-lib-table',ROOT/'sym-lib-table')
shutil.copy2(OLD/(PROJECT+'.kicad_pro'),ROOT/(PROJECT+'.kicad_pro'))
configs={};sheets=[];fp={}
# Existing preamp/phase/output circuits retain source values. Reverse prior speculative grid-return change.
for c in kept:
 if c['reference'] in ('R33','R34'):c['value']='220k';c['status']='source value retained; tube-specific grid-return limit review required'
p=ROOT/'04_output.kicad_sch'; t=parse(p.read_text())
for s in children(t,'symbol'):
 ref=next(x[2] for x in children(s,'property') if x[1]=='Reference')
 if ref in ('R33','R34'):
  for pr in children(s,'property'):
   if pr[1] in ('Value','Display'):pr[2]='220k'
p.write_text(serialize(t)+'\n')
# New sheets. Positions are logical circuit groups; conventional wired redraw follows.
def sheet(name,title):
 s=Sheet(f,PROJECT,name,title,2,rootid,uid(PROJECT+'/sheet/'+name));sheets.append(s);configs[name]={'positions':{},'notes':[]};return s
def add(s,lib,ref,val,nets,x,y,unit=1,rating='',footprint='',source='DEC-007 v0.4',datasheet=''):
 s.sym(lib,ref,val,x,y,nets,unit=unit,rating=rating,source=source,datasheet=datasheet)
 configs[s.name]['positions'][ref if unit==1 else ref+'/'+str(unit)]=[x,y,0]
 if footprint:fp[ref]=footprint
RFP='Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
CFP='Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm'
EFP='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm'
def R(s,r,v,a,b,x,y):add(s,'Device:R',r,v,{'1':a,'2':b},x,y,rating='1% 0.25W metal film, 250V minimum',footprint=RFP)
def C(s,r,v,a,b,x,y,polar=False,hv=False):add(s,'Device:C_Polarized' if polar else 'Device:C',r,v,{'1':a,'2':b},x,y,rating='630V film' if hv else ('50V electrolytic' if polar else '63V film/C0G'),footprint=('Capacitor_THT:C_Rect_L18.0mm_W5.0mm_P15.00mm_MKS4' if hv else EFP if polar else CFP))
def J(s,r,nets,x,y):add(s,'Connector_Generic:Conn_01x%02d'%len(nets),r,r+' harness',dict(zip(map(str,range(1,len(nets)+1)),nets)),x,y,footprint='Connector_PinHeader_2.54mm:PinHeader_1x%02d_P2.54mm_Vertical'%len(nets),rating='Low voltage only; soldered locking harness or retained socket')
def op(s,r,u,plus,minus,out,x,y):
 ns={'3':plus,'2':minus,'1':out} if u==1 else {'5':plus,'6':minus,'7':out}
 add(s,'Amplifier_Operational:OPA2134',r,'OPA2134PA',ns,x,y,unit=u,footprint='Package_DIP:DIP-8_W7.62mm',datasheet='https://www.ti.com/lit/ds/symlink/opa2134.pdf',rating='PDIP-8; +/-15V; design linear signal limit 10Vpk')
s=sheet('07a_reverb_send','Spring send and constant dry buffer')
J(s,'JR1',['FX_RETURN','GND'],30.48,60.96)
C(s,'C601','100n','FX_RETURN','IN_AC',66.04,60.96,hv=True)
R(s,'R601','100k','IN_AC','DRY_IN',104.14,60.96)
R(s,'R602','10M','DRY_IN','GND',142.24,99.06)
op(s,'U10',1,'DRY_IN','DRY_BUF','DRY_BUF',190.5,60.96)
# Clamp limits input fault/overdrive current through R601; not a safety isolation barrier.
add(s,'Device:D','D601','1N4148',{'1':'+15V','2':'DRY_IN'},142.24,139.7,footprint='Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal')
add(s,'Device:D','D602','1N4148',{'1':'DRY_IN','2':'-15V'},180.34,139.7,footprint='Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal')
C(s,'C602','22n','DRY_BUF','SEND_TOP',228.6,60.96)
add(s,'Device:R_Potentiometer','RV601','100k SEND trim',{'1':'SEND_TOP','2':'SEND_W','3':'GND'},266.7,99.06,footprint='Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',rating='Bourns 3296W-1-104LF; commissioning tank drive trim')
op(s,'U10',2,'SEND_W','DRV_FB','DRIVER',320.04,60.96)
R(s,'R603','10k','DRV_FB','GND',299.72,139.7);R(s,'R604','10k','DRIVER','DRV_FB',345.44,99.06)
R(s,'R605','220','DRIVER','DRIVE_CAP',345.44,177.8)
# Non-polar film coupling avoids reverse-biased polarized part on bipolar audio.
C(s,'C603','2.2u','DRIVE_CAP','TANK_IN',266.7,177.8)
J(s,'JR2',['TANK_IN','GND'],228.6,177.8)
configs[s.name]['notes']=[['JR1: after normalled FX RETURN. Dry is continuous through unity buffer.\nSend trim is internal; panel REVERB is on recovery sheet. Tank input must be insulated from case.\nSet tank current during commissioning; this is voltage drive with 220R series isolation.',20,225,1.2]]
s=sheet('07b_reverb_recovery','Spring recovery, panel REVERB and constant-dry summing')
J(s,'JR3',['TANK_OUT','GND'],30.48,60.96)
C(s,'C604','100n','TANK_OUT','REC_IN',68.58,60.96)
R(s,'R606','220k','REC_IN','GND',104.14,99.06)
op(s,'U11',1,'REC_IN','REC_FB','REC_OUT',152.4,60.96)
R(s,'R607','1k','REC_FB','GND',129.54,139.7)
R(s,'R608','100k','REC_OUT','REC_FB',190.5,99.06)
C(s,'C605','330p','REC_OUT','REC_FB',190.5,139.7)
C(s,'C606','1u','REC_OUT','WET_TOP',228.6,60.96)
J(s,'JR4',['WET_TOP','WET_W','GND'],266.7,60.96)
R(s,'R609','1M','WET_W','GND',266.7,104.14)
op(s,'U11',2,'WET_W','WET_BUF','WET_BUF',320.04,60.96)
# Muting after knob buffer with isolation resistor; avoids shorting op-amp output.
R(s,'R610','10k','WET_BUF','WET_MUTE',320.04,139.7)
add(s,'Relay:G5V-2_Split','K3','G5V-2-H1 DC12',{'4':'WET_MUTE','6':'GND','8':None},370.84,139.7,unit=2,footprint='Relay_THT:Relay_DPDT_Omron_G5V-2',datasheet='https://components.omron.com/system/files/2023-01/datasheet_pdf/K046-E1.pdf')
R(s,'R611','100k','WET_MUTE','SUM',266.7,177.8)
R(s,'R612','100k','DRY_BUF','SUM',104.14,177.8)
op(s,'U12',1,'GND','SUM','SUM_INV',190.5,215.9)
R(s,'R613','100k','SUM_INV','SUM',228.6,215.9)
configs[s.name]['paper']='A2'
configs[s.name]['notes']=[['JR4 goes to panel 100k audio REVERB pot: 1=CW, 2=wiper, 3=CCW/ground.\nDry gain is independent of REVERB. K3 off shorts only wet mix node via R610.\nRecovery gain 101 at midband; 330p feedback cap rolls off excess treble/noise.',20,300,1.3]]
s=sheet('07c_reverb_output','Non-inverting overall mix, output, power and relay')
R(s,'R614','100k','SUM_INV','OUT_FB',40.64,60.96)
op(s,'U12',2,'GND','OUT_FB','OUT_BUF',104.14,60.96)
R(s,'R615','100k','OUT_BUF','OUT_FB',152.4,60.96)
R(s,'R616','100','OUT_BUF','OUT_AC',190.5,60.96)
C(s,'C607','1u','OUT_AC','MIX_OUT',228.6,60.96)
R(s,'R617','1M','MIX_OUT','GND',266.7,99.06)
J(s,'JR5',['MIX_OUT','GND'],304.8,60.96)
J(s,'JR6',['+15V','GND','-15V','+12V','COIL_REV'],40.64,152.4)
for ref,x in [('U10',104.14),('U11',190.5),('U12',276.86)]:
 add(s,'Amplifier_Operational:OPA2134',ref,'OPA2134PA',{'8':'+15V','4':'-15V'},x,152.4,unit=3,footprint='Package_DIP:DIP-8_W7.62mm')
 i=int(ref[1:])-10
 C(s,'C'+str(610+i*2),'100n','+15V','GND',x-20.32,208.28)
 C(s,'C'+str(611+i*2),'100n','GND','-15V',x+20.32,208.28)
C(s,'C616','47u','+15V','GND',345.44,99.06,True);C(s,'C617','47u','GND','-15V',383.54,99.06,True)
add(s,'Relay:G5V-2_Split','K3','G5V-2-H1 DC12',{'1':'+12V','16':'COIL_REV'},345.44,152.4,unit=1,footprint='Relay_THT:Relay_DPDT_Omron_G5V-2')
add(s,'Relay:G5V-2_Split','K3','G5V-2-H1 DC12',{'13':None,'11':None,'9':None},383.54,208.28,unit=3,footprint='Relay_THT:Relay_DPDT_Omron_G5V-2')
configs[s.name]['paper']='A2'
configs[s.name]['notes']=[['JR5 feeds original phase-inverter C19/R24. Two inversions preserve overall dry polarity.\nJR6 comes from isolated secondary supply/controller; no mains, B+ or heater wiring on this board.\nDecouplers at IC pins; tank recovery far from coil/driver returns. K3 flyback D341 stays at controller.\nDC dry gain approximately 0.990 at midband (100k input isolation / 10M load).\nOp-amp headroom is finite: verify maximum intended preamp level, not just small-signal gain.',20,285,1.3]]
# Chassis-only interfaces: tank and user-selected pot, plus all original source amp wiring.
s=sheet('07d_reverb_harness','Off-board tank and faceplate REVERB control')
add(s,'SpringTank_Logical','RT1','8EB2C1B /800:2575 ohm',{'1':'TANK_IN','2':'GND','3':'TANK_OUT','4':'GND'},101.6,76.2,rating='Type8 medium decay; horizontal open side down; exact vendor qualification pending')
add(s,'Device:R_Potentiometer','RV602','100k LOG REVERB',{'1':'WET_TOP','2':'WET_W','3':'GND'},228.6,76.2,rating='Panel-mounted Alpha 16mm candidate; CW=wet maximum; exact shaft/bushing pending')
configs[s.name]['notes']=[['Physical spring tank, not digital reverb. Do not substitute an 8-ohm tank.\nUse shielded tank return cable; input and output cable shields return to board GND.\nTank input connector insulated; output shell bonds tank case. Isolate tank mounting from chassis\nif necessary to avoid a second audio/chassis bond; preserve separate protective-earth wiring.\nPanel REVERB adds wet while the dry path remains constant.',20,150,1.3]]
# Remove old tube-reverb PSU and two heater loads; reuse remaining validated native net maps/layout.
oldcfg=json.loads((OLD/'wire-layout.json').read_text())
for name,title,drop in [('05b_bias_reverb_supply','Bias supply and heater reference',{'R504','R505','D501','D502','C503','C504'}),('06_heaters','Original six-tube heaters and protective earth',{'V7','V8'})]:
 s=sheet(name,title)
 for c in records:
  if c['sheet']!=name or c['reference'] in drop:continue
  key=c['reference'] if c['unit']==1 else c['reference']+'/'+str(c['unit'])
  x,y,rot=oldcfg[name]['positions'][key]
  add(s,c['symbol'],c['reference'],c['value'],c['pins'],x,y,unit=c['unit'],rating=c['rating'],source=c['source'],datasheet=c['datasheet'])
  configs[name]['positions'][key]=[x,y,rot]
 configs[name]['notes']=[['Six tubes only: 4 x 12AX7 + 2 x EL34 = 4.2A at 6.3V, plus pilot.\nRetained 220V supply/bias/heater-reference adaptations are listed in source-delta.md.\nNo high-voltage reverb supply remains. PE stud is a permanent independent chassis bond.',20,250,1.2]]
# Regenerate low-voltage PSU: center-tapped 18-0-18V powers +/-15V plus original 12/5V logic.
s=sheet('08_control_supply','220V isolated audio, relay and control supplies')
add(s,'ControlTransformer_Logical','T3','220V 50Hz /18-0-18V 0.25A',{'L':'L_SW','N':'N_SW','S1':'CTRL_AC1','CT':'GND','S2':'CTRL_AC2'},60.96,60.96,rating='9VA isolation transformer; insulation/fusing/mechanics require vendor evidence')
for ref,k,a,x,y in [('D201','CTRL_RAW','CTRL_AC1',139.7,45.72),('D202','CTRL_RAW','CTRL_AC2',139.7,83.82),('D203','CTRL_AC1','NEG_RAW',139.7,121.92),('D204','CTRL_AC2','NEG_RAW',139.7,160.02)]:add(s,'Device:D',ref,'1N4007',{'1':k,'2':a},x,y)
C(s,'C201','1000u','CTRL_RAW','GND',190.5,60.96,True);f.records[-1]['rating']='50V electrolytic, ripple rating required'
C(s,'C208','1000u','GND','NEG_RAW',190.5,160.02,True);f.records[-1]['rating']='50V electrolytic, ripple rating required'
add(s,'Regulator_Linear:L7815','U6','L7815CV',{'1':'CTRL_RAW','2':'GND','3':'+15V'},254,60.96,rating='TO220 heatsink; ST datasheet')
add(s,'Regulator_Linear:L7915','U7','L7915CV',{'1':'GND','2':'NEG_RAW','3':'-15V'},254,160.02,rating='TO220 tab=negative input; isolated heatsink')
add(s,'Regulator_Linear:L7812','U4','L7812CV',{'1':'CTRL_RAW','2':'GND','3':'+12V'},345.44,60.96,rating='TO220 heatsink; worst-case dissipation review')
add(s,'Regulator_Linear:L7805','U5','L7805CV',{'1':'+12V','2':'GND','3':'+5V'},436.88,60.96)
for i,(ref,val,a,b,polar,x,y) in enumerate([('C202','330n','CTRL_RAW','GND',False,228.6,228.6),('C203','100n','+12V','GND',False,266.7,228.6),('C204','100u','+12V','GND',True,304.8,228.6),('C205','330n','+12V','GND',False,342.9,228.6),('C206','100n','+5V','GND',False,381,228.6),('C207','47u','+5V','GND',True,419.1,228.6),('C209','330n','CTRL_RAW','GND',False,228.6,276.86),('C210','100n','+15V','GND',False,266.7,276.86),('C211','10u','+15V','GND',True,304.8,276.86),('C212','2.2u','GND','NEG_RAW',True,342.9,276.86),('C213','100n','GND','-15V',False,381,276.86),('C214','10u','GND','-15V',True,419.1,276.86)]):C(s,ref,val,a,b,x,y,polar)
for ref,k,a,x in [('D205','CTRL_RAW','+12V',345.44),('D206','+12V','+5V',383.54),('D207','CTRL_RAW','+15V',421.64),('D208','-15V','NEG_RAW',459.74)]:add(s,'Device:D',ref,'1N4007',{'1':k,'2':a},x,160.02)
for ref,x in [('K1',497.84),('K2',535.94)]:add(s,'Relay:G5V-2_Split',ref,'G5V-2-H1 DC12 (candidate)',{'1':'+12V','16':'COIL_CH'},x,60.96)
for ref,net,x in [('#FLG18','CTRL_RAW',60.96),('#FLG19','NEG_RAW',99.06)]:add(s,'power:PWR_FLAG',ref,'PWR_FLAG',{'1':net},x,228.6)
configs[s.name]['paper']='A2';configs[s.name]['notes']=[['Transformer is chassis-mounted; secondary supply assembled separately from audio board.\nT3 center tap is GND. No mains traces on reverb PCB. C201/C208 must be 50V rated.\n7915 pinout differs from 7815. Insulate its tab from common heatsink/chassis.\nFuses/transformer protection and high-line thermal limits require final selected-part review.',20,330,1.2]]
# Generate raw sheets and root; continuous-wire router will use these as inputs.
for s in sheets:s.write(ROOT)
allnames=[p.stem for p in ROOT.glob('*.kicad_sch') if p.stem!=PROJECT]
allnames.sort();root=Sheet(f,PROJECT,'root','Renegade original amp + solid-state spring reverb',1,rootid);root.id=rootid
root.text('RENEGADE | ORIGINAL SIX-TUBE AMP + SOLID-STATE SPRING REVERB',18,28,2.0,True)
root.text('v0.4 engineering package | 220 V / 50 Hz | REVERB adds wet to constant dry\nSource amplifier preserved except explicitly recorded supply/interface adaptations.\nPCB: isolated low-voltage spring reverb module. Original tube stages remain chassis/turret wired.\nCabinet fit, complete selected-component simulation and hardware qualification remain required.',18,40,1.2)
for i,name in enumerate(allnames):
 x=25+(i%4)*96;y=85+(i//4)*32;sid=uid(PROJECT+'/sheet/'+name)
 root.items.append(f'(sheet (at {x} {y}) (size 80 22) (stroke (width 0.254) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) (property "Sheetname" {q(name)} (at {x} {y-1.27} 0) (effects (font (size 1.1 1.1)) (justify left bottom))) (property "Sheetfile" {q(name+".kicad_sch")} (at {x} {y+23} 0) (effects (font (size 1 1)) (justify left top))) (instances (project {q(PROJECT)} (path "/{rootid}" (page "{i+2}")))))')
root.write(ROOT);(ROOT/'root.kicad_sch').rename(ROOT/(PROJECT+'.kicad_sch'))
f.save_library()
allrecords=kept+f.records
# Footprints are assigned only to the reverb PCB; chassis components intentionally have none.
for c in allrecords:
 c['footprint']=fp.get(c['reference'],'') if c['sheet'].startswith(('07a','07b','07c')) else ''
for s in sheets:
 p=ROOT/(s.name+'.kicad_sch');t=parse(p.read_text())
 for sym in children(t,'symbol'):
  ref=next(x[2] for x in children(sym,'property') if x[1]=='Reference')
  if s.name.startswith(('07a','07b','07c')):
   next(x for x in children(sym,'property') if x[1]=='Footprint')[2]=fp.get(ref,'')
 p.write_text(serialize(t)+'\n')
(ROOT/'design-connectivity.json').write_text(json.dumps({'revision':'0.4','components':allrecords},indent=2))
(ROOT/'wire-layout.json').write_text(json.dumps(configs,indent=2))
with zipfile.ZipFile(ROOT/'validation/label-layout-v0.2.zip','w') as z:
 for name in list(configs)+[PROJECT]:z.write(ROOT/(name+'.kicad_sch'),name+'.kicad_sch')
print('Created',len(allnames)+1,'sheets;',len(allrecords),'symbol units')
