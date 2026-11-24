"""One-time manufacturer-backed correction; run --apply only on pinned baseline."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
MODULE=Path(__file__).resolve().parents[1]
BASE="d0fae8a9c8fa76af2f63d5e79e54405b1211b579"
PATHS=["engineering/whole-amp/reverb-600/circuit.json","engineering/whole-amp/reverb-600/cad/08_control_supply.kicad_sch","engineering/whole-amp/pcb-measured-r/boards/Renegade_Control.kicad_pcb"]
def main():
    assert sys.argv[1:]==["--apply"], "Explicit --apply required; this is a one-time mutation"
    originals={p:(ROOT/p).read_text() for p in PATHS}
    for p,t in originals.items():
        assert t==subprocess.check_output(["git","show",BASE+":"+p],cwd=ROOT).decode(),p+" no longer matches reviewed baseline"
    changes={}
    contract=json.loads(originals[PATHS[0]])
    for c in contract["components"]:
        if c["reference"]=="C212":
            assert c["value"]=="2.2u" and c["pins"]=={"1":"GND","2":"NEG_RAW"}
            c["value"]="47u"
    changes[PATHS[0]]=json.dumps(contract,indent=2)+"\n"
    pattern=r'(\(property\s+"Reference"\s+"C212"[\s\S]*?\(property\s+"Value"\s+)"2.2u"'
    for p in PATHS[1:]:
        new,n=re.subn(pattern,lambda m:m.group(1)+'"47u"',originals[p])
        assert n==1,(p,n)
        restored,n=re.subn(pattern.replace('"2.2u"','"47u"'),lambda m:m.group(1)+'"2.2u"',new)
        assert n==1 and restored==originals[p]
        changes[p]=new
    for p,t in changes.items():(ROOT/p).write_text(t)
    covpath=ROOT/"engineering/component-selection/coverage.json"
    cov=json.loads(covpath.read_text())
    for row in cov:
        if row["id"]=="P127":
            assert row["refs"]==["C212"] and row["value"]=="2.2u"
            row.update(value="47u",requirement="50V aluminium electrolytic; local at U7 input; minimum 22uF following ST L79 section6",selected_mpn="EEUFR1H470",candidate_mpns=["EEUFR1H470"],selection_evidence="../whole-amp/aux-supply/review.md",status="engineering value/MPN selected; native value corrected; 2.5mm part pitch versus 3.5mm provisional native footprint remains a fabrication hold")
    covpath.write_text(json.dumps(cov,indent=2)+"\n")
    record=dict(baseline_commit=BASE,authority="Existing PCB/power repair authorization and FB-115 parts-first constraint",scope="C212 value only in source/native schematic/Control board; P127 engineering selection; no geometry or connectivity change",before_sha256={p:hashlib.sha256(t.encode()).hexdigest() for p,t in originals.items()},after_sha256={p:hashlib.sha256(t.encode()).hexdigest() for p,t in changes.items()},fabrication_ready=False)
    (MODULE/"results/c212-integration.json").write_text(json.dumps(record,indent=2)+"\n")
    print("C212 2.2u -> 47u; native footprint remains explicitly provisional.")
if __name__=="__main__":main()
