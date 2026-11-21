"""Qualify KiCad's shared ngspice with analytic circuits, not amp models."""
import ctypes as ct
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

LIBRARY = Path('/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib')
OUTPUT = Path(__file__).resolve().parents[1] / 'qualification'
CHAR = ct.CFUNCTYPE(ct.c_int, ct.c_char_p, ct.c_int, ct.c_void_p)
EXIT = ct.CFUNCTYPE(ct.c_int, ct.c_int, ct.c_bool, ct.c_bool, ct.c_int, ct.c_void_p)


class Vector(ct.Structure):
    _fields_ = [('name', ct.c_char_p), ('type', ct.c_int), ('flags', ct.c_short),
                ('real', ct.POINTER(ct.c_double)), ('complex', ct.c_void_p),
                ('length', ct.c_int)]


def main():
    OUTPUT.mkdir(exist_ok=True)
    messages, exits, checks, hashes = [], [], {}, {}

    @CHAR
    def receive(text, ident, user):
        messages.append(text.decode(errors='replace'))
        return 0

    @EXIT
    def controlled_exit(status, immediate, quit_request, ident, user):
        exits.append({'status': status, 'quit': quit_request})
        return 0

    lib = ct.CDLL(str(LIBRARY))
    lib.ngSpice_Init.argtypes = [ct.c_void_p] * 7
    lib.ngSpice_Init.restype = ct.c_int
    lib.ngSpice_Command.argtypes = [ct.c_char_p]
    lib.ngSpice_Command.restype = ct.c_int
    lib.ngSpice_Circ.argtypes = [ct.POINTER(ct.c_char_p)]
    lib.ngSpice_Circ.restype = ct.c_int
    lib.ngGet_Vec_Info.argtypes = [ct.c_char_p]
    lib.ngGet_Vec_Info.restype = ct.POINTER(Vector)

    def command(text):
        code = lib.ngSpice_Command(text.encode())
        if code != 0 or exits:
            raise RuntimeError(f'ngspice command failed: {text}; code={code}; exits={exits}')

    def circuit(name, text):
        data = text.encode()
        (OUTPUT / name).write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
        lines = [line.encode() for line in text.splitlines()] + [None]
        code = lib.ngSpice_Circ((ct.c_char_p * len(lines))(*lines))
        if code != 0 or exits:
            raise RuntimeError(f'Circuit load failed: {name}; code={code}; exits={exits}')

    def vector(name):
        pointer = lib.ngGet_Vec_Info(name.encode())
        if not pointer or not pointer.contents.real or pointer.contents.length < 1:
            raise RuntimeError(f'Missing real vector: {name}')
        values = [pointer.contents.real[i] for i in range(pointer.contents.length)]
        if not all(math.isfinite(value) for value in values):
            raise RuntimeError(f'Nonfinite vector: {name}')
        return values

    result = {'purpose': 'Solver/interface qualification only; not an amplifier simulation',
              'python': sys.executable, 'architecture': platform.machine(),
              'library': str(LIBRARY), 'checks': checks, 'input_sha256': hashes,
              'passed': False}
    try:
        code = lib.ngSpice_Init(receive, None, controlled_exit, None, None, None, None)
        if code != 0:
            raise RuntimeError(f'ngspice initialization failed: {code}')
        command('version')
        circuit('dc-divider.cir', 'Qualification: DC divider\nV1 in 0 5\nR1 in out 1k\nR2 out 0 1k\n.end\n')
        command('op')
        dc = vector('v(out)')[0]
        checks['dc'] = {'actual_v': dc, 'expected_v': 2.5, 'absolute_tolerance_v': 1e-6}
        if abs(dc - 2.5) > 1e-6:
            raise RuntimeError('DC result differs from analytic divider')
        command('destroy all')
        circuit('rc-step.cir', 'Qualification: RC step\nV1 in 0 PULSE(0 5 0 1n 1n 10m 20m)\nR1 in out 1k\nC1 out 0 1u IC=0\n.end\n')
        command('tran 10u 5m uic')
        times, volts = vector('time'), vector('v(out)')
        if len(times) != len(volts) or len(times) < 50:
            raise RuntimeError('Incomplete transient vectors')
        index = min(range(len(times)), key=lambda i: abs(times[i] - 0.001))
        expected = 5 * (1 - math.exp(-times[index] / 0.001))
        checks['rc_one_tau'] = {'time_s': times[index], 'actual_v': volts[index],
                                'expected_v': expected, 'absolute_tolerance_v': 0.01,
                                'samples': len(times)}
        if abs(volts[index] - expected) > 0.01:
            raise RuntimeError('Transient result differs from analytic RC response')
        errors = [m for m in messages if m.lower().startswith('stderr error') or 'fatal error' in m.lower()]
        if errors:
            raise RuntimeError('Solver errors: ' + '; '.join(errors))
        result['passed'] = True
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        result['engine_version_output'] = [m for m in messages if 'ngspice-' in m]
        (OUTPUT / 'ngspice.log').write_text('\n'.join(messages) + '\n')
        (OUTPUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
