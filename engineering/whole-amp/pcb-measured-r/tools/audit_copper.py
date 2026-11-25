"""Read-only copper geometry inventory; not an ampacity or EMC certificate.

Inputs: authoritative boards/*.kicad_pcb. Output: review/copper-audit.json.
Only exact endpoint joins on one layer are screened for bends. Pad/via/branch
nodes are reported separately; zone geometry and interior intersections need
native DRC and visual review. Never saves a board or its paired project.
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import pcbnew as p

ROOT = Path(__file__).resolve().parents[1]
KEEP = []


def point(v):
    return (v.x, v.y)


def inspect_board(path):
    b = p.LoadBoard(str(path))
    KEEP.append(b)
    nets = defaultdict(lambda: {"segments": 0, "length_mm": 0., "widths_mm": set(), "vias": [], "pad_connections": []})
    # Include wholly unrouted nets: counting only existing tracks concealed
    # current-budget coverage gaps on Main/Power/Control.
    for f in b.GetFootprints():
        for q in f.Pads():
            net = q.GetNetname()
            if net:
                nets[net]['pad_connections'].append({'reference': f.GetReference(), 'pad': q.GetNumber()})
    nodes = defaultdict(list)
    nonline = []
    for t in b.GetTracks():
        row = nets[t.GetNetname()]
        if isinstance(t, p.PCB_VIA):
            row["vias"].append({"at_mm": [p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)], "outer_layer_diameters_mm": {b.GetLayerName(layer): p.ToMM(t.GetWidth(layer)) for layer in [p.F_Cu, p.B_Cu]}, "drill_mm": p.ToMM(t.GetDrillValue())})
            continue
        row["segments"] += 1
        row["length_mm"] += p.ToMM(t.GetLength())
        row["widths_mm"].add(round(p.ToMM(t.GetWidth()), 6))
        if isinstance(t, p.PCB_ARC):
            nonline.append(str(t.m_Uuid.AsString()))
            continue
        a, z = point(t.GetStart()), point(t.GetEnd())
        for here, other in [(a, z), (z, a)]:
            nodes[(t.GetNetname(), t.GetLayer(), here)].append((other[0]-here[0], other[1]-here[1]))
    bends, junctions = [], []
    vias_at = {point(t.GetPosition()) for t in b.GetTracks() if isinstance(t, p.PCB_VIA)}
    for (net, layer, at), vectors in nodes.items():
        if len(vectors) < 2:
            continue
        covered_pad = any(q.GetNetname() == net and q.HitTest(p.VECTOR2I(*at)) for f in b.GetFootprints() for q in f.Pads())
        record = {"net": net, "layer": b.GetLayerName(layer), "at_mm": [p.ToMM(x) for x in at]}
        if len(vectors) != 2 or at in vias_at or covered_pad:
            record.update({"segments": len(vectors), "in_pad": covered_pad, "at_via": at in vias_at})
            turns = []
            for i, u in enumerate(vectors):
                for v in vectors[i+1:]:
                    denom = math.hypot(*u)*math.hypot(*v)
                    if denom:
                        turns.append(round(180-math.degrees(math.acos(max(-1., min(1., (u[0]*v[0]+u[1]*v[1])/denom)))), 3))
            record['pairwise_turns_degrees'] = turns
            record['right_angle_pair_present'] = any(abs(t-90) < .1 for t in turns)
            record['qualified'] = False  # a branch listing is not a passed corner review
            junctions.append(record)
            continue
        u, v = vectors
        denom = math.hypot(*u)*math.hypot(*v)
        if denom == 0:
            record["issue"] = "zero-length segment"
        else:
            turn = 180-math.degrees(math.acos(max(-1., min(1., (u[0]*v[0]+u[1]*v[1])/denom))))
            if turn <= 45.1:
                continue
            record["turn_degrees"] = round(turn, 3)
        bends.append(record)
    for row in nets.values():
        row["widths_mm"] = sorted(row["widths_mm"])
        row["length_mm"] = round(row["length_mm"], 3)
        row['pad_connections'] = sorted(row['pad_connections'], key=lambda x:(x['reference'], x['pad']))
        row['has_routed_copper'] = bool(row['segments'] or row['vias'])
        row['length_scope'] = 'Sum of native tracks/arcs, not a source-to-load path length; zones excluded'
        row["current_qualification"] = "pending per-path current/stackup/thermal evidence"
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "nets": dict(sorted(nets.items())), "simple_bends_over_45_degrees": bends, "junctions_for_visual_review": junctions, "arc_items_not_bend_screened": nonline, "all_corner_review_complete": False}


if __name__ == "__main__":
    result = {"scope": "All pad-connected and routed nets; no connectivity, zone-neck, RMS-current, thermal or EMC qualification", "boards": {}}
    for name in ["Main", "Power", "Control", "Reverb"]:
        result["boards"][name] = inspect_board(ROOT / "boards" / f"Renegade_{name}.kicad_pcb")
    result["fabrication_ready"] = False
    (ROOT / "review/copper-audit.json").write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({name: {"total_nets": len(r["nets"]), "routed_nets": sum(n['has_routed_copper'] for n in r['nets'].values()), "bend_candidates": len(r["simple_bends_over_45_degrees"]), "junctions": len(r["junctions_for_visual_review"])} for name, r in result["boards"].items()}, indent=2))
