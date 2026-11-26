"""Candidate body/lead arithmetic only; no cabinet or electrical-fit approval."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    candidates = [
        (ROOT / "panasonic-contract.json", "body_nominal_L_W_H_mm"),
        (ROOT.parent / "fc6136-fit-contract.json", "body_nominal_W_T_H_mm"),
    ]
    results = []
    for path, body_key in candidates:
        raw = path.read_bytes()
        part = json.loads(raw)
        body = [round(n + t, 3) for n, t in zip(
            part[body_key], part["body_tolerance_plus_minus_mm"])]
        lead_min = (part["lead_length_nominal_mm"]
                    - part["lead_length_tolerance_plus_minus_mm"])
        gap = part.get("recommended_neighbor_spacing_mm", 10)
        # Manufacturer neighbor gap or conditional comparison; never HV spacing.
        arrays = []
        for name, cols, rows, cell in [
            ("two_by_two", 2, 2, body),
            ("short_axis_row", 4, 1, [body[1], body[0], body[2]]),
            ("long_axis_row", 4, 1, body),
        ]:
            a = round(cols * cell[0] + (cols - 1) * gap, 3)
            b = round(rows * cell[1] + (rows - 1) * gap, 3)
            t = round(body[2] + 1.6, 3)
            arrays.append({
                "name": name, "columns": cols, "rows": rows,
                "cell_body_L_W_H_mm": cell,
                "horizontal_body_and_nominal_PCB_extent_mm": [a, b, t],
                "vertical_body_and_nominal_PCB_extent_mm": [a, t, b],
                "local_depth_saved_vertical_mm": round(b - t, 3),
            })
        results.append({
            "mpn": part["mpn"],
            "input_path": str(path.relative_to(ROOT.parent)),
            "input_sha256": hashlib.sha256(raw).hexdigest(),
            "max_body_L_W_H_mm": body,
            "minimum_exposed_lead_mm": lead_min,
            "lead_remaining_below_nominal_1_6_mm_PCB": {
                "body_seated_mm": round(lead_min - 1.6, 3),
                "body_raised_3_mm": round(lead_min - 1.6 - 3, 3),
            },
            "conditional_four_body_2_by_2_extent_mm": [
                round(2 * body[0] + gap, 3),
                round(2 * body[1] + gap, 3),
                body[2],
            ],
            "body_gap_mm": gap,
            "gap_basis": ("manufacturer neighbor recommendation"
                          if "recommended_neighbor_spacing_mm" in part
                          else "comparison assumption only"),
            "upper_PCB_plus_body_height_mm": round(1.6 + body[2], 3),
            "orientation_comparisons": arrays,
        })
    receipt = {
        "status": "conditional packaging arithmetic; neither part adopted",
        "assumptions": {
            "PCB_nominal_thickness_mm": 1.6,
            "trial_body_lift_mm": 3,
            "bank_rows": 2,
            "bank_columns": 2,
        },
        "excluded": [
            "PCB thickness tolerance and required solder protrusion",
            "body-to-pin position tolerances, supports and board margins",
            "connectors, mounting holes, creepage and clearance",
            "lower components, separation and removal/tool envelopes",
            "cabinet, speaker, transformer and thermal fit",
        ],
        "candidates": results,
        "assembly_approved": False,
    }
    out = ROOT / "results/assembly-options.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(out)


if __name__ == "__main__":
    main()
