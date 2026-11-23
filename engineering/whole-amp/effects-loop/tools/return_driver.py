"""Bounded RETURN headroom experiment; no native circuit mutation.

TI SBOA510 section 2 supply bootstrap with three OPA462 macro-models.
This is a feasibility fixture, not a selected low-cost implementation.
Fetch the unmodified official model with --fetch; run with no arguments.
"""
import hashlib
import io
import json
import re
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from run import OUT, sp, stats

MODEL = Path('/tmp/renegade-opa462-model/OPA462.LIB')
URL = 'https://www.ti.com/lit/zip/SBOMAV9'
SHA = '66a115944b72948befa0c0c03a4d7123a80253c1e706fca587686838b66ea4a8'


def fetch():
    with urllib.request.urlopen(URL, timeout=30) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    name = next(n for n in archive.namelist() if n.upper().endswith('/OPA462.LIB') or n.upper() == 'OPA462.LIB')
    data = archive.read(name)
    assert hashlib.sha256(data).hexdigest() == SHA, 'Manufacturer model changed: review before use'
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    MODEL.write_bytes(data)


def midpoint_initialization(rail):
    """Guide Newton iteration for the hash-pinned floating-supply macro-model.

    Nodesets are initial guesses, not voltage clamps. External OP bounds and
    completed transient evidence remain mandatory. Do not edit the vendor model.
    """
    model = MODEL.read_text().split('.SUBCKT OPA462', 1)[1].split('.ENDS', 1)[0]
    nodes = sorted(set(re.findall(r'\bN[0-9]+\b', model))) + [
        'MID', 'CLAMP', 'CL_CLAMP', 'CLAW_CLAMP', 'VCLP', 'VOUT_S', 'VSENSE']
    guesses = {}
    for unit, vp, vn in [('xup', rail, 0), ('xdn', 0, -rail), ('xmain', rail/2, -rail/2)]:
        for node in nodes:
            guesses[unit+'.'+node] = (vp+vn)/2
        for node, value in [('VCC_B', vp), ('VEE_B', vn),
                            ('N2425309', (3*vp+vn)/4), ('N2425287', (vp+vn)/2),
                            ('N2425325', (vp+3*vn)/4)]:
            guesses[unit+'.'+node] = value
    return '\n'.join(f'.nodeset v({node})={value}' for node, value in guesses.items())


def deck(hz, peak, rail, bootstrap=True):
    power = '''RUP VP UP 100k
RUF UP BUF 100k
RDN VN DN 100k
RDF DN BUF 100k
XUP UP VUP VP 0 VUP OPA462
XDN DN VDN 0 VN VDN OPA462
CB VUP VDN 100n
''' if bootstrap else '''EP VUP 0 VP 0 .5
EN VDN 0 VN 0 .5
CB VUP VDN 100n
'''
    return f'''RETURN headroom experiment, not selected hardware
.include "{MODEL}"
.options method=gear maxord=2 reltol=.001 abstol=1n vntol=10u
.nodeset v(BUF)=0 v(PORT)=0 v(VUP)={rail/2} v(VDN)={-rail/2}
{midpoint_initialization(rail) if bootstrap else ""}
VP VP 0 {rail}
VN VN 0 {-rail}
VS SRC 0 DC 0 AC 1 SIN(0 {peak/100} {hz})
RI SRC INP 1k
RIN INP 0 1meg
RF BUF INV 990k
RG INV 0 10k
XMAIN INP INV VUP VDN BUF OPA462
{power}
RO BUF PORT 1k
RL PORT 0 340k
CL PORT 0 100p
.end
'''


CASES = [(1000, 135.1, 170, False)] + [
    (f, amplitude, supply, True)
    for supply in [166.6, 173.4]
    for f, amplitude in [(82.4, 135.1), (1000, 135.1), (5000, 135.1), (20000, 135.1), (1000, 150)]
]
TIMEOUT_S = 45


def case_key(case):
    return 'return-real-' + '-'.join(str(v) for v in case)


def measure(case):
    hz, peak, rail, boot = case
    key = case_key(case)
    text = deck(hz, peak, rail, boot)
    (OUT/(key+'.cir')).write_text(text)
    start = time.monotonic()
    sp.load(text); sp.cmd('op')
    op = {n:sp.vector('v('+n.lower()+')') for n in ['BUF','PORT','VUP','VDN']}
    assert all(len(v) and np.isfinite(v[-1]) for v in op.values()), 'No finite operating point'
    op = {n:float(v[-1]) for n,v in op.items()}
    assert abs(op['BUF']) < 1 and abs(op['PORT']) < 1, ('Invalid zero-input output', op)
    assert abs(op['VUP']-rail/2) < 1 and abs(op['VDN']+rail/2) < 1, ('Invalid supply midpoint', op)
    sp.cmd('save v(buf) v(port) v(vup) v(vdn) v(inp) vp#branch vn#branch')
    end = max(.03, 30/hz); step = min(2e-6, 1/(hz*192))
    sp.cmd(f'tran {step} {end} {end-20/hz} {step}')
    t = np.array(sp.vector('time'))
    assert len(t) and t[-1] >= end*(1-1e-8), sp.logs[-10:]
    wave = {n:np.array(sp.vector('v('+n+')')) for n in ['BUF','PORT','VUP','VDN','INP']}
    metrics = {n:stats(t,y,hz,end) for n,y in wave.items()}
    settling = abs(stats(t,wave['PORT'],hz,end-10/hz)['fundamental_Vpk']/metrics['PORT']['fundamental_Vpk']-1)
    # Input resistor and 1k output resistor losses are deliberate in the fixture.
    expected = peak * 1e6/1001000 * 340/341
    return dict(hz=hz,requested_output_peak_V=peak,supply_magnitude_V=rail,bootstrap=boot,
        end_s=float(t[-1]),elapsed_s=time.monotonic()-start,op=op,signals=metrics,
        settled_relative_fundamental=settling,
        gain_error_percent=100*(metrics['PORT']['fundamental_Vpk']/expected-1),
        maximum_main_supply_span_V=float(np.max(wave['VUP']-wave['VDN'])),
        minimum_upper_output_margin_V=float(np.min(wave['VUP']-wave['BUF'])),
        minimum_lower_output_margin_V=float(np.min(wave['BUF']-wave['VDN'])),status='completed')


def run_one(index):
    case = CASES[index]
    key = case_key(case)
    result = dict(hz=case[0], requested_output_peak_V=case[1],
                  supply_magnitude_V=case[2], bootstrap=case[3])
    start = time.monotonic()
    try:
        assert hashlib.sha256(MODEL.read_bytes()).hexdigest() == SHA, 'Model checksum mismatch'
        result.update(measure(case))
    except (AssertionError, IndexError, OSError) as error:
        result.update(status='failed', error=str(error), elapsed_s=time.monotonic()-start,
                      final_log=sp.logs[-12:])
    finally:
        (OUT/(key+'.log')).write_text('\n'.join(l.rstrip() for l in sp.logs)+'\n')
        (OUT/(key+'.json')).write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')


def run():
    rows = []
    for i, case in enumerate(CASES):
        key = case_key(case)
        # Each model runs in a separate bounded process; one failed OP cannot corrupt the next.
        try:
            process = subprocess.run([sys.executable, __file__, '--case', str(i)],
                                     timeout=TIMEOUT_S, capture_output=True, text=True)
            if process.returncode:
                row = dict(status='failed', error=process.stderr[-3000:])
            else:
                row = json.loads((OUT/(key+'.json')).read_text())
        except subprocess.TimeoutExpired:
            row = dict(status='timeout', timeout_s=TIMEOUT_S)
        row.update(hz=case[0], requested_output_peak_V=case[1], supply_magnitude_V=case[2], bootstrap=case[3])
        (OUT/(key+'.json')).write_text(json.dumps(row, indent=2, allow_nan=False)+'\n')
        rows.append(row)
        report = dict(model_url=URL, model_sha256=SHA,
            application_note='https://www.ti.com/lit/an/sboa510/sboa510.pdf',
            initialization='Floating macro-model internal nodes seeded near local midpoint; nodesets only, unmodified model. External OP checked.',
            expected_cases=len(CASES), cases=rows, all_requested_cases_attempted=len(rows)==len(CASES),
            native_circuit_changed=False, headroom_qualified=False, fabrication_release=False,
            scope='Unmodified manufacturer model experiment. Fixed-supply comparator then three-amplifier bootstrap. Ideal supplies; not integrated with amp. Failed or timed-out cases are NOT electrical results. Gain/mixing, startup, supply tolerances, protection, component cost/stock and fit remain unqualified.')
        (OUT/'return-real-summary.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
        print(key, row['status'], flush=True)


if __name__ == '__main__':
    if '--fetch' in sys.argv:
        fetch()
    elif '--case' in sys.argv:
        run_one(int(sys.argv[sys.argv.index('--case')+1]))
    else:
        run()
