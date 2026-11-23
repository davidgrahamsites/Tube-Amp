# Relay diode correction — 22 November 2026

Status: native schematic correction; not complete PCB or fabrication approval.

The connector/PCB review found D332 reversed in `09b_latches_drivers.kicad_sch`. Rotate only that diode from 270 to 90 degrees. Its pin 1 (cathode) now connects to +12V and pin 2 (anode) to COIL_CH, matching the intended relay flyback polarity and candidate PCB. D331 and D341 retain cathodes on +12V and anodes on COIL_CH and COIL_REV respectively.

Before/after native KiCad XML exports were compared. Exactly two pin/net assignments changed: D332.1 COIL_CH → +12V and D332.2 +12V → COIL_CH. Every other exported pin/net assignment was unchanged. Temporary exports: /tmp/renegade-before-d332.xml and /tmp/renegade-after-d332.xml. These are working evidence, not permanent source dependencies; the corrected native schematic is canonical.

Assembly metadata was also aligned: D331 and D332 Main; D341 Reverb. No circuit connectivity was changed by those metadata edits.

Outstanding: complete ERC/presentation review and reconcile native exported GND/PE alias with PCB comparison, preserving the required protective-earth bond. Candidate PCB routing and physical qualification remain incomplete. See the local-loop native review under pcb-measured-r/review for fresh candidate checks; do not equate candidate checks with adoption into active boards.
