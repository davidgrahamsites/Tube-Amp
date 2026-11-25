# Socket service study task card

Owner: mechanical integration. Inputs: current native board inventory, fit-register trial poses, and the socket module's maximum-body/height interface. Electrical blocks and native component positions remain owned by PCB integration.

Process: rerun check_socket_fit.py and board_fit_cad.py, then socket_fit_cad.py. The latter adds five conservative socket-plus-IC bounding solids and separate vertical service volumes. It tests known-solid intersections, native reopening and STEP round-trip. These are planning bounds, not exact socket cosmetic models or a complete populated chassis.

Done condition: all five current footprints consume the same dimensions; exported geometry and checks agree, collisions and missing populations remain explicit. The existing 467 × 160 × 383 mm rectangular cabinet datum is still an unverified common volume. No fastening to removable wood; drill clearance stays pending. Final three-board placement, thermal clearances, all other parts, wiring and the whole-chassis removal path remain separate work.

Human check: compare exact purchased socket/IC height, retention and puller movement with the editable FreeCAD service volumes, then inspect the entire loaded chassis against the real cabinet before manufacturing.
