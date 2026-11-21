# Continuous-wire schematic redraw

- Owner: root agent; no delegation.
- Input: saved v0.2 native schematic and pin register; user's request for a familiar drawing with wires instead of pin-by-pin net labels.
- Output: same canonical editable project, presentation revision v0.3, fresh PDF and native validation.
- Scope: rearrange symbols and replace intra-sheet labels with continuous orthogonal wiring, explicit junction dots and conventional ground symbols. Keep sheet-interface labels. Preserve circuit pin partitions and intentional no-connects.
- Method: declared positions in `wire-layout.json`; controlled native re-layout in `tools/wire_layout.py`; native KiCad load/export, exact pin-partition comparison to v0.2 plus the register, ERC and rendered page review.
- Preservation: prior layout/native evidence in `validation/label-layout-v0.2.zip`; source baseline, circuit values and original source retained. Native edit hashes guard repeat re-layout.
- Done condition: every revised circuit sheet drawn with continuous wires, native export succeeds, pin partitions unchanged, no new ERC errors, each PDF page reviewed.
- Dependencies and human check: full build-component qualification and original fabrication review boundary remain pending. This presentation task does not change circuit qualification.
- Estimated effort: one sustained redraw and review session, with corrections driven by native/rendered evidence.
