"""CB-010. Guarded cutoff: an independent current-limited HV disconnect.

Place a normally-off cascode between raw B+ and the CB-009 fixed feed:

    raw -- M1 IXTP3N100D2 (1000 V depletion, gate to output through RG1)
        -- M2 NDT3055L (60 V logic FET, gate from a VOM1271 photovoltaic driver)
        -- RS (two 27.4 ohm in parallel) -- output -- 900 ohm feed -- AQV256HA ...

Q1 MMBT3904 senses RS and pulls the M2 gate down. M1 then absorbs the voltage.
LED off removes M2 gate drive, so loss of control opens the path. The limiter
needs no control power once the LED is lit. Everything downstream is CB-009.

This file owns results/guarded-cutoff.json. Simulation and arithmetic only.
Level-1 MOSFET surrogates with data-sheet corners. No native CAD is touched.
Run: python3.13 with numpy; KiCad libngspice through the existing adapter.
"""

import numpy as np

import supply_faults
from supply_trial import MODULE

OUT = MODULE / 'results/guarded-cutoff.json'
TRIP_LO, TRIP_HI = supply_faults.trip_corners()
CAP_NOM, CAP_TOL = 22.0, .20
C_ONE_OPEN = 3*CAP_NOM*(1-CAP_TOL)      # 52.8 uF: four fitted, one open, rest -20%
C_MAX = 4*CAP_NOM*(1+CAP_TOL)           # 105.6 uF
NORMAL_A = .02272                        # CB-009 branch current at 16.5 mA load
PA_ABS = 350.
FEED_MIN = 900*.95

# ---------------------------------------------------------------- parts
PARTS = {
    'M1': dict(part='Littelfuse/IXYS IXTP3N100D2', package='TO-220AB, tab is drain', qty=1,
               VDSX_V=1000, VGS_off_V=[-4.5, -2.5], VGS_off_test='VDS 25 V, 250 uA',
               RDS_on_max_ohm_25C=6, ID_on_min_A=3, gfs_S=[1.2, 2.0], Ciss_pF=1020, Crss_pF=17,
               IDSX_off_uA=dict(at_25C=5, at_125C=50, condition='VDS 1000 V, VGS -5 V'),
               VGS_max_V=20, PD_W_25C=125, RthJC_K_W=1.0, RthCS_K_W=.5, TJ_max_C=150,
               SOA='75 W minimum: VDS 800 V, ID 94 mA, case 75 C, 5 s',
               source='DS100184E(4/17), project copy engineering/component-selection/'
                      'heater-divider-rating/sources/ixtp3n100d2-manufacturer-extract.pdf'),
    'M2': dict(part='onsemi NDT3055L', package='SOT-223', qty=1, VDSS_V=60, VGS_max_V=20,
               VGS_th_V=[1, 1.6, 2], VGS_th_tempco_mV_K=-4, RDS_on_max_ohm=dict(at_4p5V=.12, at_10V_125C=.18),
               gfs_S_typ=7, Ciss_pF=345, Coss_pF=110, Crss_pF=30, IGSS_nA=100, PD_W=[1.1, 3],
               RthJC_K_W=12, source='onsemi NDT3055L/D rev 3, March 2025',
               sha256='5aefcdff043c3d4ba4ad63f82496cba93665823add615bd002db1bad5dcd7230'),
    'U1': dict(part='Vishay VOM1271T', package='SOP-4', qty=1, LED_VF_V=[1.2, 1.4, 1.6], LED_abs_mA=50,
               VOC_V=dict(at_5mA_typ=8.1, at_10mA_min=7.8, at_10mA_typ=8.4, at_20mA_typ=8.7, at_30mA_typ=8.9),
               ISC_uA=dict(at_5mA_typ=7, at_10mA_min=6, at_10mA_typ=15, at_20mA_typ=30, at_30mA_typ=47),
               ton_us_typ=53, toff_us_typ=65, switching_condition='200 pF, 20 mA; typical only, no maximum',
               VISO_Vrms=3750, VIORM_Vpeak=707, VIOTM_Vpeak=6000, creepage_mm=5, CTI=175,
               ambient_C=[-40, 100], integrated_turn_off=True,
               source='Vishay 83469 rev 1.9, 08-Aug-2023, https://www.vishay.com/docs/83469/vom1271.pdf',
               sha256='224bc07fd9de81b1f48ef9f64e907572a9f17f25455e2a99535216aadcdf7009'),
    'Q1': dict(part='onsemi MMBT3904LT1G', package='SOT-23', qty=1,
               note='Generic 2N3904 Gummel-Poon model. Saturation current swept x0.5 to x2.'),
    'RS': dict(part='two 27.4 ohm 1 % 0.25 W thin-film in parallel', value_ohm=13.7, qty=2,
               note='One open leaves 27.4 ohm: the limit halves and the rail sags into the window trip.'),
    'DZ': dict(part='10 V 5 % small-signal Zener, BZX84-C10 class', qty=1, connects='cathode M2 drain, anode M2 source'),
    'RT': dict(value_ohm=470e3, qty=1, connects='across M2 drain-source'),
    'RG1': dict(value_ohm=100, qty=1, connects='M1 gate to guard output',
                note='10 k let a hard close pass 0.6 A for 4 to 14 us. 100 ohm cuts that to under 0.2 us.'),
    'RB': dict(value_ohm=1e3, qty=1, connects='M2 source to Q1 base'),
    'RLED': dict(value_ohm=240, qty=1, note='10.3 to 17.8 mA over the CB-007 4.07 to 5.48 V drive window.'),
}
REJECTED = {
    'Panasonic AQV259 as the series switch': dict(
        load_V_abs=1000, load_mA_25C=dict(A=30, B=40, C=50), peak_mA_100ms=90,
        Ron_max_ohm=dict(A=200, B=100, C=50), Ron_typ_ohm=dict(A=85, B=60, C=30),
        drop_at_normal_V=dict(A_max=NORMAL_A*200, C_max=NORMAL_A*50),
        leakage_uA_max=10, isolation_Vrms=1500, turn_off_ms_max=.2,
        findings=['No AQV259H exists. The 5000 Vrms H types stop at AQV256H, 600 V.',
                  'Normal 22.72 mA uses 76 % of the 25 C connection-A rating before derating.',
                  'Maker caution "Continual DC bias (AQV259 and AQV258)": a steady input-to-output '
                  'bias can degrade the output breakdown voltage. A high-side B+ switch has that bias.'],
        source='Panasonic ASCTB465E 202601, PhotoMOS HE DIP6 1 Form A',
        sha256='3610ef23d962514fc61e9f8071aad553263668bed7091a2edcb27df5a297ba27'),
    'IXTH12N100L / IXTK22N100L enhancement linear FET': dict(
        VDSS_V=1000, VGS_th_V=[3, 5], SOA_12N100L='200 W: 800 V, 0.25 A, case 60 C (2007 preliminary sheet)',
        finding='Electrically suitable with one photovoltaic driver only at the 5 V threshold limit '
                '(VOC minimum 7.8 V at 25 C). DigiKey Canada snapshot 28 Nov 2026: zero stock, '
                '24 and 29 week lead. Unverified second-hand reading.',
        sha256_12N100L_2007='374c92baa5c142c52e344ff358863ee7a66c2167ac98365e1fe6f11bed3e7595'),
    'IXCP10M45S / IXCY10M45S two-terminal regulator': 'Task statement: 450 V class. Below the 550 V cold case.',
    'Plain self-biased depletion FET with one source resistor': 'See self_bias_only below.',
    'Energise-to-trip gate pull-down on M1': 'A depletion FET stays on when control power is lost.',
}
STOCK = dict(status='Distributor snapshots through web search on 28 Nov 2026. Second-hand and undated. '
                    'Confirm on the distributor page before ordering.',
             IXTP3N100D2='Mouser about 1,100 to 2,048 in two aggregator snapshots; DigiKey zero with 57 week lead.',
             VOM1271T='DigiKey regional pages 94,039 and 103,415; LCSC 3,373; RS 110.',
             NDT3055L='Not checked. Data sheet revised March 2025.',
             IXTH12N100L='DigiKey Canada zero, 30 expected 18 Jan 2027.',
             IXTK22N100L='DigiKey Canada zero, 25 expected 18 Jan 2027.')

# ---------------------------------------------------------------- model
NOM = dict(vp=-3.5, kp1=1.33, rd1=6., cgd1=17e-12, vth2=1.6, kp2=6.1, rd2=.12, cgd2=30e-12,
           rs=13.7, tq=25., is_mult=1., isc=15e-6, voc=8.4, roff=150e3, rg1=100., rb=1e3,
           stack=False, fault=None)
Q3904 = ('NPN(is={is_}f xti=3 eg=1.11 vaf=74.03 bf=416.4 ne=1.259 ise=6.734f ikf=66.78m xtb=1.5 '
         'br=.7371 nc=2 rc=1 cjc=3.638p mjc=.3085 vjc=.75 fc=.5 cje=4.493p mje=.2593 vje=.75 '
         'tr=239.5n tf=301.2p itf=.4 vtf=4 xtf=2 rb=10)')
PV_NVT = .45                            # fourteen-junction stack slope, declared


def corner(**kw):
    c = dict(NOM)
    c.update(kw)
    return c


# Declared corners. Hot: Q1 at 85 C, weak driver, low M2 threshold, M1 drift resistance x2.3.
HOT_LOW = corner(tq=85, is_mult=2, isc=4e-6, voc=6.0, vth2=.76, rs=13.7*1.01, rd1=13.8, vp=-2.5, kp1=.48, rd2=.18)
COLD_HIGH = corner(tq=0, is_mult=.5, isc=40e-6, voc=9.5, vth2=2.1, rs=13.7*.99, rd1=4.5, vp=-4.5, kp1=1.33)


def guard(inp, out, c, led='VLED10 led10 0 1'):
    """Two-terminal guard between inp and out. led10 is 1 with the LED lit."""
    f = c['fault']
    top = 't1b' if c['stack'] else inp
    n = [led, f'RD10 {top} d10 {c["rd1"]}', 'M10 d10 g10 t10 t10 dep10',
         f'.model dep10 NMOS(level=1 vto={c["vp"]} kp={c["kp1"]} lambda=1e-4)',
         'CGS10 g10 t10 1000p', f'CGD10 g10 d10 {c["cgd1"]}', 'CDS10 d10 t10 68p', f'RG10 g10 {out} {c["rg1"]}',
         f'RD20 t10 d20 {c["rd2"]}', 'M20 d20 g20 s20 s20 enh20',
         f'.model enh20 NMOS(level=1 vto={c["vth2"]} kp={c["kp2"]} lambda=.01)',
         'CGS20 g20 s20 315p', f'CGD20 g20 d20 {c["cgd2"]}', 'CDS20 d20 s20 110p',
         'DZ10 s20 t10 z10', '.model z10 D(bv=10 ibv=1m rs=5)', 'RT10 t10 s20 470k',
         f'RS10 s20 {out} {1e-3 if f == "rs_short" else c["rs"]*(2 if f == "rs_one_open" else 1)}',
         f'RB10 s20 b10 {c["rb"]}',
         # VOM1271: short-circuit current, junction stack, integrated turn-off, 10 M test load.
         f'BPV {out} g20 i={c["isc"]}*v(led10)', f'DPV g20 {out} pvstack',
         f'.model pvstack D(is={c["isc"]/np.exp(c["voc"]/PV_NVT)} n={PV_NVT/.025865})',
         'BOFF noff10 0 v=1-v(led10)', f'SOFF g20 {out} noff10 0 swoff10',
         f'.model swoff10 SW(vt=.5 vh=0 ron={c["roff"]} roff=1e12)', f'RPV g20 {out} 10meg']
    if f != 'q_open':
        n += [f'Q10 g20 b10 {out} q3904 temp={c["tq"]}', '.model q3904 '+Q3904.format(is_=6.734*c['is_mult'])]
    if c['stack']:                      # optional second 1000 V device, both gates on the output
        n += [f'RD1B {inp} d1b {c["rd1"]}', 'M1B d1b g1b t1b t1b dep10', 'CGS1B g1b t1b 1000p', 'CDS1B d1b t1b 68p',
              f'CGD1B g1b d1b {c["cgd1"]}', f'RG1B g1b {out} {c["rg1"]}']
        if f == 'm1_short':
            n.append('RFM1 d1b t1b 1m')
    elif f == 'm1_short':
        n.append(f'RFM1 {inp} t10 1m')
    if f in ('m2_short', 'dz_short'):
        n.append('RFM2 t10 s20 1m')
    if f == 'm1_gate_source_short':
        n.append('RFGS g10 t10 1m')
    return '\n'.join(n)+'\n'
