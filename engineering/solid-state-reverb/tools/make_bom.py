from pathlib import Path
import json,csv,collections,re
R=Path(__file__).resolve().parents[1];cs=json.loads((R/'design-connectivity.json').read_text())['components'];groups={}
for c in cs:
 if c['reference'].startswith('#'):continue
 if c['reference'] not in groups:groups[c['reference']]={**c,'pins':{}}
 groups[c['reference']]['pins'].update(c['pins'])
fields=['reference','quantity','assembly','value','function','required_ratings','manufacturer','part_number_or_selection','footprint','source_evidence','status','procurement_notes']
rows=[]
for ref,c in groups.items():
 pcb=c['sheet'].startswith(('07a','07b','07c'));man='';pn='Select to value/rating and actual lead/body drawing';status='engineering specification; purchase qualification pending';notes='Confirm exact bought part dimensions and ratings; no price/stock quote';rating=c['rating'];func=c['sheet'];evidence=c['datasheet'] or c['source']
 if ref in ('U10','U11','U12'):man='Texas Instruments';pn='OPA2134PA';status='selected design reference; PDIP pin map checked';rating='+/-15V; PDIP8; do not substitute single OPA134';evidence='https://www.ti.com/lit/ds/symlink/opa2134.pdf'
 if ref in ('K1','K2','K3'):man='Omron';pn='G5V-2-H1 DC12';rating='High-sensitivity 12V coil, 150mW nominal; DPDT';evidence='https://components.omron.com/system/files/2023-01/datasheet_pdf/K046-E1.pdf'
 if ref=='RV601':man='Bourns';pn='3296W-1-104LF';rating='100k multi-turn cermet; internal SEND calibration';evidence='https://www.bourns.com/docs/product-datasheets/3296.pdf'
 if ref=='RV602':man='Alpha candidate';pn='100k audio/log, panel-mounted; shaft/bushing variant pending';rating='Clockwise adds wet; wire terminal identities by measurement, not apparent lug order';notes='Front/top faceplate REVERB; off-board. Keep dry signal constant.'
 if ref=='RT1':man='Accu-Bell / Belton candidate';pn='8EB2C1B';rating='800ohm input /2575ohm output at 1kHz; medium decay; input insulated/output grounded; horizontal open side down';notes='Supplier/manufacturer confirmation and China stock pending; impedance is NOT DC resistance; no 8ohm substitution';evidence='Tank selection dossier in evidence/parts.md'
 if ref=='T1':man='Hammond electrical reference';pn='372FX or documented 220V/50Hz equivalent';rating='300-0-300VAC 173mA; 50V bias tap; 6.3VAC 5A; >=150VA reference';notes='China transformer selection, lead map, insulation and geometry pending. Insulate unused 5V/heater-CT leads.'
 if ref=='T2':man='Hammond electrical reference';pn='1650F or qualified equivalent';rating='7.6k CT primary; 4/8/16ohm secondary; 25W component rating';notes='Output power is not measured/guaranteed by this rating; verify winding phasing and purchased lead map.'
 if ref=='T3':pn='Custom/stock 220V 50Hz :18-0-18VAC 0.25A, 9VA';rating='Safety-isolated winding and thermal protection evidence required';notes='Separate chassis-mounted transformer; both primary branches must be 220V/50Hz.'
 if ref=='L1':man='Hammond reference';pn='193D or qualified equivalent';rating='8H,150mA,75ohm reference; screen/preamp supply only'
 if re.fullmatch(r'V[1-4]',ref):man='JJ reference';pn='ECC83S /12AX7';rating='6.3V,0.3A heater; exact manufacturer tube and heater/cathode stresses must be qualified'
 if ref in ('V5','V6'):man='JJ reference';pn='EL34';rating='6.3V,1.5A heater; plate25W/screen8W limits; measured bias required';notes='Match pair at intended conditions; 220k fixed-bias grid-return suitability still requires exact-tube evidence.'
 if ref in ('U4','U5','U6','U7'):man='STMicroelectronics';pn={'U4':'L7812CV','U5':'L7805CV','U6':'L7815CV','U7':'L7915CV'}[ref];rating='TO220; input and thermal envelope review; 7915 pin/tab differs from 78xx';evidence='https://www.st.com/resource/en/datasheet/'+('l79.pdf' if ref=='U7' else 'l78.pdf')
 if ref in ('C201','C208'):rating='1000uF 50V,105C, ripple current and lead pitch checked against actual part'
 if pcb and ref.startswith('R') and not ref.startswith('RV'):man='Yageo/Vishay equivalent';pn='Metal-film axial, 1%, value as listed';rating='>=0.25W, <=6.3x2.5mm body, 10.16mm formed lead pitch; R602 10Mohm requires suitable series'
 if pcb and ref.startswith('C'):
  notes='Footprint is an explicit maximum body/lead envelope; qualify an exact part before ordering PCB.'
 if ref in ('F1','F2','S2'):status='BLOCKED exact protective/switch rating and coordination';notes='Do not procure by legacy printed value. Resolve against actual transformer, inrush and interruption conditions.'
 qty=0 if ref=='R100' else 1
 rows.append(dict(zip(fields,[ref,qty,'reverb PCB' if pcb else 'chassis/other assembly',c['value'],func,rating,man,pn,c.get('footprint',''),evidence,status,notes])))
# Mechanical/wiring items absent from electrical netlist, explicitly not component duplicates.
extras=[
('MECH-CAB',1,'Mable 5E3 empty 1x12 cabinet','508x420mm; depth215/242mm; 312mm opening','China listing; stock/material/fit confirmation pending'),
('MECH-CHASSIS',1,'Custom chassis for existing shell','Dimensions withheld pending fit proof; no stock 5E3 chassis assumption','Keep original cabinet; support two transformers, OT, choke, six sockets and controls'),
('MECH-SPEAKER',1,'12-inch guitar speaker, 8ohm proposed interface','Power handling at least actual measured amp output with margin; match baffle270mm cutout/312mm bolt circle','Exact existing preferred model not established; preserve cabinet choice; qualify speaker before drilling'),
('SOCKET-NOVAL',4,'9-pin chassis tube socket','12AX7 pin pattern; voltage/temperature rated; shields/retainers as selected','View socket pin numbers from wiring side and verify physical numbering'),
('SOCKET-OCTAL',2,'8-pin chassis tube socket','EL34 voltage/temp rating and retention','Chassis mounted; grid/screen resistors at socket pins'),
('SOCKET-DIP8',3,'Optional turned-pin DIP8 socket','7.62mm row pitch','Optional; not extra op-amps'),
('MECH-HEATSINK',3,'Heatsinks for U4/U6/U7','Thermal design to actual high-line load; isolate U7 tab','U5 heatsink depends on measured load'),
('MECH-STANDOFF',4,'Insulated M3 standoffs plus screws','>=8mm underside clearance target, actual assembly reviewed','PCB has four 3.2mm NPTH holes'),
('MECH-TANKBAG',1,'Tank bag and resilient mounting hardware','Fit actual type8 tank; preserve mounting orientation','Place far from power transformer; verify mechanical feedback'),
('HARNESS-RCA',2,'Shielded RCA tank cables','Input and output identified; input shell isolation maintained','Do not confuse input/output or add chassis ground loops'),
('HARNESS-PCB',6,'JR1..JR6 mating harnesses','2/2/2/3/2/5 circuits respectively; retention and conductor sizing','Reference PCB connector pin schedule; no mains/HV'),
('MECH-KNOBS',10,'Operating knobs incl REVERB','Match exact pot shafts; two-row panel layout may be needed','9 original operating controls +REVERB; bias/send trims internal'),
('MECH-PEDAL',1,'Passive two-button momentary TRS pedal','Tip channel, ring reverb, sleeve common','Connect power off pending insertion testing'),
('MECH-PE',1,'Protective-earth stud and bonding hardware set','Dedicated locked metal bond; no dependence on PCB or signal cable','Independent qualified protective-bond inspection required'),
('WIRE-KIT',1,'Rated hookup wire, shield, sleeving, ties and terminals','Separate mains/HV/heater/audio ratings, temperature and routing','Final wire lengths depend on chassis; include strain relief and socket insulation'),
('BOARD-REVERB',1,'Renegade_Reverb v0.4 PCB','160x100mm; 2-layer;1.6mmFR4;1oz; PTH/NPTH','Engineering preview; no manufacturing release'),
('BOARD-TURRET',1,'Main amplifier turret/eyelet assembly','HV spacing/clearance and actual parts layout pending','Main tube circuit is not on the reverb PCB'),
('BOARD-CONTROL',1,'Controller and LV-supply assembly','Native integrated sheets08/09/10; no finished PCB in this package','Requires proper assembly design; not solderless breadboard')]
for ref,qty,val,rating,notes in extras:rows.append(dict(zip(fields,[ref,qty,'mechanical/harness',val,'assembly',rating,'','Selection pending','','Project requirements','engineering specification',notes])))
rows.sort(key=lambda r:r['reference'])
for name,subset in [('bom.csv',rows),('pcb/bom-reverb.csv',[r for r in rows if r['assembly']=='reverb PCB'])]:
 with (R/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(subset)
print(len(groups),'schematic components;',len(rows),'BOM rows;',sum(r['quantity'] for r in rows if r['assembly']=='reverb PCB'),'PCB fitted components')
