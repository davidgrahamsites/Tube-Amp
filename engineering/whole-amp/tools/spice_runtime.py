"""TI OPAx134 manufacturer model; electrical tank surrogate only.
No model of acoustic decay, vibration, cabinet hum, original tube amp or safety.
"""
from pathlib import Path
import ctypes as ct,json,math,hashlib,csv
R=Path(__file__).resolve().parents[1];OUT=R/'simulation'
CHAR=ct.CFUNCTYPE(ct.c_int,ct.c_char_p,ct.c_int,ct.c_void_p)
EXIT=ct.CFUNCTYPE(ct.c_int,ct.c_int,ct.c_bool,ct.c_bool,ct.c_int,ct.c_void_p)
class Complex(ct.Structure):_fields_=[('real',ct.c_double),('imag',ct.c_double)]
class Vector(ct.Structure):_fields_=[('name',ct.c_char_p),('type',ct.c_int),('flags',ct.c_short),('real',ct.POINTER(ct.c_double)),('complex',ct.POINTER(Complex)),('length',ct.c_int)]
logs=[]
@CHAR
def cb(t,i,u):logs.append(t.decode(errors='replace'));return 0
@EXIT
def ex(s,im,q,i,u):logs.append('EXIT '+str(s));return 0
lib=ct.CDLL('/Applications/KiCad/KiCad.app/Contents/Frameworks/libngspice.0.dylib');lib.ngSpice_Init.argtypes=[ct.c_void_p]*7;lib.ngSpice_Init(cb,None,ex,None,None,None,None)
lib.ngSpice_Circ.argtypes=[ct.POINTER(ct.c_char_p)];lib.ngSpice_Command.argtypes=[ct.c_char_p];lib.ngGet_Vec_Info.argtypes=[ct.c_char_p];lib.ngGet_Vec_Info.restype=ct.POINTER(Vector)
for cm in Path('/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/ngspice').glob('*.cm'):
 lib.ngSpice_Command(('codemodel '+str(cm)).encode())
lib.ngSpice_Command(b'set ngbehavior=ps')
def cmd(s):
 v=lib.ngSpice_Command(s.encode());assert v==0,(s,v,logs[-10:])
def vector(n):
 p=lib.ngGet_Vec_Info(n.encode());assert p,(n,logs[-30:]);v=p.contents
 if bool(v.real):return [v.real[i] for i in range(v.length)]
 return [complex(v.complex[i].real,v.complex[i].imag) for i in range(v.length)]

def load(text):
 lines=[s.encode() for s in text.splitlines()]+[None]
 rc=lib.ngSpice_Circ((ct.c_char_p*len(lines))(*lines))
 assert rc==0,(rc,logs[-30:])
