# DIP socket draft correction — 24 November 2026

Owner: component integration. Contract: footprint-contract.json. Factory: tools/build_footprints.py; native application: ../../whole-amp/pcb-measured-r/tools/integrate_socket_footprints.py. Independent verifier: tools/check_footprints.py.

U1/U2 use TE 1-2199298-3 and U10/U11/U12 use TE 1-2199298-2 candidate socket footprints. All52 plated holes change from0.8 to1.0mm; pad centers, numbering, nets and1.6mm copper pads remain unchanged. Pin1 remains roundrect. The rectangular tail maximum0.70×0.22mm has diagonal0.734mm, so a round1mm hole accommodates its cross-section; a rectangular pin does not automatically require a plated slot. Manufacturer revisionA drawing is retained; currentA1 drawing and sample verification remain release gates. Proposed hole/registration tolerances leave0.20mm residual annulus; the fabricator has not accepted these tolerances.

F.Fab represents the maximum socket body; F.CrtYd bounds the larger socket/IC assembly plus0.25mm. C352 moves0.3mm inY to clear U2's expanded courtyard. Four trace endpoints follow it with unchanged0.3mm width and45-degree bends. No other copper changes belong to this checkpoint.

Native netlist and ERC are unchanged. Exported drills prove the52 intended changes and unchanged other plated/nonplated holes and slots. Control retains13 existing DRC findings and79 unconnected items; Reverb remains0/0. Deliberately undersized and mirrored-pin1 checks fail as expected. Native Control/Reverb plots were visually inspected at full board and enlarged socket/bypass scales: socket outlines and pin1 are visible and the C352 overlap is gone. This inspection also exposed the separately tracked U12 square T-junction (FB-119); it is not cleared by this socket check.

All16 IC/tube references remain subject to socket qualification; no exception adopted. Contact tolerance, current drawing, retention, actual fitted sample and full populated assembly remain open. Chinese stock observations in te-candidate-review.md remain dated observations, not a purchase or delivery guarantee. No fabrication release.
