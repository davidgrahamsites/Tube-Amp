# Native schematic product
Inputs: ../circuit.json, preserved whole-amp integrated sheets and source symbol library.
Process: generated once by ../tools/build_revision.py, then checked by KiCad CLI and pin comparison. Subsequent manual edits must be preserved before regeneration.
Outputs: editable full-amplifier schematic and local library; no PCB manufacturing files.
Human check: inspect send, recovery, output and tank harness sheets and confirm original amp sheets remain unchanged.
